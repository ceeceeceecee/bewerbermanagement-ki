# Bewerbermanagement-KI – Moderne HR-Lösung für Behörden

![DSGVO-konform](https://img.shields.io/badge/DSGVO-konform-brightgreen)
![AGG-konform](https://img.shields.io/badge/AGG-konform-brightgreen)
![Self-Hosted](https://img.shields.io/badge/Self--Hosted-blue)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB)

## 🎯 Problem

Deutsche Behörden stehen vor massiven Herausforderungen im Personalrecruiting:

- **Fachkräftemangel** — Offene Stellen bleiben monatelang unbesetzt
- **Veraltete Ausschreibungen** — Unattraktive Formulierungen schrecken Bewerber ab
- **Langsame Prozesse** — Manuelle Sichtung hundrierender Bewerbungen
- **DSGVO-Hürden** — Unsicherheit bei der Verarbeitung sensibler Bewerberdaten
- **AGG-Risiken** — Diskriminierungsfallen in Ausschreibungstexten

## ✅ Features

- 🤖 **KI-gestützte Ausschreibungsoptimierung** — Modernisierung mit AGG-Check
- 📊 **Transparentes Bewerber-Scoring** — KI bewertet, Mensch entscheidet
- 📄 **PDF-Analyse** — Automatische Extraktion aus Lebenslauf & Anschreiben
- 📧 **Automatisierte Kommunikation** — Eingangsbestätigung, Einladungen, Absagen
- 📅 **Terminmanagement** — Vorstellungsgespräche organisieren
- 📈 **Statistiken & Reporting** — Bewerbungszahlen, Time-to-Hire, Quellen
- 🔒 **DSGVO-konform** — Self-Hosted, Löschkonzept, Audit-Log
- ⚖️ **AGG-konform** — KI als Entscheidungshilfe, keine automatischen Entscheidungen
- 🐳 **Ein-Kommando-Install** — Docker Compose macht alles

## 🚀 Schnellstart

```bash
git clone https://github.com/ceeceeceecee/bewerbermanagement-ki.git
cd bewerbermanagement-ki
cp config/settings.example.yaml config/settings.yaml
docker compose up -d
```

Anschließend: **http://localhost:8501**

## 📁 Projektstruktur

```
bewerbermanagement-ki/
├── app.py                          # Streamlit Web-App
├── processor/
│   ├── ausschreibung_optimizer.py  # KI-Ausschreibungsoptimierung
│   ├── bewerbung_analyzer.py       # KI-Bewerbungsanalyse & Scoring
│   └── kommunikation.py            # E-Mail-Kommunikation
├── database/
│   ├── schema.sql                  # PostgreSQL-Schema
│   └── db_manager.py              # Datenbank-Zugriff
├── prompts/                        # Ollama-System-Prompts
├── email_templates/                # HTML-E-Mail-Vorlagen
├── config/                         # Konfiguration (Platzhalter)
├── docs/                           # DSGVO, Setup, AGG
├── scripts/                        # Setup & Demo-Daten
└── docker-compose.yml
```

## 🤖 KI-Backend

**Standard: Ollama (lokal, DSGVO-konform)**
- Alle KI-Funktionen laufen lokal über Ollama
- Keine Daten verlassen den Server
- Empfohlenes Modell: `llama3` oder `mistral`

**Optional: Claude API (Cloud-Fallback)**
- Kann als Alternative konfiguriert werden
- ⚠️ DSGVO-Vorabklärung erforderlich!

## ⚖️ AGG-Konformität

Dieses System ist als **Entscheidungshilfe** konzipiert:

> Die KI liefert Bewertungen und Empfehlungen. Die **letzte Entscheidung** liegt immer bei einer menschlichen Fachkraft. Automatisierte Entscheidungen im Sinne des § 15 Abs. 1 AGG werden nicht getroffen.

## 📄 Lizenz

MIT License — siehe [LICENSE](LICENSE)
