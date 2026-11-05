import streamlit as st
import io
import os
from datetime import datetime
from PIL import Image
from streamlit_cropper import st_cropper
from supabase import create_client, Client

# ---------------------------------------------------------
# SEITEN-KONFIGURATION & INITIALISIERUNG
# ---------------------------------------------------------
st.set_page_config(page_title="Travel Buddy", page_icon="✈️", layout="wide")

SUPABASE_URL = "https://iryqxhtqnzdfqrquswzb.supabase.co"
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "DEIN_ANON_KEY_HIER_EINTRAGEN")

ADMIN_EMAIL = "t_feisst@web.de"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_supabase()

if "user" not in st.session_state:
    st.session_state.user = None

# ---------------------------------------------------------
# CSS-OPTIMIERUNG FÜR MODERNE 20:9 SMARTPHONE-PROFILBILDER
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Länglicher, moderner Handy-Profilbild-Container (ca. 20:9 Verhältnis) */
    .profile-card-img-container {
        width: 100% !important;
        height: 480px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: #2b2b2b !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        margin-bottom: 12px !important;
    }
    
    /* Oben zentriert für den perfekten Kopf-Fokus */
    .profile-card-img {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
        object-position: center top !important;
    }
    
    /* Platzhalter für Profile ohne Bild */
    .profile-placeholder {
        font-size: 6rem !important;
        color: #777777 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATENBANK- & STORAGE-FUNKTIONEN
# ---------------------------------------------------------
def profile_initialisieren_falls_leer():
    try:
        response = supabase.from_("reise_profil").select("id", count="exact").execute()
        if not response.data or len(response.data) == 0:
            beispiele = [
                {"name": "Anna", "alter": 28, "profil_text": "Liebe die Natur und das Meer!", "reise_stil": "Strand & Wellness", "budget": "Mittelklasse", "tempo": "Entspannt", "wunsch_kontinent": "Europa", "wunsch_land": "Spanien", "charakter": "Spontan & Offen", "avatar_url": ""},
                {"name": "Maximilian", "alter": 32, "profil_text": "Backpacking in Asien.", "reise_stil": "Backpacking", "budget": "Günstig", "tempo": "Actionreich", "wunsch_kontinent": "Asien", "wunsch_land": "Thailand", "charakter": "Aktiv & Sportlich", "avatar_url": ""},
                {"name": "Sophie", "alter": 27, "profil_text": "Städtetrips und Kultur.", "reise_stil": "Kultur & Städtetrip", "budget": "Mittelklasse", "tempo": "Ausgewogen", "wunsch_kontinent": "Europa", "wunsch_land": "Italien", "charakter": "Genießer & Entspannt", "avatar_url": ""}
            ]
            for b in beispiele:
                supabase.from_("reise_profil").insert(b).execute()
    except Exception as e:
        print(f"Hinweis beim Initialisieren: {e}")

profile_initialisieren_falls_leer()

@st.cache_data(ttl=30)
def alle_profile_laden():
    try:
        response = supabase.from_("reise_profil").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Fehler beim Laden der Profile: {e}")
        return []

@st.cache_data(ttl=30)
def alle_nachrichten_laden():
    try:
        response = supabase.from_("nachrichten").select("*").execute()
        return response.data if response.data else []
    except Exception:
        return []

def zugeschnittenes_bild_hochladen(cropped_img):
    if cropped_img is None:
        return ""
    try:
        buffered = io.BytesIO()
        cropped_img.save(buffered, format="JPEG")
        file_bytes = buffered.getvalue()
        file_name = f"{datetime.now().timestamp()}_profile.jpg"

        supabase.storage.from_("profil_bilder").upload(
            path=file_name,
            file=file_bytes,
            file_options={"content-type": "image/jpeg"}
        )
        return supabase.storage.from_("profil_bilder").get_public_url(file_name)
    except Exception as e:
        st.error(f"Fehler beim Bildupload: {e}")
        return ""

def profil_speichern(name, alter, profil_text, reise_stil, budget, tempo, wunsch_kontinent, wunsch_land, charakter, avatar_url):
    daten = {
        "name": name, "alter": alter, "profil_text": profil_text,
        "reise_stil": reise_stil, "budget": budget, "tempo": tempo,
        "wunsch_kontinent": wunsch_kontinent, "wunsch_land": wunsch_land,
        "charakter": charakter, "avatar_url": avatar_url
    }
    supabase.from_("reise_profil").insert(daten).execute()
    st.cache_data.clear()

def profil_loeschen(profil_id):
    supabase.from_("reise_profil").delete().eq("id", profil_id).execute()
    supabase.from_("nachrichten").delete().or_(f"absender_id.eq.{profil_id},empfaenger_id.eq.{profil_id}").execute()
    st.cache_data.clear()

def nachricht_senden(absender_id, empfaenger_id, text):
    zeit = datetime.now().strftime("%d.%m.%Y %H:%M")
    daten = {
        "absender_id": absender_id, "empfaenger_id": empfaenger_id,
        "nachricht": text, "zeitstempel": zeit
    }
    supabase.from_("nachrichten").insert(daten).execute()

def chat_laden(p1_id, p2_id):
    try:
        response = supabase.from_("nachrichten").select("*").or_(f"and(absender_id.eq.{p1_id},empfaenger_id.eq.{p2_id}),and(absender_id.eq.{p2_id},empfaenger_id.eq.{p1_id})").order("id").execute()
        return response.data if response.data else []
    except Exception:
        return []

# ---------------------------------------------------------
# NAVIGATION & SIDEBAR
# ---------------------------------------------------------
st.title("✈️ Travel Buddy")

is_admin = (st.session_state.user == ADMIN_EMAIL)

if is_admin:
    nav_optionen = ["🔍 Entdecken & Filtern", "🎯 Smart Partner-Matching", "👤 Mein Profil erstellen", "💬 Postfach & Live-Chat", "🛠️ Admin-Bereich", "🔐 Login / Registrierung"]
else:
    nav_optionen = ["🔍 Entdecken & Filtern", "🎯 Smart Partner-Matching", "👤 Mein Profil erstellen", "💬 Postfach & Live-Chat", "🔐 Login / Registrierung"]

menue = st.sidebar.radio("Navigation", nav_optionen)

if st.session_state.user:
    st.sidebar.success(f"Eingeloggt:\n{st.session_state.user}")
    if is_admin:
        st.sidebar.markdown("🛡️ **Admin**")
    if st.sidebar.button("Abmelden"):
        st.session_state.user = None
        st.toast("Abgemeldet.", icon="👋")
        st.rerun()
else:
    st.sidebar.info("Nicht eingeloggt.")

# ---------------------------------------------------------
# BEREICH 1: ENTDECKEN & FILTERN (HAUPTSEITE)
# ---------------------------------------------------------
if menue == "🔍 Entdecken & Filtern":
    st.header("🌍 Finde deinen perfekten Reise-Buddy")
    profile = alle_profile_laden()

    if not profile:
        st.info("Keine Profile in der Cloud.")
    else:
        col_q1, col_q2, col_q3 = st.columns(3)
        with col_q1:
            st.markdown("### 1️⃣ Mit wem?")
            filter_alter = st.slider("Altersspanne:", 18, 80, (18, 50))
            filter_charakter = st.selectbox("Charakter-Typ:", ["Alle", "Spontan & Offen", "Ruhig & Planend", "Aktiv & Sportlich", "Genießer & Entspannt"])
        with col_q2:
            st.markdown("### 2️⃣ Wohin?")
            kontinente = ["Alle"] + list(set([p.get('wunsch_kontinent', 'Europa') for p in profile if p.get('wunsch_kontinent')]))
            filter_kontinent = st.selectbox("Wunsch-Kontinent:", kontinente)
        with col_q3:
            st.markdown("### 3️⃣ Warum / Wie?")
            stile = ["Alle"] + list(set([p.get('reise_stil', 'Strand & Wellness') for p in profile if p.get('reise_stil')]))
            filter_stil = st.selectbox("Reise-Stil:", stile)

        st.markdown("---")
        st.subheader("📋 Passende Reise-Profile")

        gefilterte_profile = [p for p in profile if filter_alter[0] <= int(p.get('alter', 25)) <= filter_alter[1] and (filter_charakter == "Alle" or p.get('charakter') == filter_charakter) and (filter_kontinent == "Alle" or p.get('wunsch_kontinent') == filter_kontinent) and (filter_stil == "Alle" or p.get('reise_stil') == filter_stil)]

        if not gefilterte_profile:
            st.warning("Keine Profile gefunden, die exakt zu diesen Kriterien passen.")
        else:
            for i in range(0, len(gefilterte_profile), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(gefilterte_profile):
                        p = gefilterte_profile[i + j]
                        with cols[j]:
                            with st.container(border=True):
                                avatar_url = p.get('avatar_url', '')
                                
                                # Moderner 20:9 Container für Bild oder Platzhalter
                                if avatar_url and avatar_url.startswith('http'):
                                    st.markdown(
                                        f'''<div class="profile-card-img-container">
                                                <img src="{avatar_url}" class="profile-card-img">
                                            </div>''',
                                        unsafe_allow_html=True
                                    )
                                else:
                                    st.markdown(
                                        f'''<div class="profile-card-img-container">
                                                <span class="profile-placeholder">👤</span>
                                            </div>''',
                                        unsafe_allow_html=True
                                    )

                                st.markdown(f"**{p['name']}**, {p['alter']} Jahre")
                                st.markdown(f"🗺️ **Ziel:** {p['wunsch_land']} ({p['wunsch_kontinent']})")
                                with st.expander("Details anzeigen"):
                                    st.write(f"💬 **Über mich:** {p['profil_text']}")
                                    st.write(f"🎒 **Stil:** {p['reise_stil']}")

# ---------------------------------------------------------
# BEREICH 2: SMART PARTNER-MATCHING
# ---------------------------------------------------------
elif menue == "🎯 Smart Partner-Matching":
    st.header("🎯 Smart Match")
    profile = alle_profile_laden()
    if profile:
        profil_namen = {p['name']: p['id'] for p in profile}
        eigenes_profil_name = st.selectbox("Wer sucht?", list(profil_namen.keys()))
        eigenes_id = profil_namen[eigenes_profil_name]

        for mp in profile:
            if mp['id'] == eigenes_id: continue
            with st.expander(f"⭐ {mp['name']} ({mp['alter']} J.) – {mp['wunsch_land']}"):
                avatar_url = mp.get('avatar_url', '')
                if avatar_url and avatar_url.startswith('http'):
                    st.markdown(f'''<div style="width: 110px; height: 160px; border-radius: 8px; overflow: hidden; background: #222; display: flex; align-items: center; justify-content: center;"><img src="{avatar_url}" style="width: 100%; height: 100%; object-fit: cover; object-position: center top;"></div>''', unsafe_allow_html=True)
                st.write(f"💬 {mp['profil_text']}")

# ---------------------------------------------------------
# BEREICH 3: MEIN PROFIL ERSTELLEN
# ---------------------------------------------------------
elif menue == "👤 Mein Profil erstellen":
    st.header("👤 Profil & Zuschnitt")
    if not st.session_state.user:
        st.warning("🔐 Bitte zuerst anmelden.")
    else:
        if "step" not in st.session_state: st.session_state.step = 1
        if "p_name" not in st.session_state: st.session_state.p_name = ""
        if "p_alter" not in st.session_state: st.session_state.p_alter = 25
        if "p_cropped_img" not in st.session_state: st.session_state.p_cropped_img = None

        if st.session_state.step == 1:
            with st.form("form_s1"):
                name = st.text_input("Name:", value=st.session_state.p_name)
                alter = st.number_input("Alter:", 18, 99, int(st.session_state.p_alter))
                bild = st.file_uploader("Bild:", type=["jpg", "jpeg", "png"])
                if st.form_submit_button("Zuschnitt starten ➡️"):
                    if name and bild:
                        st.session_state.p_name = name
                        st.session_state.p_alter = alter
                        st.session_state.raw_image = Image.open(bild)
                        st.session_state.step = 1.5
                        st.rerun()
        elif st.session_state.step == 1.5:
            # Bildzuschnitt im modernen 9:20 Format (entspricht dem hochkant 20:9 Handy-Display)
            cropped = st_cropper(st.session_state.raw_image, realtime_update=True, aspect_ratio=(9, 20))
            if st.button("Übernehmen 💾"):
                st.session_state.p_cropped_img = cropped
                st.session_state.step = 2
                st.rerun()
        elif st.session_state.step == 2:
            if st.button("In Cloud speichern 🚀"):
                url = zugeschnittenes_bild_hochladen(st.session_state.p_cropped_img)
                profil_speichern(st.session_state.p_name, st.session_state.p_alter, "Reise-Bio folgt.", "Strand & Wellness", "Mittelklasse", "Ausgewogen", "Europa", "Spanien", "Spontan", url)
                st.success("Gespeichert!")
                st.session_state.step = 1
                st.rerun()

# ---------------------------------------------------------
# BEREICH 4: POSTFACH & LIVE-CHAT
# ---------------------------------------------------------
elif menue == "💬 Postfach & Live-Chat":
    st.header("💬 Postfach")

    if not st.session_state.user:
        st.warning("🔐 Bitte anmelden.")
    else:
        profile = alle_profile_laden()
        if not profile:
            st.info("Keine Profile.")
        else:
            profil_namen = {p['name']: p['id'] for p in profile}
            absender_name = st.selectbox("Mein Profil:", list(profil_namen.keys()))
            a_id = profil_namen[absender_name]

            st.markdown("---")
            col_postfach, col_chat = st.columns([1, 2])

            with col_postfach:
                st.subheader("📥 Chats")
                chatpartner_liste = [p for p in profile if p['id'] != a_id]
                if not chatpartner_liste:
                    selected_partner = None
                else:
                    partner_namen = [p['name'] for p in chatpartner_liste]
                    ausgewaehlter = st.radio("Wählen:", partner_namen)
                    selected_partner = [p for p in chatpartner_liste if p['name'] == ausgewaehlter][0]

            with col_chat:
                if not chatpartner_liste or not selected_partner:
                    st.info("Wähle links einen Chatpartner.")
                else:
                    e_id = selected_partner['id']
                    st.subheader(f"💬 Chat mit {selected_partner['name']}")
                    
                    # Nachrichten aus der Datenbank laden
                    nachrichten = chat_laden(a_id, e_id)
                    
                    # Container für den Chatverlauf (mit fester Höhe)
                    with st.container(height=400):
                        if not nachrichten:
                            st.info("Noch keine Nachrichten vorhanden. Schreib die erste Nachricht! 👋")
                        
                        for msg in nachrichten:
                            if msg['absender_id'] == a_id:
                                with st.chat_message("user", avatar="👤"):
                                    st.write(msg['nachricht'])
                                    st.caption(f"<div style='text-align: right; font-size: 0.75rem;'>{msg.get('zeitstempel', '')}</div>", unsafe_allow_html=True)
                            else:
                                with st.chat_message("assistant", avatar="✈️"):
                                    st.write(msg['nachricht'])
                                    st.caption(f"<div style='font-size: 0.75rem;'>{msg.get('zeitstempel', '')}</div>", unsafe_allow_html=True)
                            
                    # Modernes Chat-Eingabefeld am unteren Bildschirmrand
                    if prompt := st.chat_input(f"Schreibe an {selected_partner['name']}..."):
                        if prompt.strip():
                            nachricht_senden(a_id, e_id, prompt)
                            st.rerun()

# ---------------------------------------------------------
# BEREICH 5: ADMIN-BEREICH
# ---------------------------------------------------------
elif menue == "🛠️ Admin-Bereich":
    if not is_admin:
        st.error("⛔ Kein Zugriff.")
    else:
        st.header("🛠️ Admin-Bereich")
        for p in alle_profile_laden():
            if st.button(f"Löschen: {p['name']}", key=f"adm_{p['id']}"):
                profil_loeschen(p['id'])
                st.success("Gelöscht!")
                st.rerun()

# ---------------------------------------------------------
# BEREICH 6: LOGIN & REGISTRIERUNG
# ---------------------------------------------------------
elif menue == "🔐 Login / Registrierung":
    st.header("🔐 Login")
    t1, t2 = st.tabs(["Login", "Registrieren"])
    with t1:
        with st.form("login"):
            mail = st.text_input("E-Mail")
            pwd = st.text_input("Passwort", type="password")
            if st.form_submit_button("Einloggen"):
                try:
                    supabase.auth.sign_in_with_password({"email": mail, "password": pwd})
                    st.session_state.user = mail
                    st.success("Eingeloggt!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Fehler: {e}")
    with t2:
        with st.form("reg"):
            r_mail = st.text_input("E-Mail")
            r_pwd = st.text_input("Passwort", type="password")
            r_name = st.text_input("Name")
            if st.form_submit_button("Registrieren"):
                try:
                    supabase.auth.sign_up({"email": r_mail, "password": r_pwd})
                    supabase.from_("reise_profil").insert({"name": r_name, "alter": 25, "profil_text": "Neu!"}).execute()
                    st.success("Erfolgreich!")
                except Exception as e:
                    st.error(f"Fehler: {e}")