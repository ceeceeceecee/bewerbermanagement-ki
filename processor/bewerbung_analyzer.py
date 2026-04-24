# BewerbungAnalyzer — KI-gestützte Analyse von Bewerbungen
# PDF-Einlesen mit PyPDF2, Scoring über Ollama

import json
import requests
import io
from pathlib import Path
from typing import Optional

try:
    from PyPDF2 import PdfReader
    PDF_VERFUEGBAR = True
except ImportError:
    PDF_VERFUEGBAR = False


class BewerbungAnalyzer:
    """Analysiert Bewerbungsunterlagen und erstellt ein transparentes Scoring."""

    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama3"):
        self.ollama_url = ollama_url
        self.model = model
        prompt_path = Path(__file__).parent.parent / "prompts" / "bewerbung-scoring.txt"
        self.system_prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""

    def _call_ollama(self, user_message: str) -> str:
        """Sendet eine Anfrage an die Ollama API."""
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
            raise ConnectionError("Ollama-Server nicht erreichbar.")
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama-Anfrage hat das Zeitlimit überschritten.")

    def _extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extrahiert Text aus einer PDF-Datei."""
        if not PDF_VERFUEGBAR:
            raise ImportError("PyPDF2 nicht installiert. Bitte: pip install PyPDF2")
        reader = PdfReader(io.BytesIO(pdf_bytes))
        texte = []
        for seite in reader.pages:
            text = seite.extract_text()
            if text:
                texte.append(text)
        return "\n\n".join(texte)

    def extract_profile(self, lebenslauf_pdf: bytes, anschreiben_pdf: Optional[bytes] = None) -> dict:
        """
        Extrahiert das Bewerberprofil aus PDF-Dokumenten.
        Gibt strukturierte Daten zurück.
        """
        lebenslauf_text = self._extract_text_from_pdf(lebenslauf_pdf)
        anschreiben_text = ""
        if anschreiben_pdf:
            anschreiben_text = self._extract_text_from_pdf(anschreiben_pdf)

        nachricht = f"""Extrahiere das Bewerberprofil aus folgenden Dokumenten:

=== LEBENSLAUF ===
{lebenslauf_text[:4000]}

=== ANSCHREIBEN ===
{anschreiben_text[:2000] if anschreiben_text else "Nicht vorhanden"}

Gib als JSON zurück:
{{
    "name": "...",
    "kontakt": {{"email": "...", "telefon": "..."}},
    "bildung": ["..."],
    "berufserfahrung": ["..."],
    "kenntnisse": ["..."],
    "sprachen": ["..."],
    "zertifikate": ["..."],
    "summary": "Kurze Zusammenfassung des Profils"
}}"""

        antwort = self._call_ollama(nachricht)
        try:
            start = antwort.find("{")
            end = antwort.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(antwort[start:end])
        except json.JSONDecodeError:
            pass

        return {"name": "Unbekannt", "kontakt": {}, "bildung": [], "berufserfahrung": [], "summary": antwort}

    def score_bewerbung(self, lebenslauf_pdf: bytes, stellentext: str, anschreiben_pdf: Optional[bytes] = None) -> dict:
        """
        Bewertet eine Bewerbung anhand der Stellenbeschreibung.
        Gibt Score (0-100), Begründung und Details zurück.

        WICHTIG: Dies ist eine KI-basierte Entscheidungshilfe.
        Die endgültige Entscheidung trifft immer eine menschliche Fachkraft.
        """
        lebenslauf_text = self._extract_text_from_pdf(lebenslauf_pdf)
        anschreiben_text = ""
        if anschreiben_pdf:
            anschreiben_text = self._extract_text_from_pdf(anschreiben_pdf)

        nachricht = f"""Bewerte folgende Bewerbung für die ausgeschriebene Stelle.

=== STELLENBESCHREIBUNG ===
{stellentext[:3000]}

=== LEBENSLAUF ===
{lebenslauf_text[:4000]}

=== ANSCHREIBEN ===
{anschreiben_text[:2000] if anschreiben_text else "Nicht vorhanden"}

Erstelle eine Bewertung. Die Antwort MUSS als JSON zurückgegeben werden:
{{
    "score": 0-100,
    "begruendung": "Detaillierte Begründung der Bewertung",
    "staerken": ["Stärke 1", "Stärke 2", ...],
    "schwaechen": ["Schwäche 1", ...],
    "rueckfragen": ["Offene Frage 1", ...],
    "empfehlung": "Empfehlung als Text",
    "kriterien": {{
        "qualifikation": {{"punktzahl": 0-100, "kommentar": "..."}},
        "berufserfahrung": {{"punktzahl": 0-100, "kommentar": "..."}},
        "motivation": {{"punktzahl": 0-100, "kommentar": "..."}},
        "soft_skills": {{"punktzahl": 0-100, "kommentar": "..."}}
    }}
}}

ERINNERUNG: Du bist eine Entscheidungshilfe. Der Score dient der Unterstützung
der menschlichen Fachkraft, die letztendlich entscheidet."""

        antwort = self._call_ollama(nachricht)
        try:
            start = antwort.find("{")
            end = antwort.rfind("}") + 1
            if start >= 0 and end > start:
                ergebnis = json.loads(antwort[start:end])
                # Score sicher in den Bereich 0-100 bringen
                ergebnis["score"] = max(0, min(100, int(ergebnis.get("score", 0))))
                return ergebnis
        except json.JSONDecodeError:
            pass

        return {
            "score": 0,
            "begruendung": "KI-Analyse konnte nicht durchgeführt werden.",
            "staerken": [],
            "schwaechen": [],
            "rueckfragen": [],
            "empfehlung": "Manuelle Prüfung erforderlich",
        }

    def extract_highlights(self, lebenslauf_pdf: bytes) -> list:
        """Extrahiert die wichtigsten Highlights aus einem Lebenslauf."""
        text = self._extract_text_from_pdf(lebenslauf_pdf)
        nachricht = f"""Liste die 5 wichtigsten Highlights aus diesem Lebenslauf auf:

---
{text[:3000]}
---

Gib als JSON zurück: {{"highlights": ["Highlight 1", "Highlight 2", ...]}}"""

        antwort = self._call_ollama(nachricht)
        try:
            start = antwort.find("{")
            end = antwort.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(antwort[start:end]).get("highlights", [])
        except json.JSONDecodeError:
            pass
        return []

    def flag_concerns(self, lebenslauf_pdf: bytes, stellentext: str) -> list:
        """
        Identifiziert mögliche Bedenken bei einer Bewerbung.
        Hilft der Fachkraft, gezielt nachzufragen.
        """
        text = self._extract_text_from_pdf(lebenslauf_pdf)
        nachricht = f"""Identifiziere mögliche Bedenken bei dieser Bewerbung
im Hinblick auf die folgende Stelle:

=== STELLE ===
{stellentext[:2000]}

=== LEBENSLAUF ===
{text[:3000]}

Gib als JSON zurück:
{{"bedenken": [{{"thema": "...", "beschreibung": "...", "prioritaet": "hoch/mittel/gering"}}]}}"""

        antwort = self._call_ollama(nachricht)
        try:
            start = antwort.find("{")
            end = antwort.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(antwort[start:end]).get("bedenken", [])
        except json.JSONDecodeError:
            pass
        return []
