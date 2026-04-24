# Installation — Bewerbermanagement-KI

## Voraussetzungen

- **Docker** & **Docker Compose** (empfohlen)
- Alternativ: Python 3.11+ mit PostgreSQL und Redis
- **Ollama** (lokal installiert für KI-Funktionen)

## Option 1: Docker (Empfohlen)

### 1. Repository klonen

```bash
git clone https://github.com/ceeceeceecee/bewerbermanagement-ki.git
cd bewerbermanagement-ki
```

### 2. Konfiguration anpassen

```bash
cp config/settings.example.yaml config/settings.yaml
cp config/bewertungskriterien.example.yaml config/bewertungskriterien.yaml
```

Bearbeiten Sie `config/settings.yaml` und passen Sie:
- SMTP-Zugangsdaten
- Datenbank-Passwort
- Behördenname

### 3. Setup ausführen

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 4. Anwendung öffnen

 Öffnen Sie: **http://localhost:8501**

## Option 2: Manuelle Installation

### 1. Python-Umgebung erstellen

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# oder: venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. PostgreSQL einrichten

```bash
# Datenbank erstellen
createdb bewerbermanagement
createuser bewerberki -P

# Schema importieren
psql -U bewerberki -d bewerbermanagement -f database/schema.sql
```

### 3. Redis starten

```bash
redis-server
```

### 4. Ollama installieren & Modell laden

```bash
# Ollama installieren (https://ollama.ai)
curl -fsSL https://ollama.ai/install.sh | sh

# Modell herunterladen
ollama pull llama3
```

### 5. Konfiguration

```bash
cp config/settings.example.yaml config/settings.yaml
# settings.yaml bearbeiten
```

### 6. Anwendung starten

```bash
streamlit run app.py --server.port 8501
```

## Ollama-Konfiguration

### Empfohlene Modelle

| Modell | Größe | Empfehlung |
|--------|-------|------------|
| llama3 | ~4.7 GB | Standard — gutes Preis-Leistungs-Verhältnis |
| mistral | ~4.1 GB | Leichter, schneller |
| llama3:70b | ~40 GB | Beste Qualität (erfordert starke Hardware) |

### Ollama testen

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3",
  "messages": [{"role": "user", "content": "Hallo"}],
  "stream": false
}'
```

## Umgebungsvariablen

| Variable | Standard | Beschreibung |
|----------|----------|-------------|
| `DATABASE_URL` | postgresql://bewerberki:bewerberki@localhost:5432/bewerbermanagement | Datenbankverbindung |
| `REDIS_URL` | redis://localhost:6379/0 | Redis-Verbindung |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama API |
| `TZ` | Europe/Berlin | Zeitzone |

## Erster Start

1. Öffnen Sie http://localhost:8501
2. Prüfen Sie das Dashboard
3. Erstellen Sie eine erste Stellenausschreibung
4. Laden Sie eine Demo-Bewerbung hoch
5. Testen Sie das KI-Scoring (Ollama muss laufen)

## Fehlerbehebung

### Ollama nicht erreichbar
```bash
# Ollama-Status prüfen
ollama list

# Ollama neu starten
ollama serve
```

### Datenbank-Verbindung fehlgeschlagen
```bash
# PostgreSQL-Status prüfen
docker compose ps db

# Logs anzeigen
docker compose logs db
```

### Port bereits belegt
```bash
# Prüfen welcher Prozess Port 8501 nutzt
lsof -i :8501
```
