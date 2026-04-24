# AusschreibungOptimizer — KI-gestützte Optimierung von Stellenausschreibungen
# Verwendet Ollama HTTP API (lokal, DSGVO-konform)

import json
import requests
from pathlib import Path


class AusschreibungOptimizer:
    """Optimiert Stellenausschreibungen mit Hilfe lokaler KI (Ollama)."""

    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama3"):
        self.ollama_url = ollama_url
        self.model = model
        # System-Prompt laden
        prompt_path = Path(__file__).parent.parent / "prompts" / "ausschreibung-optimierung.txt"
        self.system_prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""

    def _call_ollama(self, user_message: str) -> str:
        """Sendet eine Anfrage an die Ollama API und gibt die Antwort zurück."""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    "stream": False,
                },
                timeout=120,
            )
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Ollama-Server nicht erreichbar. Bitte stellen Sie sicher, dass Ollama läuft (localhost:11434).")
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama-Anfrage hat das Zeitlimit überschritten.")

    def optimize_text(self, ausschreibungstext: str) -> dict:
        """
        Modernisiert einen Ausschreibungstext.
        Gibt optimierten Text und Änderungen zurück.
        """
        nachricht = f"""Bitte optimiere folgende Stellenausschreibung:

---
{ausschreibungstext}
---

Gib das Ergebnis als JSON zurück:
{{"optimierter_text": "...", "aenderungen": ["..."], "hinweise": ["..."]}}"""

        antwort = self._call_ollama(nachricht)

        # JSON aus der Antwort extrahieren
        try:
            # Finde JSON-Block in der Antwort
            start = antwort.find("{")
            end = antwort.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(antwort[start:end])
        except json.JSONDecodeError:
            pass

        return {"optimierter_text": antwort, "aenderungen": [], "hinweise": ["KI-Antwort konnte nicht als JSON geparst werden."]}

    def add_benefits(self, ausschreibungstext: str, vorhandene_benefits: list = None) -> dict:
        """
        Schlägt zusätzliche Benefits für die Ausschreibung vor.
        Berücksichtigt bereits vorhandene Benefits.
        """
        benefits_str = ", ".join(vorhandene_benefits) if vorhandene_benefits else "Keine angegeben"
        nachricht = f"""Basiierend auf folgender Ausschreibung:

---
{ausschreibungstext}
---

Vorhandene Benefits: {benefits_str}

Schlage 5-8 passende Benefits für eine Behörde vor. Gib als JSON zurück:
{{"vorgeschlagene_benefits": ["...", "..."], "begruendung": "..."}}"""

        antwort = self._call_ollama(nachricht)
        try:
            start = antwort.find("{")
            end = antwort.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(antwort[start:end])
        except json.JSONDecodeError:
            pass

        return {"vorgeschlagene_benefits": [], "begruendung": antwort}

    def check_diskriminierung(self, text: str) -> dict:
        """
        Prüft einen Text auf mögliche AGG-Diskriminierung.
        Gibt Funde und Alternativvorschläge zurück.
        """
        nachricht = f"""Prüfe folgenden Text auf mögliche Diskriminierung gemäß dem
Allgemeinen Gleichbehandlungsgesetz (AGG). Prüfe auf:
- Altersdiskriminierung (z.B. 'jung', 'dynamisch')
- Geschlechterdiskriminierung
- Ethnische Diskriminierung
- Diskriminierung wegen Behinderung
- Diskriminierung wegen Religion/Weltanschauung
- Sexuelle Identität

Text:
---
{text}
---

Gib als JSON zurück:
{{"probleme": [{{"fund": "...", "art": "...", "alternative": "..."}}], "gesamt_bewertung": "konform/nachbesserungsbedarf", "hinweise": ["..."]}}"""

        antwort = self._call_ollama(nachricht)
        try:
            start = antwort.find("{")
            end = antwort.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(antwort[start:end])
        except json.JSONDecodeError:
            pass

        return {"probleme": [], "gesamt_bewertung": "prüfung_fehlgeschlagen", "hinweise": [antwort]}

    def generate_summary(self, ausschreibungstext: str, max_laenge: int = 200) -> str:
        """Erstellt eine Kurzzusammenfassung der Ausschreibung."""
        nachricht = f"""Fasse folgende Stellenausschreibung in maximal {max_laenge} Wörtern zusammen.
Die Zusammenfassung soll für einen schnellen Überblick geeignet sein:

---
{ausschreibungstext}
---

Gib nur die Zusammenfassung zurück, keinen zusätzlichen Text."""

        return self._call_ollama(nachricht).strip()
