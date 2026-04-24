# KommunikationsManager — E-Mail-Kommunikation mit Bewerbern
# KI-Personalisierung via Ollama

import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional
from jinja2 import Environment, FileSystemLoader


class KommunikationsManager:
    """Verwaltet die E-Mail-Kommunikation mit Bewerbern."""

    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama3",
                 smtp_config: Optional[dict] = None):
        self.ollama_url = ollama_url
        self.model = model
        self.smtp_config = smtp_config or {}

        # Jinja2 Template-Loader
        template_dir = Path(__file__).parent.parent / "email_templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True,
        )

        # System-Prompt laden
        prompt_path = Path(__file__).parent.parent / "prompts" / "kommunikation-vorlagen.txt"
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
                timeout=60,
            )
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return ""

    def _render_template(self, template_name: str, variablen: dict) -> str:
        """Rendert ein HTML-E-Mail-Template mit Jinja2."""
        try:
            template = self.env.get_template(template_name)
            return template.render(**variablen)
        except Exception as e:
            return f"Fehler beim Rendern des Templates: {e}"

    def _personalisieren(self, basis_text: str, kontext: dict) -> str:
        """Personalisiert einen Text mit Hilfe der KI."""
        nachricht = f"""Personalisiere folgende E-Mail für den Bewerber:

Kontext:
- Name: {kontext.get('name', 'Unbekannt')}
- Stelle: {kontext.get('stelle', 'Unbekannt')}
- Besonderheiten: {kontext.get('besonderheiten', 'Keine')}

Original-Text:
---
{basis_text}
---

Gib den personalisierten Text zurück. Behalte den professionellen Ton einer Behörde bei."""

        return self._call_ollama(nachricht) or basis_text

    def send_eingangsbestaetigung(self, name: str, email: str, stelle: str,
                                    eingangsdatum: str = None) -> dict:
        """
        Sendet eine Eingangsbestätigung an den Bewerber.
        """
        if eingangsdatum is None:
            eingangsdatum = datetime.now().strftime("%d.%m.%Y")

        variablen = {
            "name": name,
            "stelle": stelle,
            "eingangsdatum": eingangsdatum,
            "behoerde": self.smtp_config.get("behoerde_name", "Ihre Behörde"),
        }

        html = self._render_template("eingangsbestaetigung.html", variablen)
        betreff = f"Eingangsbestätigung Ihrer Bewerbung — {stelle}"

        return self._send_email(email, betreff, html, {
            "typ": "eingangsbestaetigung",
            "bewerber": name,
            "stelle": stelle,
        })

    def send_terminvorschlag(self, name: str, email: str, stelle: str,
                              datum: str, uhrzeit: str, ort: str) -> dict:
        """
        Sendet eine Einladung zum Vorstellungsgespräch.
        """
        variablen = {
            "name": name,
            "stelle": stelle,
            "datum": datum,
            "uhrzeit": uhrzeit,
            "ort": ort,
            "behoerde": self.smtp_config.get("behoerde_name", "Ihre Behörde"),
        }

        html = self._render_template("termineinladung.html", variablen)
        betreff = f"Einladung zum Vorstellungsgespräch — {stelle}"

        return self._send_email(email, betreff, html, {
            "typ": "termineinladung",
            "bewerber": name,
            "stelle": stelle,
        })

    def send_absage(self, name: str, email: str, stelle: str,
                     grund: str = "") -> dict:
        """
        Sendet eine wertschätzende Absage.
        """
        variablen = {
            "name": name,
            "stelle": stelle,
            "grund": grund,
            "behoerde": self.smtp_config.get("behoerde_name", "Ihre Behörde"),
        }

        html = self._render_template("absage.html", variablen)
        betreff = f"Information zu Ihrer Bewerbung — {stelle}"

        return self._send_email(email, betreff, html, {
            "typ": "absage",
            "bewerber": name,
            "stelle": stelle,
        })

    def send_zusage(self, name: str, email: str, stelle: str,
                     startdatum: str = "") -> dict:
        """
        Sendet eine Zusage an den Bewerber.
        """
        variablen = {
            "name": name,
            "stelle": stelle,
            "startdatum": startdatum,
            "behoerde": self.smtp_config.get("behoerde_name", "Ihre Behörde"),
        }

        html_content = f"""
        <html><body>
        <h2>Herzlichen Glückwunsch, {name}!</h2>
        <p>Wir freuen uns, Ihnen mitteilen zu können, dass wir Sie für die Stelle
        <strong>{stelle}</strong> ausgewählt haben.</p>
        {"<p>Ihr voraussichtlicher Starttermin ist der " + startdatum + ".</p>" if startdatum else ""}
        <p>Wir werden uns in Kürze mit weiteren Details bei Ihnen melden.</p>
        <p>Mit freundlichen Grüßen,<br>{variablen['behoerde']}</p>
        </body></html>
        """

        betreff = f"Zusage — {stelle}"

        return self._send_email(email, betreff, html_content, {
            "typ": "zusage",
            "bewerber": name,
            "stelle": stelle,
        })

    def _send_email(self, empfaenger: str, betreff: str, html: str,
                    metadaten: dict = None) -> dict:
        """
        Sendet eine E-Mail (Platzhalter-Implementierung).
        In Produktion: SMTP-Versand via smtplib.
        """
        # Platzhalter — in Produktion hier SMTP implementieren
        return {
            "status": "vorbereitet",
            "empfaenger": empfaenger,
            "betreff": betreff,
            "html_vorschau": html[:500] + "...",
            "metadaten": metadaten,
            "hinweis": "E-Mail wurde vorbereitet. SMTP-Versand muss konfiguriert werden.",
        }
