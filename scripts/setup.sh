#!/bin/bash
# ============================================================
# Bewerbermanagement-KI — Setup-Script
# Initialisiert Datenbank, erstellt Demo-Daten
# ============================================================

set -e

echo "=========================================="
echo "  Bewerbermanagement-KI — Setup"
echo "=========================================="

# Farben
GRUEN='\033[0;32m'
GELB='\033[1;33m'
ROT='\033[0;31m'
NC='\033[0m'

# Prüfe ob Docker installiert
if ! command -v docker &> /dev/null; then
    echo -e "${ROT}Fehler: Docker ist nicht installiert.${NC}"
    echo "Bitte installieren Sie Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker compose &> /dev/null && ! docker-compose --version &> /dev/null; then
    echo -e "${ROT}Fehler: Docker Compose ist nicht installiert.${NC}"
    exit 1
fi

# Konfiguration erstellen
if [ ! -f config/settings.yaml ]; then
    echo -e "${GELB}Konfiguration wird erstellt...${NC}"
    cp config/settings.example.yaml config/settings.yaml
    echo -e "${GRUEN}config/settings.yaml erstellt. Bitte anpassen!${NC}"
else
    echo -e "${GRUEN}Konfiguration bereits vorhanden.${NC}"
fi

if [ ! -f config/bewertungskriterien.yaml ]; then
    cp config/bewertungskriterien.example.yaml config/bewertungskriterien.yaml
    echo -e "${GRUEN}config/bewertungskriterien.yaml erstellt.${NC}"
fi

# Upload-Verzeichnis erstellen
mkdir -p uploads

# Docker-Container starten
echo -e "${GELB}Docker-Container werden gestartet...${NC}"
docker compose up -d

# Warte auf Datenbank
echo -e "${GELB}Warte auf Datenbank...${NC}"
sleep 10

# Demo-Daten einfügen
echo -e "${GELB}Demo-Daten werden eingefügt...${NC}"
docker compose exec -T db psql -U bewerberki -d bewerbermanagement << 'SQL'
-- Demo-Stellen
INSERT INTO stellen (referenz, titel, abteilung, beschreibung, status) VALUES
('BA-2024-001', 'Fachangestellte/r für Bürgerdienste (m/w/d)', 'Bürgeramt',
 'Wir suchen engagierte Fachkräfte für die Betreuung unserer Bürgerinnen und Bürger.', 'offen'),
('IT-2024-003', 'IT-Systemadministrator (m/w/d)', 'IT-Abteilung',
 'Verwaltung und Betrieb unserer IT-Infrastruktur. Linux- und Netzwerkkenntnisse erforderlich.', 'offen'),
('AV-2024-005', 'Verwaltungsfachangestellte/r (m/w/d)', 'Allgemeine Verwaltung',
 'Allgemeine verwaltende Tätigkeiten in der Stadtverwaltung.', 'besetzt')
ON CONFLICT (referenz) DO NOTHING;

-- Demo-Bewerber
INSERT INTO bewerber (vorname, nachname, email, telefon, einwilligung_datenschutz) VALUES
('Anna', 'Müller', 'anna.mueller@example.com', '+49 123 456789', true),
('Thomas', 'Schmidt', 'thomas.schmidt@example.com', '+49 123 456790', true),
('Lisa', 'Weber', 'lisa.weber@example.com', '+49 123 456791', true),
('Markus', 'Fischer', 'markus.fischer@example.com', '+49 123 456792', true)
ON CONFLICT DO NOTHING;

-- Demo-Bewerbungen
INSERT INTO bewerbungen (bewerber_id, stellen_id, status, quelle, eingangsdatum) VALUES
(1, 1, 'neu', 'interamt.de', '2024-01-20'),
(2, 1, 'neu', 'direktbewerbung', '2024-01-22'),
(3, 2, 'eingeladen', 'LinkedIn', '2024-02-05'),
(4, 2, 'abgelehnt', 'interamt.de', '2024-02-08')
ON CONFLICT DO NOTHING;

-- Demo-Scoring
INSERT INTO scoring_details (bewerbung_id, score, begruendung, staerken, empfehlung, ki_modell) VALUES
(1, 82, 'Sehr passende Qualifikation mit Berufserfahrung im Bürgerdienst.',
 '["Relevante Ausbildung", "Berufserfahrung", "Zertifikat"]',
 'Einladung empfohlen', 'ollama-llama3'),
(2, 65, 'Grundsätzlich passend, jedoch keine Erfahrung im öffentlichen Dienst.',
 '["Gute Allgemeinbildung", "IT-Grundkenntnisse"]',
 'Weiter in der Auswahl', 'ollama-llama3'),
(3, 91, 'Hervorragende Qualifikation. Informatikstudium mit Zertifizierungen.',
 '["Informatikstudium", "RHCSA Zertifizierung", "Cloud-Erfahrung"]',
 'Dringend einladen — Top-Kandidat', 'ollama-llama3'),
(4, 38, 'Qualifikationsprofil passt nur teilweise zur Stelle.',
 '["Gute Kommunikation"]',
 'Nicht passend', 'ollama-llama3')
ON CONFLICT DO NOTHING;

SQL

echo ""
echo -e "${GRUEN}=========================================="
echo "  Setup abgeschlossen!"
echo "==========================================${NC}"
echo ""
echo "  Anwendung: http://localhost:8501"
echo "  Datenbank: localhost:5432"
echo "  Redis:     localhost:6379"
echo ""
echo -e "${GELB}Hinweis: Konfigurieren Sie config/settings.yaml${NC}"
echo -e "${GELB}und stellen Sie sicher, dass Ollama läuft.${NC}"
