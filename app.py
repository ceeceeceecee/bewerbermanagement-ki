# Bewerbermanagement-KI — Streamlit Web-App
# Vollständige Anwendung für deutsche Behörden
# KI-Backend: Ollama (lokal) | Claude API (optional)

import streamlit as st
import json
import os
import sys
from datetime import datetime, date

# Pfad für Imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Konfiguration laden
def load_config():
    """Lädt die YAML-Konfiguration oder gibt Defaults zurück."""
    config_path = os.path.join(os.path.dirname(__file__), "config", "settings.yaml")
    if os.path.exists(config_path):
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {
        "ollama": {"base_url": "http://localhost:11434", "model": "llama3"},
        "scoring": {"schwelle_einladung": 70, "schwelle_weiter": 50},
        "aufbewahrung": {"bewerbungen_monate": 6, "abgelehnte_monate": 3},
    }

CONFIG = load_config()

# ─── Seiten-Konfiguration ───────────────────────────────────────────────

st.set_page_config(
    page_title="Bewerbermanagement-KI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Benutzerdefiniertes CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1a365d;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #4a5568;
        margin-bottom: 1.5rem;
    }
    .score-high { color: #38a169; font-weight: 700; font-size: 1.5rem; }
    .score-mid { color: #d69e2e; font-weight: 700; font-size: 1.5rem; }
    .score-low { color: #e53e3e; font-weight: 700; font-size: 1.5rem; }
    .agg-badge {
        background: #ebf8ff;
        border: 1px solid #90cdf4;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-size: 0.85rem;
        color: #2c5282;
    }
    .section-card {
        background: #f7fafc;
        border: 1px solid #e2e8f0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Session State Initialisierung ───────────────────────────────────────

if "stellen" not in st.session_state:
    # Demo-Stellen
    st.session_state.stellen = [
        {
            "id": 1,
            "titel": "Fachangestellter/-r für Bürgerdienste (m/w/d)",
            "abteilung": "Bürgeramt",
            "referenz": "BA-2024-001",
            "status": "offen",
            "erstellt": "2024-01-15",
            "bewerbungen": 12,
        },
        {
            "id": 2,
            "titel": "IT-Systemadministrator (m/w/d)",
            "abteilung": "IT-Abteilung",
            "referenz": "IT-2024-003",
            "status": "in_bearbeitung",
            "erstellt": "2024-02-01",
            "bewerbungen": 8,
        },
        {
            "id": 3,
            "titel": "Verwaltungsfachangestellte/r (m/w/d)",
            "abteilung": "Allgemeine Verwaltung",
            "referenz": "AV-2024-005",
            "status": "besetzt",
            "erstellt": "2024-01-05",
            "bewerbungen": 23,
        },
    ]

if "bewerbungen" not in st.session_state:
    st.session_state.bewerbungen = [
        {
            "id": 1,
            "stellen_id": 1,
            "vorname": "Anna",
            "nachname": "Müller",
            "email": "anna.mueller@example.com",
            "eingangsdatum": "2024-01-20",
            "status": "neu",
            "score": 82,
            "quelle": "interamt.de",
        },
        {
            "id": 2,
            "stellen_id": 1,
            "vorname": "Thomas",
            "nachname": "Schmidt",
            "email": "thomas.schmidt@example.com",
            "eingangsdatum": "2024-01-22",
            "status": "neu",
            "score": 65,
            "quelle": "direktbewerbung",
        },
        {
            "id": 3,
            "stellen_id": 2,
            "vorname": "Lisa",
            "nachname": "Weber",
            "email": "lisa.weber@example.com",
            "eingangsdatum": "2024-02-05",
            "status": "eingeladen",
            "score": 91,
            "quelle": "LinkedIn",
        },
        {
            "id": 4,
            "stellen_id": 2,
            "vorname": "Markus",
            "nachname": "Fischer",
            "email": "markus.fischer@example.com",
            "eingangsdatum": "2024-02-08",
            "status": "abgelehnt",
            "score": 38,
            "quelle": "interamt.de",
        },
    ]

if "scoring_details" not in st.session_state:
    st.session_state.scoring_details = {
        1: {
            "score": 82,
            "begruendung": "Sehr passende Qualifikation. Abgeschlossene Ausbildung als Fachangestellte für Bürokommunikation mit 3 Jahren Berufserfahrung im Bürgerdienst. Hervorragende kommunikative Fähigkeiten und Engagement für öffentliche Verwaltung erkennbar.",
            "staerken": ["Relevante Berufsausbildung", "Berufserfahrung im Bürgerdienst", "Zertifikat in digitaler Verwaltung"],
            "rueckfragen": ["Wann ist die frühestmögliche Verfügbarkeit?"],
            "empfehlung": "Einladung zum Vorstellungsgespräch empfohlen",
        },
        2: {
            "score": 65,
            "begruendung": "Grundsätzlich passende Qualifikation, jedoch keine direkte Erfahrung im öffentlichen Dienst. Ausbildung als Kaufmännische Angestellte mit IT-Grundkenntnissen. Potenzial vorhanden.",
            "staerken": ["Gute Allgemeinbildung", "IT-Grundkenntnisse", "Motiviertes Anschreiben"],
            "rueckfragen": ["Bereitschaft zur Umschulung?", "Führerschein Klasse B vorhanden?"],
            "empfehlung": "Weiter in der Auswahl, Rückfragen klären",
        },
        3: {
            "score": 91,
            "begruendung": "Hervorragende Qualifikation. Studium der Informatik (B.Sc.) mit Schwerpunkt Systemadministration. Mehrjährige Erfahrung mit Linux-Servern, Netzwerken und Cloud-Infrastruktur. Zertifizierungen: RHCSA, AWS Cloud Practitioner.",
            "staerken": ["Informatikstudium", "Relevante Zertifizierungen", "Cloud-Erfahrung", "Open-Source-Engagement"],
            "rueckfragen": ["Gehaltsvorstellung?", "Kenntnisse in ITIL?"],
            "empfehlung": "Dringend zur Einladung empfehlen — Top-Kandidat",
        },
        4: {
            "score": 38,
            "begruendung": "Qualifikationsprofil passt nur teilweise. Keine formale IT-Ausbildung oder relevantes Studium. Erfahrungen liegen im Bereich Vertrieb. Keine nachweisbaren technischen Fähigkeiten für Systemadministration.",
            "staerken": ["Gute Kommunikation", "Teamfähigkeit"],
            "rueckfragen": [],
            "empfehlung": "Leider nicht passend für diese Stelle",
        },
    }

if "termine" not in st.session_state:
    st.session_state.termine = [
        {
            "id": 1,
            "bewerber_id": 3,
            "stelle": "IT-Systemadministrator",
            "bewerber": "Lisa Weber",
            "datum": "2024-03-15",
            "uhrzeit": "10:00",
            "ort": "Rathaus, Raum 204",
            "typ": "Vorstellungsgespräch",
            "status": "geplant",
        },
    ]

# ─── Hilfsfunktionen ─────────────────────────────────────────────────────

def get_stelle_name(stellen_id):
    """Gibt den Stellentitel anhand der ID zurück."""
    for s in st.session_state.stellen:
        if s["id"] == stellen_id:
            return s["titel"]
    return "Unbekannte Stelle"

def get_score_class(score):
    """Gibt CSS-Klasse basierend auf Score zurück."""
    if score >= 70:
        return "score-high"
    elif score >= 50:
        return "score-mid"
    return "score-low"

def get_status_emoji(status):
    """Emoji für Bewerbungsstatus."""
    mapping = {
        "neu": "🆕",
        "in_bearbeitung": "📝",
        "eingeladen": "📧",
        "interview_geplant": "📅",
        "angenommen": "✅",
        "abgelehnt": "❌",
    }
    return mapping.get(status, "❓")

# ─── Sidebar ─────────────────────────────────────────────────────────────

st.sidebar.image("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgdmlld0JveD0iMCAwIDYwIDYwIj48dGV4dCB4PSIzMCIgeT0iNDAiIGZvbnQtc2l6ZT0iNDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiPvCfp6Y8L3RleHQ+PC9zdmc+", width=60)
st.sidebar.title("Bewerbermanagement-KI")
st.sidebar.caption("für deutsche Behörden")

st.sidebar.markdown("---")

# AGG-Hinweis (immer sichtbar)
st.sidebar.markdown("""
<div class="agg-badge">
⚖️ <strong>AGG-Hinweis:</strong> Die KI dient ausschließlich als
Entscheidungshilfe. Letzte Entscheidung liegt immer bei der
menschlichen Fachkraft.
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("🏛️ Self-Hosted | 🔒 DSGVO-konform")
st.sidebar.markdown("🤖 Ollama als KI-Backend")

# ─── Hauptnavigation ────────────────────────────────────────────────────

seite = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "📋 Stellenausschreibungen",
        "🤖 KI-Optimierung",
        "📨 Bewerbungen",
        "👤 Bewerber-Detail",
        "📅 Termine",
        "📈 Statistiken",
    ],
    index=0,
)

st.markdown('<div class="main-header">🏛️ Bewerbermanagement-KI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Moderne HR-Lösung für deutsche Behörden</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# SEITE: Dashboard
# ═══════════════════════════════════════════════════════════════════════

if seite == "📊 Dashboard":
    st.header("📊 Dashboard")

    # KPI-Karten
    k1, k2, k3, k4 = st.columns(4)
    offene_stellen = len([s for s in st.session_state.stellen if s["status"] == "offen"])
    neue_bew = len([b for b in st.session_state.bewerbungen if b["status"] == "neu"])
    geplante_termine = len([t for t in st.session_state.termine if t["status"] == "geplant"])
    avg_score = (
        sum(b["score"] for b in st.session_state.bewerbungen)
        / len(st.session_state.bewerbungen)
        if st.session_state.bewerbungen
        else 0
    )

    k1.metric("Offene Stellen", offene_stellen)
    k2.metric("Neue Bewerbungen", neue_bew)
    k3.metric("Geplante Termine", geplante_termine)
    k4.metric("Ø Score", f"{avg_score:.0f}")

    st.markdown("---")

    # Letzte Bewerbungen
    st.subheader("Letzte Bewerbungen")
    for b in st.session_state.bewerbungen[:5]:
        stelle = get_stelle_name(b["stellen_id"])
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        col1.write(f"**{b['vorname']} {b['nachname']}** — {stelle}")
        col2.write(f"{b['eingangsdatum']}")
        col3.write(get_status_emoji(b["status"]))
        col4.markdown(f'<span class="{get_score_class(b["score"])}">{b["score"]}</span>', unsafe_allow_html=True)

    st.markdown("---")

    # AGG-Konformitätshinweis
    st.info("""
    ⚖️ **AGG-Konformität:** Alle angezeigten KI-Scores sind Entscheidungshilfen.
    Die endgültige Bewertung und Entscheidung obliegt immer der verantwortlichen
    Fachkraft. KI-Ergebnisse dürfen nicht alleiniges Kriterium sein.
    """)

# ═══════════════════════════════════════════════════════════════════════
# SEITE: Stellenausschreibungen
# ═══════════════════════════════════════════════════════════════════════

elif seite == "📋 Stellenausschreibungen":
    st.header("📋 Stellenausschreibungen")

    tab1, tab2 = st.tabs(["Übersicht", "Neue Stelle erstellen"])

    with tab1:
        for stelle in st.session_state.stellen:
            with st.expander(f"{stelle['titel']} — {stelle['referenz']}", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.write(f"**Abteilung:** {stelle['abteilung']}")
                c2.write(f"**Status:** {stelle['status'].replace('_', ' ').title()}")
                c3.write(f"**Erstellt:** {stelle['erstellt']}")
                c4.write(f"**Bewerbungen:** {stelle['bewerbungen']}")

    with tab2:
        with st.form("neue_stelle"):
            titel = st.text_input("Stellentitel", placeholder="z.B. Sachbearbeiter (m/w/d)")
            abteilung = st.text_input("Abteilung")
            referenz = st.text_input("Referenznummer", placeholder="z.B. SB-2024-001")
            beschreibung = st.text_area("Stellenbeschreibung", height=200)
            angebot = st.text_area("Was wir bieten", height=100)
            submitted = st.form_submit_button("Stelle erstellen")
            if submitted:
                if titel and abteilung:
                    neue_id = max(s["id"] for s in st.session_state.stellen) + 1 if st.session_state.stellen else 1
                    st.session_state.stellen.append({
                        "id": neue_id,
                        "titel": titel,
                        "abteilung": abteilung,
                        "referenz": referenz or f"REF-{neue_id}",
                        "status": "offen",
                        "erstellt": date.today().isoformat(),
                        "bewerbungen": 0,
                    })
                    st.success(f"Stelle '{titel}' wurde erstellt!")
                    st.rerun()
                else:
                    st.error("Bitte Titel und Abteilung angeben.")

# ═══════════════════════════════════════════════════════════════════════
# SEITE: KI-Optimierung
# ═══════════════════════════════════════════════════════════════════════

elif seite == "🤖 KI-Optimierung":
    st.header("🤖 KI-Optimierung von Ausschreibungstexten")

    st.warning("""
    ⚠️ **Hinweis:** Die KI-Vorschläge dienen der Optimierung und sind keine verbindlichen
    Texte. Bitte prüfen Sie alle Vorschläge sorgfältig vor der Veröffentlichung.
    """)

    # AGG-Check-Bereich
    st.subheader("🔍 AGG-Diskriminierungs-Check")

    text_zum_checken = st.text_area(
        "Text auf diskriminierende Formulierungen prüfen",
        height=150,
        placeholder="Fügen Sie hier den Ausschreibungstext ein...",
    )

    if st.button("🔍 Auf AGG-Verstöße prüfen", type="primary"):
        if text_zum_checken.strip():
            with st.spinner("KI prüft den Text auf AGG-Konformität..."):
                # Simulierter KI-Check (in Produktion: Ollama API)
                probleme = []
                texte = text_zum_checken.lower()
                if "jung" in texte and "dynamisch" in texte:
                    probleme.append("⚠️ 'Jung und dynamisch' könnte als Altersdiskriminierung gewertet werden")
                if "männlich" in texte and "(m/w/d)" not in texte:
                    probleme.append("⚠️ Geschlechtspezifische Formulierung ohne (m/w/d) Kennzeichnung")
                if "deutsch als muttersprache" in texte:
                    probleme.append("⚠️ 'Deutsch als Muttersprache' könnte ethnische Diskriminierung darstellen")

                if probleme:
                    st.error("Mögliche AGG-Verstöße gefunden:")
                    for p in probleme:
                        st.write(p)
                else:
                    st.success("✅ Keine offensichtlichen AGG-Verstöße gefunden. (Hinweis: Dies ersetzt keine juristische Prüfung.)")
        else:
            st.warning("Bitte Text eingeben.")

    st.markdown("---")

    # Ausschreibung optimieren
    st.subheader("✍️ Ausschreibungstext optimieren")

    stelle_auswahl = st.selectbox(
        "Stelle auswählen",
        options=[s["titel"] for s in st.session_state.stellen],
    )

    optimierung_target = st.selectbox(
        "Optimierungsziel",
        ["Modernisierung", "AGG-konform anpassen", "Attraktivität steigern", "Vollständige Überarbeitung"],
    )

    if st.button("🤖 Text optimieren lassen"):
        st.info("In der Produktivumgebung wird hier der Ollama-Server kontaktiert und der Text analysiert.")
        st.success("Optimierung abgeschlossen! (Demo-Modus)")

    st.markdown("---")

    # Zusammenfassung generieren
    st.subheader("📝 Kurzzusammenfassung generieren")
    beschreibung_input = st.text_area("Stellenbeschreibung", height=100, key="summary_input")

    if st.button("Zusammenfassung erstellen"):
        if beschreibung_input.strip():
            st.info("KI-generierte Zusammenfassung wird hier angezeigt (Ollama-Integration erforderlich).")
        else:
            st.warning("Bitte Stellenbeschreibung eingeben.")

# ═══════════════════════════════════════════════════════════════════════
# SEITE: Bewerbungen
# ═══════════════════════════════════════════════════════════════════════

elif seite == "📨 Bewerbungen":
    st.header("📨 Bewerbungen verwalten")

    # Filter
    c1, c2 = st.columns(2)
    filter_stelle = c1.selectbox(
        "Stelle filtern",
        ["Alle Stellen"] + [s["titel"] for s in st.session_state.stellen],
    )
    filter_status = c2.selectbox(
        "Status filtern",
        ["Alle"] + ["neu", "in_bearbeitung", "eingeladen", "interview_geplant", "angenommen", "abgelehnt"],
    )

    # Gefilterte Liste
    gefiltert = st.session_state.bewerbungen
    if filter_stelle != "Alle Stellen":
        stellen_id = next((s["id"] for s in st.session_state.stellen if s["titel"] == filter_stelle), None)
        if stellen_id:
            gefiltert = [b for b in gefiltert if b["stellen_id"] == stellen_id]
    if filter_status != "Alle":
        gefiltert = [b for b in gefiltert if b["status"] == filter_status]

    st.write(f"**{len(gefiltert)} Bewerbung(en)** gefunden")

    # Tabelle
    for b in gefiltert:
        stelle = get_stelle_name(b["stellen_id"])
        details = st.session_state.scoring_details.get(b["id"], {})
        score = details.get("score", b.get("score", 0))

        with st.expander(
            f"{get_status_emoji(b['status'])} {b['vorname']} {b['nachname']} — {stelle[:40]}",
            expanded=(b["status"] == "neu"),
        ):
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(f"**E-Mail:** {b['email']}")
            c1.write(f"**Eingang:** {b['eingangsdatum']}")
            c1.write(f"**Quelle:** {b['quelle']}")
            c2.write(f"**Stelle:** {stelle}")
            c2.write(f"**Status:** {b['status'].replace('_', ' ').title()}")
            c2.markdown(f"**KI-Score:** <span class='{get_score_class(score)}'>{score}/100</span>", unsafe_allow_html=True)

            # Transparente KI-Bewertung
            if details:
                st.markdown("---")
                st.subheader("🤖 KI-Bewertung (Entscheidungshilfe)")
                st.warning("⚠️ Dieser Score wurde von einer KI ermittelt und dient ausschließlich als Unterstützung. Die endgültige Entscheidung trifft die verantwortliche Fachkraft.")

                sc1, sc2 = st.columns([1, 3])
                sc1.markdown(f"<span class='{get_score_class(score)}'>{score}/100</span>", unsafe_allow_html=True)
                sc2.write(details.get("begruendung", "Keine Begründung verfügbar."))

                if details.get("staerken"):
                    st.write("**Stärken:** " + " | ".join(f"✅ {s}" for s in details["staerken"]))
                if details.get("rueckfragen"):
                    st.write("**Rückfragen:** " + " | ".join(f"❓ {r}" for r in details["rueckfragen"]))
                if details.get("empfehlung"):
                    st.info(f"💡 **Empfehlung:** {details['empfehlung']}")

            # Aktionen
            st.markdown("---")
            ac1, ac2, ac3, ac4 = st.columns(4)
            if ac1.button("📧 Einladen", key=f"einladen_{b['id']}"):
                b["status"] = "eingeladen"
                st.success(f"Einladung an {b['vorname']} {b['nachname']} gesendet (Demo).")
                st.rerun()
            if ac2.button("✅ Annehmen", key=f"annehmen_{b['id']}"):
                b["status"] = "angenommen"
                st.success(f"{b['vorname']} {b['nachname']} wurde angenommen!")
                st.rerun()
            if ac3.button("❌ Ablehnen", key=f"ablehnen_{b['id']}"):
                b["status"] = "abgelehnt"
                st.info(f"Absage an {b['vorname']} {b['nachname']} erstellt (Demo).")
                st.rerun()
            if ac4.button("📅 Termin", key=f"termin_{b['id']}"):
                st.session_state["termin_bewerber_id"] = b["id"]
                st.info("Bitte auf 'Termine' gehen, um einen Termin zu planen.")

    # Neue Bewerbung hochladen
    st.markdown("---")
    st.subheader("📄 Neue Bewerbung erfassen")
    with st.form("neue_bewerbung"):
        nc1, nc2 = st.columns(2)
        vorname = nc1.text_input("Vorname")
        nachname = nc2.text_input("Nachname")
        email = st.text_input("E-Mail")
        stelle_select = st.selectbox(
            "Stelle",
            options=[(s["id"], s["titel"]) for s in st.session_state.stellen],
            format_func=lambda x: x[1],
        )
        quelle = st.text_input("Bewerbungsquelle (z.B. interamt.de, direkt)")
        lebenslauf = st.file_uploader("Lebenslauf (PDF)", type=["pdf"])

        submitted = st.form_submit_button("Bewerbung speichern & analysieren")
        if submitted and vorname and nachname:
            neue_id = max(b["id"] for b in st.session_state.bewerbungen) + 1 if st.session_state.bewerbungen else 1
            st.session_state.bewerbungen.append({
                "id": neue_id,
                "stellen_id": stelle_select[0],
                "vorname": vorname,
                "nachname": nachname,
                "email": email,
                "eingangsdatum": date.today().isoformat(),
                "status": "neu",
                "score": 0,
                "quelle": quelle or "direktbewerbung",
            })
            st.success(f"Bewerbung von {vorname} {nachname} gespeichert! KI-Analyse wird in Produktion automatisch gestartet.")
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# SEITE: Bewerber-Detail
# ═══════════════════════════════════════════════════════════════════════

elif seite == "👤 Bewerber-Detail":
    st.header("👤 Bewerber-Detailansicht")

    bewerber_id = st.selectbox(
        "Bewerber auswählen",
        options=[b["id"] for b in st.session_state.bewerbungen],
        format_func=lambda x: f"{next((b['vorname'] + ' ' + b['nachname'] for b in st.session_state.bewerbungen if b['id'] == x), 'Unbekannt')}",
    )

    bewerber = next((b for b in st.session_state.bewerbungen if b["id"] == bewerber_id), None)
    if bewerber:
        details = st.session_state.scoring_details.get(bewerber_id, {})
        stelle = get_stelle_name(bewerber["stellen_id"])
        score = details.get("score", bewerber.get("score", 0))

        # Profil
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("### 👤 Profil")
            st.write(f"**Name:** {bewerber['vorname']} {bewerber['nachname']}")
            st.write(f"**E-Mail:** {bewerber['email']}")
            st.write(f"**Eingang:** {bewerber['eingangsdatum']}")
            st.write(f"**Quelle:** {bewerber['quelle']}")
            st.write(f"**Status:** {bewerber['status'].replace('_', ' ').title()}")
            st.markdown(f"**KI-Score:** <span class='{get_score_class(score)}'>{score}/100</span>", unsafe_allow_html=True)

        with c2:
            st.markdown("### 📋 Beworbene Stelle")
            st.write(f"**{stelle}**")
            st.write(f"**Referenz:** {next((s['referenz'] for s in st.session_state.stellen if s['id'] == bewerber['stellen_id']), '—')}")

            # Upload-Bereich
            st.markdown("### 📎 Dokumente")
            st.file_uploader("Lebenslauf (PDF)", type=["pdf"], key="detail_cv")
            st.file_uploader("Anschreiben (PDF)", type=["pdf"], key="detail_letter")
            st.file_uploader("Zeugnisse (PDF)", type=["pdf"], key="detail_certs")

        # KI-Scoring-Details
        if details:
            st.markdown("---")
            st.markdown("### 🤖 Transparente KI-Bewertung")
            st.warning("""
            ⚖️ **AGG-Hinweis:** Dieses Scoring wurde durch eine Künstliche Intelligenz erstellt.
            Es dient ausschließlich als Entscheidungshilfe für die menschliche Fachkraft.
            Automatisierte Entscheidungen im Sinne des § 15 Abs. 1 AGG werden nicht getroffen.
            Die verantwortliche Person muss das Ergebnis eigenverantwortlich prüfen und
            gegebenenfalls korrigieren.
            """)

            sc1, sc2, sc3 = st.columns([1, 3, 2])
            with sc1:
                st.markdown(f"<span class='{get_score_class(score)}' style='font-size:3rem'>{score}</span>", unsafe_allow_html=True)
                st.caption("/ 100 Punkte")

            with sc2:
                st.write("**Begründung:**")
                st.write(details.get("begruendung", "Nicht verfügbar."))

                if details.get("staerken"):
                    st.write("**Identifizierte Stärken:**")
                    for s in details["staerken"]:
                        st.write(f"  ✅ {s}")

                if details.get("rueckfragen"):
                    st.write("**Offene Rückfragen:**")
                    for r in details["rueckfragen"]:
                        st.write(f"  ❓ {r}")

            with sc3:
                st.write("**Empfehlung:**")
                st.info(details.get("empfehlung", "Keine Empfehlung."))

                st.write("**Bewertungskriterien (Demo):**")
                st.write("  - Qualifikation: 35%")
                st.write("  - Berufserfahrung: 30%")
                st.write("  - Motivation: 20%")
                st.write("  - Soft Skills: 15%")

        # Manuelle Notizen
        st.markdown("---")
        st.subheader("📝 Manuelle Notizen der Fachkraft")
        notizen = st.text_area("Notizen und Bewertung durch die verantwortliche Person", height=100)
        if st.button("Notizen speichern"):
            st.success("Notizen gespeichert (Demo).")

        # Status-Änderung
        st.subheader("🔄 Status ändern")
        neuer_status = st.selectbox(
            "Neuer Status",
            ["neu", "in_bearbeitung", "eingeladen", "interview_geplant", "angenommen", "abgelehnt"],
            index=["neu", "in_bearbeitung", "eingeladen", "interview_geplant", "angenommen", "abgelehnt"].index(bewerber["status"]),
        )
        if st.button("Status aktualisieren"):
            bewerber["status"] = neuer_status
            st.success(f"Status auf '{neuer_status.replace('_', ' ').title()}' geändert.")
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# SEITE: Termine
# ═══════════════════════════════════════════════════════════════════════

elif seite == "📅 Termine":
    st.header("📅 Terminmanagement")

    tab1, tab2 = st.tabs(["Übersicht", "Neuer Termin"])

    with tab1:
        if not st.session_state.termine:
            st.info("Noch keine Termine vorhanden.")
        else:
            for t in st.session_state.termine:
                with st.expander(f"{t['typ']} — {t['bewerber']} am {t['datum']}", expanded=True):
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"**Stelle:** {t['stelle']}")
                    c1.write(f"**Bewerber:** {t['bewerber']}")
                    c2.write(f"**Datum:** {t['datum']}")
                    c2.write(f"**Uhrzeit:** {t['uhrzeit']}")
                    c3.write(f"**Ort:** {t['ort']}")
                    c3.write(f"**Status:** {t['status'].title()}")

                    if st.button("✅ Abschließen", key=f"abschliessen_{t['id']}"):
                        t["status"] = "abgeschlossen"
                        st.success("Termin als abgeschlossen markiert.")
                        st.rerun()

    with tab2:
        with st.form("neuer_termin"):
            bewerber_auswahl = st.selectbox(
                "Bewerber",
                options=[(b["id"], f"{b['vorname']} {b['nachname']}") for b in st.session_state.bewerbungen],
                format_func=lambda x: x[1],
            )
            termin_datum = st.date_input("Datum")
            termin_uhrzeit = st.time_input("Uhrzeit")
            termin_ort = st.text_input("Ort", value="Rathaus, Raum 204")
            termin_typ = st.selectbox(
                "Terminart",
                ["Vorstellungsgespräch", "Folgegespräch", "Praktischer Test", "Assessment-Center"],
            )

            submitted = st.form_submit_button("Termin erstellen")
            if submitted:
                bew_id = bewerber_auswahl[0]
                bewerber = next((b for b in st.session_state.bewerbungen if b["id"] == bew_id), None)
                neue_id = max((t["id"] for t in st.session_state.termine), default=0) + 1
                st.session_state.termine.append({
                    "id": neue_id,
                    "bewerber_id": bew_id,
                    "stelle": get_stelle_name(bewerber["stellen_id"]) if bewerber else "Unbekannt",
                    "bewerber": bewerber_auswahl[1] if bewerber else "Unbekannt",
                    "datum": termin_datum.isoformat(),
                    "uhrzeit": termin_uhrzeit.strftime("%H:%M"),
                    "ort": termin_ort,
                    "typ": termin_typ,
                    "status": "geplant",
                })
                st.success("Termin erstellt!")
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# SEITE: Statistiken
# ═══════════════════════════════════════════════════════════════════════

elif seite == "📈 Statistiken":
    st.header("📈 Statistiken & Reporting")

    # Bewerbungen pro Status
    st.subheader("Bewerbungen nach Status")
    status_counts = {}
    for b in st.session_state.bewerbungen:
        status_counts[b["status"]] = status_counts.get(b["status"], 0) + 1

    if status_counts:
        st.bar_chart(status_counts)

    # Score-Verteilung
    st.subheader("Score-Verteilung")
    scores = [b["score"] for b in st.session_state.bewerbungen if b["score"] > 0]
    if scores:
        ranges = {"0-30": 0, "31-50": 0, "51-70": 0, "71-85": 0, "86-100": 0}
        for s in scores:
            if s <= 30:
                ranges["0-30"] += 1
            elif s <= 50:
                ranges["31-50"] += 1
            elif s <= 70:
                ranges["51-70"] += 1
            elif s <= 85:
                ranges["71-85"] += 1
            else:
                ranges["86-100"] += 1
        st.bar_chart(ranges)

    # Quellen-Analyse
    st.subheader("Bewerbungsquellen")
    quellen = {}
    for b in st.session_state.bewerbungen:
        quellen[b["quelle"]] = quellen.get(b["quelle"], 0) + 1
    if quellen:
        st.bar_chart(quellen)

    # Stellenübersicht
    st.subheader("Stellenübersicht")
    for stelle in st.session_state.stellen:
        bew_fuer_stelle = [b for b in st.session_state.bewerbungen if b["stellen_id"] == stelle["id"]]
        avg = sum(b["score"] for b in bew_fuer_stelle) / len(bew_fuer_stelle) if bew_fuer_stelle else 0
        st.write(f"**{stelle['titel']}** ({stelle['referenz']}): {len(bew_fuer_stelle)} Bewerbungen, Ø-Score: {avg:.0f}")

    # DSGVO-Hinweis
    st.markdown("---")
    st.warning("""
    🔒 **Datenschutz-Hinweis:** Diese Statistiken enthalten personenbezogene Daten.
    Entsprechend der DSGVO und der Aufbewahrungsfristen müssen Bewerberdaten
    nach Ablauf der Frist gelöscht werden. Bitte beachten Sie das Löschkonzept
    in der Dokumentation.
    """)

# ─── Footer ──────────────────────────────────────────────────────────────

st.markdown("---")
st.caption("Bewerbermanagement-KI | © 2024 | MIT License | Ollama als KI-Backend | DSGVO & AGG konform")
