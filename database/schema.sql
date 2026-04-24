-- ============================================================
-- Bewerbermanagement-KI — Datenbankschema (PostgreSQL)
-- ============================================================
-- DSGVO-Konform: Löschfristen als Kommentar hinterlegt
-- Besonders schützenswerte Daten: Bewerberdaten (Art. 9 DSGVO)
-- ============================================================

-- Tabellen für Stellenausschreibungen
CREATE TABLE IF NOT EXISTS stellen (
    id SERIAL PRIMARY KEY,
    referenz VARCHAR(50) UNIQUE NOT NULL,
    titel VARCHAR(500) NOT NULL,
    abteilung VARCHAR(200),
    beschreibung TEXT,
    angebot TEXT,
    anforderungsprofil TEXT,
    status VARCHAR(50) DEFAULT 'entwurf',  -- entwurf, offen, in_bearbeitung, besetzt, geschlossen
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(200)
);

-- Bewerber-Stammdaten (besonders schützenswert!)
-- DSGVO-Löschfrist: 6 Monate nach Abschluss des Bewerbungsverfahrens
CREATE TABLE IF NOT EXISTS bewerber (
    id SERIAL PRIMARY KEY,
    vorname VARCHAR(200) NOT NULL,
    nachname VARCHAR(200) NOT NULL,
    email VARCHAR(500),
    telefon VARCHAR(100),
    strasse VARCHAR(500),
    plz VARCHAR(10),
    ort VARCHAR(200),
    geburtsdatum DATE,                    -- Sensibel! Nur bei Einwilligung
    geschlecht VARCHAR(20),               -- Sensibel! Nur bei Einwilligung
    einwilligung_datenschutz BOOLEAN DEFAULT FALSE,
    einwilligung_datum TIMESTAMP,
    loeschdatum DATE,                     -- Automatische Löschung an diesem Datum
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bewerbungen (Verknüpfung Bewerber ↔ Stelle)
-- DSGVO-Löschfrist: 6 Monate nach Verfahrensabschluss (§ 15 Abs. 4 AGG)
CREATE TABLE IF NOT EXISTS bewerbungen (
    id SERIAL PRIMARY KEY,
    bewerber_id INTEGER REFERENCES bewerber(id) ON DELETE CASCADE,
    stellen_id INTEGER REFERENCES stellen(id),
    status VARCHAR(50) DEFAULT 'neu',     -- neu, in_bearbeitung, eingeladen, angenommen, abgelehnt
    quelle VARCHAR(200),                  -- interamt.de, direkt, LinkedIn, etc.
    eingangsdatum DATE NOT NULL,
    notizen TEXT,
    manuelle_bewertung TEXT,              -- Bewertung durch menschliche Fachkraft
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Termine (Vorstellungsgespräche etc.)
CREATE TABLE IF NOT EXISTS termine (
    id SERIAL PRIMARY KEY,
    bewerber_id INTEGER REFERENCES bewerber(id) ON DELETE CASCADE,
    stellen_id INTEGER REFERENCES stellen(id),
    typ VARCHAR(100),                     -- Vorstellungsgespräch, Folgegespräch, etc.
    datum DATE NOT NULL,
    uhrzeit TIME NOT NULL,
    dauer_minuten INTEGER DEFAULT 60,
    ort VARCHAR(500),
    teilnehmer TEXT,                      -- JSON-Array mit Namen der Interviewer
    status VARCHAR(50) DEFAULT 'geplant', -- geplant, durchgeführt, abgesagt
    notizen TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Kommunikations-Log (DSGVO-Dokumentationspflicht)
CREATE TABLE IF NOT EXISTS kommunikation_log (
    id SERIAL PRIMARY KEY,
    bewerber_id INTEGER REFERENCES bewerber(id) ON DELETE CASCADE,
    stellen_id INTEGER REFERENCES stellen(id),
    typ VARCHAR(50),                      -- eingangsbestaetigung, einladung, absage, zusage
    empfaenger VARCHAR(500),
    betreff VARCHAR(500),
    inhalt TEXT,
    versanddatum TIMESTAMP,
    status VARCHAR(50),                   -- gesendet, fehlgeschlagen, vorbereitet
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- KI-Scoring-Details (Transparenz!)
-- WICHTIG: KI-Scoring ist Entscheidungshilfe, MENSCH entscheidet
CREATE TABLE IF NOT EXISTS scoring_details (
    id SERIAL PRIMARY KEY,
    bewerbung_id INTEGER REFERENCES bewerbungen(id) ON DELETE CASCADE,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    begruendung TEXT,
    staerken TEXT,                        -- JSON-Array
    schwaechen TEXT,                      -- JSON-Array
    rueckfragen TEXT,                     -- JSON-Array
    empfehlung TEXT,
    kriterien TEXT,                       -- JSON mit Detail-Scores
    ki_modell VARCHAR(100),               -- Welches KI-Modell verwendet wurde
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hinweis TEXT DEFAULT 'KI-Entscheidungshilfe — Letzte Entscheidung trifft die menschliche Fachkraft'
);

-- Audit-Log (Nachvollziehbarkeit, DSGVO)
-- Mindestens 2 Jahre aufbewahren
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    tabelle VARCHAR(100),
    datensatz_id INTEGER,
    aktion VARCHAR(50),                   -- CREATE, UPDATE, DELETE, LOGIN, EXPORT
    benutzer VARCHAR(200),
    ip_adresse VARCHAR(50),
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indizes für Performance
CREATE INDEX IF NOT EXISTS idx_bewerbungen_stellen ON bewerbungen(stellen_id);
CREATE INDEX IF NOT EXISTS idx_bewerbungen_status ON bewerbungen(status);
CREATE INDEX IF NOT EXISTS idx_bewerbungen_bewerber ON bewerbungen(bewerber_id);
CREATE INDEX IF NOT EXISTS idx_bewerber_loeschdatum ON bewerber(loeschdatum);
CREATE INDEX IF NOT EXISTS idx_termine_datum ON termine(datum);
CREATE INDEX IF NOT EXISTS idx_scoring_bewerbung ON scoring_details(bewerbung_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at);

-- ============================================================
-- DSGVO-Löschkonzept:
-- - Bewerberdaten: 6 Monate nach Verfahrensabschluss (§ 15 Abs. 4 AGG)
-- - Abgelehnte Bewerbungen: 6 Monate nach Absage
-- - Kommunikations-Log: 6 Monate nach letztem Kontakt
-- - Audit-Log: 2 Jahre (Revisionspflicht)
-- - scoring_details: Gelöscht zusammen mit Bewerbung
-- ============================================================
