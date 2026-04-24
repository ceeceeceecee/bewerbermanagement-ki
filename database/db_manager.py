# DatabaseManager — Datenbank-Zugriff für Bewerbermanagement
# PostgreSQL mit psycopg2

import os
import json
from datetime import datetime, date
from typing import Optional, List, Dict, Any


class DatabaseManager:
    """Verwaltet alle Datenbankoperationen für das Bewerbermanagement."""

    def __init__(self, connection_string: Optional[str] = None):
        """Initialisiert die Datenbankverbindung."""
        self.conn_string = connection_string or os.environ.get(
            "DATABASE_URL",
            "postgresql://bewerberki:bewerberki@localhost:5432/bewerbermanagement"
        )
        self._conn = None

    def _get_connection(self):
        """Gibt eine Datenbankverbindung zurück (Lazy Loading)."""
        if self._conn is None or self._conn.closed:
            import psycopg2
            self._conn = psycopg2.connect(self.conn_string)
            self._conn.autocommit = False
        return self._conn

    def close(self):
        """Schließt die Datenbankverbindung."""
        if self._conn and not self._conn.closed:
            self._conn.close()

    def init_schema(self, schema_path: str = None):
        """Initialisiert das Datenbankschema."""
        if schema_path is None:
            from pathlib import Path
            schema_path = Path(__file__).parent / "schema.sql"

        with open(schema_path, "r", encoding="utf-8") as f:
            sql = f.read()

        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()

    # ─── Stellen CRUD ────────────────────────────────────────────────

    def create_stelle(self, referenz: str, titel: str, abteilung: str,
                       beschreibung: str = "", status: str = "entwurf") -> int:
        """Erstellt eine neue Stellenausschreibung."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO stellen (referenz, titel, abteilung, beschreibung, status)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (referenz, titel, abteilung, beschreibung, status))
        stelle_id = cur.fetchone()[0]
        conn.commit()
        self._audit_log("stellen", stelle_id, "CREATE", details=f"Neue Stelle: {titel}")
        cur.close()
        return stelle_id

    def get_stellen(self, status: Optional[str] = None) -> List[Dict]:
        """Gibt alle Stellen zurück, optional gefiltert nach Status."""
        conn = self._get_connection()
        cur = conn.cursor()
        if status:
            cur.execute("SELECT * FROM stellen WHERE status = %s ORDER BY created_at DESC", (status,))
        else:
            cur.execute("SELECT * FROM stellen ORDER BY created_at DESC")
        spalten = [desc[0] for desc in cur.description]
        ergebnisse = [dict(zip(spalten, row)) for row in cur.fetchall()]
        cur.close()
        return ergebnisse

    def update_stelle(self, stelle_id: int, **felder) -> bool:
        """Aktualisiert eine Stellenausschreibung."""
        if not felder:
            return False
        felder["updated_at"] = datetime.now()
        set_clause = ", ".join(f"{k} = %s" for k in felder)
        werte = list(felder.values()) + [stelle_id]
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(f"UPDATE stellen SET {set_clause} WHERE id = %s", werte)
        conn.commit()
        self._audit_log("stellen", stelle_id, "UPDATE", details=str(felder))
        cur.close()
        return cur.rowcount > 0

    # ─── Bewerber CRUD ──────────────────────────────────────────────

    def create_bewerber(self, vorname: str, nachname: str, email: str,
                         einwilligung: bool = False) -> int:
        """Erstellt einen neuen Bewerber-Datensatz."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bewerber (vorname, nachname, email, einwilligung_datenschutz)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (vorname, nachname, email, einwilligung))
        bewerber_id = cur.fetchone()[0]
        conn.commit()
        self._audit_log("bewerber", bewerber_id, "CREATE",
                        details=f"Neuer Bewerber: {vorname} {nachname}")
        cur.close()
        return bewerber_id

    def get_bewerber(self, bewerber_id: int) -> Optional[Dict]:
        """Gibt einen Bewerber anhand der ID zurück."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM bewerber WHERE id = %s", (bewerber_id,))
        if cur.rowcount == 0:
            cur.close()
            return None
        spalten = [desc[0] for desc in cur.description]
        ergebnis = dict(zip(spalten, cur.fetchone()))
        cur.close()
        return ergebnis

    # ─── Bewerbungen CRUD ───────────────────────────────────────────

    def create_bewerbung(self, bewerber_id: int, stellen_id: int,
                          quelle: str = "direkt") -> int:
        """Erstellt eine neue Bewerbung."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bewerbungen (bewerber_id, stellen_id, quelle, eingangsdatum)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (bewerber_id, stellen_id, quelle, date.today()))
        bewerbung_id = cur.fetchone()[0]
        conn.commit()
        self._audit_log("bewerbungen", bewerbung_id, "CREATE")
        cur.close()
        return bewerbung_id

    def get_bewerbungen(self, stellen_id: Optional[int] = None,
                         status: Optional[str] = None) -> List[Dict]:
        """Gibt Bewerbungen zurück, optional gefiltert."""
        conn = self._get_connection()
        cur = conn.cursor()
        sql = """
            SELECT b.*, bw.vorname, bw.nachname, bw.email,
                   s.titel as stelle_titel, s.referenz as stelle_referenz
            FROM bewerbungen b
            JOIN bewerber bw ON b.bewerber_id = bw.id
            JOIN stellen s ON b.stellen_id = s.id
            WHERE 1=1
        """
        params = []
        if stellen_id:
            sql += " AND b.stellen_id = %s"
            params.append(stellen_id)
        if status:
            sql += " AND b.status = %s"
            params.append(status)
        sql += " ORDER BY b.eingangsdatum DESC"

        cur.execute(sql, params)
        spalten = [desc[0] for desc in cur.description]
        ergebnisse = [dict(zip(spalten, row)) for row in cur.fetchall()]
        cur.close()
        return ergebnisse

    # ─── Scoring ────────────────────────────────────────────────────

    def save_scoring(self, bewerbung_id: int, score: int, begruendung: str,
                      staerken: list, schwaechen: list, rueckfragen: list,
                      empfehlung: str, kriterien: dict, ki_modell: str = "ollama"):
        """Speichert die KI-Bewertung zu einer Bewerbung."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO scoring_details
            (bewerbung_id, score, begruendung, staerken, schwaechen,
             rueckfragen, empfehlung, kriterien, ki_modell)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (bewerbung_id, score, begruendung, json.dumps(staerken),
              json.dumps(schwaechen), json.dumps(rueckfragen), empfehlung,
              json.dumps(kriterien), ki_modell))
        conn.commit()
        self._audit_log("scoring_details", bewerbung_id, "CREATE",
                        details=f"Score: {score}, Modell: {ki_modell}")
        cur.close()

    # ─── Termine ────────────────────────────────────────────────────

    def create_termin(self, bewerber_id: int, stellen_id: int, typ: str,
                       datum: date, uhrzeit: str, ort: str) -> int:
        """Erstellt einen neuen Termin."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO termine (bewerber_id, stellen_id, typ, datum, uhrzeit, ort)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """, (bewerber_id, stellen_id, typ, datum, uhrzeit, ort))
        termin_id = cur.fetchone()[0]
        conn.commit()
        self._audit_log("termine", termin_id, "CREATE", details=f"Termin: {typ} am {datum}")
        cur.close()
        return termin_id

    # ─── DSGVO-Löschfunktion ────────────────────────────────────────

    def dsgvo_loeschen(self) -> Dict[str, int]:
        """
        Löscht alle Datensätze, deren Löschdatum erreicht ist.
        DSGVO-konforme automatische Bereinigung.
        """
        conn = self._get_connection()
        cur = conn.cursor()

        # Bewerber mit abgelaufenem Löschdatum finden und löschen
        # (CASCADE löscht automatisch verknüpfte Bewerbungen, Termine, etc.)
        heute = date.today()
        cur.execute("SELECT COUNT(*) FROM bewerber WHERE loeschdatum IS NOT NULL AND loeschdatum <= %s", (heute,))
        anzahl = cur.fetchone()[0]

        if anzahl > 0:
            cur.execute("""
                DELETE FROM bewerber
                WHERE loeschdatum IS NOT NULL AND loeschdatum <= %s
                RETURNING id, vorname, nachname
            """, (heute,))
            geloescht = cur.fetchall()
            for row in geloescht:
                self._audit_log("bewerber", row[0], "DELETE",
                                details=f"DSGVO-Löschung: {row[1]} {row[2]}")
            conn.commit()

        cur.close()
        return {"geloeschte_bewerber": anzahl, "datum": str(heute)}

    # ─── Audit-Log ──────────────────────────────────────────────────

    def _audit_log(self, tabelle: str, datensatz_id: int, aktion: str,
                    details: str = "", benutzer: str = "system"):
        """Schreibt einen Eintrag in das Audit-Log."""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO audit_log (tabelle, datensatz_id, aktion, benutzer, details)
            VALUES (%s, %s, %s, %s, %s)
        """, (tabelle, datensatz_id, aktion, benutzer, details))
        conn.commit()
        cur.close()
