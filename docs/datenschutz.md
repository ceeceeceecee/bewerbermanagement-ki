# Datenschutzerklärung — Bewerbermanagement-KI

## 1. Verantwortliche Stelle

Die verantwortliche Stelle für die Datenverarbeitung ist die jeweilige Behörde, die dieses System einsetzt.

## 2. Zweck der Datenverarbeitung

Das Bewerbermanagement-KI verarbeitet personenbezogene Daten ausschließlich zum Zweck der:

- Verwaltung von Stellenausschreibungen
- Bearbeitung von eingehenden Bewerbungen
- Organisation von Vorstellungsgesprächen
- Kommunikation mit Bewerbern
- Statistischen Auswertung des Recruiting-Prozesses

Rechtsgrundlage: Art. 6 Abs. 1 lit. b DSGVO (Bewerbungsverfahren als Vertragserfüllung)

## 3. Besonders schützenswerte Daten

Bewerberdaten können folgende besonders schützenswerte Datenkategorien (Art. 9 DSGVO) umfassen:

- Gesundheitsdaten (bei Angabe von Behinderungen)
- Ethnische Herkunft (bei Angabe)
- Politische Meinungen (bei Angabe)

**Diese Daten werden nur verarbeitet, wenn der Bewerber ausdrücklich eingewilligt hat (Art. 9 Abs. 2 lit. a DSGVO).**

## 4. KI-Verarbeitung

### KI-Scoring
- Die KI-Analyse dient ausschließlich als **Entscheidungshilfe** für die menschliche Fachkraft
- Es werden **keine automatisierten Entscheidungen** im Sinne des Art. 22 DSGVO getroffen
- Die KI läuft **lokal** (Ollama) — es werden keine Daten an externe Server übermittelt

### KI-Optimierung von Texten
- Ausschreibungstexte werden lokal durch die KI optimiert
- Keine Bewerberdaten werden für die Textoptimierung verwendet

## 5. Aufbewahrungsfristen

| Datenkategorie | Aufbewahrungsfrist | Rechtsgrundlage |
|---|---|---|
| Bewerbungsunterlagen | 6 Monate nach Verfahrensabschluss | § 15 Abs. 4 AGG |
| Abgelehnte Bewerbungen | 6 Monate nach Absage | § 15 Abs. 4 AGG |
| Eingestellte Bewerber | Übergang in Personalakte | BDSG |
| Kommunikations-Log | 6 Monate nach letztem Kontakt | DSGVO |
| Audit-Log | 24 Monate | Revisionspflicht |
| Scoring-Details | Zusammen mit Bewerbung | DSGVO |

## 6. Löschkonzept

### Automatische Löschung
Das System bietet eine automatische Löschfunktion, die regelmäßig prüft, ob die Aufbewahrungsfristen abgelaufen sind:

1. Täglich wird geprüft, ob Löschdaten erreicht sind
2. Betroffene Datensätze werden automatisch gelöscht
3. Alle Löschungen werden im Audit-Log dokumentiert

### Manuelles Löschen
Bewerber haben jederzeit das Recht auf:
- **Auskunft** (Art. 15 DSGVO)
- **Berichtigung** (Art. 16 DSGVO)
- **Löschung** (Art. 17 DSGVO)
- **Einschränkung** (Art. 18 DSGVO)
- **Datenübertragbarkeit** (Art. 20 DSGVO)

### Kaskaden-Löschung
Beim Löschen eines Bewerbers werden automatisch gelöscht:
- Alle verknüpften Bewerbungen
- Alle Termine
- Alle Kommunikations-Einträge
- Alle Scoring-Details

## 7. Technische Maßnahmen

- **Verschlüsselung:** PostgreSQL mit SSL, HTTPS für die Web-App
- **Zugriffskontrolle:** Rollenbasiertes Zugriffssystem
- **Audit-Log:** Alle Zugriffe und Änderungen werden protokolliert
- **Lokale KI:** Ollama läuft auf dem eigenen Server — keine Datenabgabe
- **Backup:** Regelmäßige verschlüsselte Backups

## 8. Einwilligung

Vor der Verarbeitung von Bewerberdaten muss die Einwilligung eingeholt werden:

- Einwilligungserklärung zur Datenverarbeitung
- Hinweis auf die Verarbeitung durch KI
- Hinweis auf die Aufbewahrungsfristen
- Recht auf Widerruf

## 9. Datenschutz-Folgenabschätzung

Da die KI nur als Entscheidungshilfe dient und keine automatisierten Entscheidungen trifft, ist eine Datenschutz-Folgenabschätzung (Art. 35 DSGVO) in der Regel nicht erforderlich. Dies sollte jedoch im Einzelfall geprüft werden.

## 10. Kontakt

Bei Fragen zum Datenschutz wenden Sie sich an den Datenschutzbeauftragten Ihrer Behörde.
