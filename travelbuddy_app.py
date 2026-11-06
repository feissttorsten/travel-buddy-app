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

if "nav_auswahl" not in st.session_state:
    st.session_state.nav_auswahl = "Entdecken & Filtern"

if "sprache" not in st.session_state:
    st.session_state.sprache = "Deutsch"

# ---------------------------------------------------------
# ERWEITERTES SPRACH-DICTIONARY (9 SPRACHEN)
# ---------------------------------------------------------
TEXTE = {
    "Deutsch": {
        "titel": "✈️ Travel Buddy",
        "menue_titel": "📌 Menü",
        "nav_entdecken": "🔍 Entdecken & Filtern",
        "nav_matching": "🎯 Buddy-Matching",
        "nav_profil": "👤 Mein Profil erstellen",
        "nav_postfach": "💬 Postfach & Live-Chat",
        "nav_login": "🔐 Login / Registrierung",
        "nav_admin": "🛠️ Admin-Bereich",
        "suche_header": "🌍 Wer will wohin & wann?",
        "suche_sub": "Finde sofort heraus, wer im gewünschten Monat reisen möchte oder welches Ziel gerade im Fokus steht.",
        "label_monat": "📅 Wann soll es losgehen? (Reisemonat)",
        "label_land": "✈️ Wohin soll die Reise gehen? (Wunschland)",
        "expander_filter": "⚙️ Erweiterte Filter (Alter & Reisestil anzeigen)",
        "label_alter": "Altersspanne:",
        "label_stil": "Reise-Stil:",
        "ergebnis_titel": "📋 Passende Travel Buddies",
        "keine_treffer": "Keine Profile gefunden, die exakt zu dieser Kombination passen.",
        "details": "Details anzeigen",
        "ueber_mich": "💬 **Über mich:**",
        "stil": "🎒 **Stil:**",
        "ziel": "✈️ **Ziel:**",
        "geplant": "📅 **Geplant:**",
        "schnell_entdecken": "🔍 Schnellstart: Entdecken & Filtern",
        "schnell_matching": "🎯 Schnellstart: Buddy-Matching",
        "abmelden": "Abmelden",
        "eingeloggt": "Eingeloggt:",
        "nicht_eingeloggt": "Nicht eingeloggt."
    },
    "English": {
        "titel": "✈️ Travel Buddy",
        "menue_titel": "📌 Menu",
        "nav_entdecken": "🔍 Discover & Filter",
        "nav_matching": "🎯 Buddy Matching",
        "nav_profil": "👤 Create My Profile",
        "nav_postfach": "💬 Inbox & Live-Chat",
        "nav_login": "🔐 Login / Register",
        "nav_admin": "🛠️ Admin Area",
        "suche_header": "🌍 Who wants to go where & when?",
        "suche_sub": "Instantly find out who wants to travel in your desired month or which destination is currently trending.",
        "label_monat": "📅 When do you want to go? (Travel Month)",
        "label_land": "✈️ Where do you want to go? (Destination Country)",
        "expander_filter": "⚙️ Advanced Filters (Age & Travel Style)",
        "label_alter": "Age range:",
        "label_stil": "Travel style:",
        "ergebnis_titel": "📋 Matching Travel Buddies",
        "keine_treffer": "No profiles found matching this exact combination.",
        "details": "Show Details",
        "ueber_mich": "💬 **About me:**",
        "stil": "🎒 **Style:**",
        "ziel": "✈️ **Destination:**",
        "geplant": "📅 **Planned:**",
        "schnell_entdecken": "🔍 Quickstart: Discover & Filter",
        "schnell_matching": "🎯 Quickstart: Buddy Matching",
        "abmelden": "Log out",
        "eingeloggt": "Logged in:",
        "nicht_eingeloggt": "Not logged in."
    },
    "Español": {
        "titel": "✈️ Travel Buddy",
        "menue_titel": "📌 Menú",
        "nav_entdecken": "🔍 Descubrir y Filtrar",
        "nav_matching": "🎯 Coincidencia de Compañeros",
        "nav_profil": "👤 Crear mi perfil",
        "nav_postfach": "💬 Bandeja de entrada y Chat",
        "nav_login": "🔐 Iniciar sesión / Registrarse",
        "nav_admin": "🛠️ Área de Admin",
        "suche_header": "🌍 ¿Quién quiere ir a dónde y cuándo?",
        "suche_sub": "Encuentra al instante quién quiere viajar en el mes deseado.",
        "label_monat": "📅 ¿Cuándo quieres ir? (Mes de viaje)",
        "label_land": "✈️ ¿A dónde quieres ir? (País de destino)",
        "expander_filter": "⚙️ Filtros avanzados (Edad y Estilo)",
        "label_alter": "Rango de edad:",
        "label_stil": "Estilo de viaje:",
        "ergebnis_titel": "📋 Compañeros de viaje compatibles",
        "keine_treffer": "No se encontraron perfiles con esta combinación exacta.",
        "details": "Mostrar detalles",
        "ueber_mich": "💬 **Sobre mí:**",
        "stil": "🎒 **Estilo:**",
        "ziel": "✈️ **Destino:**",
        "geplant": "📅 **Planeado:**",
        "schnell_entdecken": "🔍 Inicio rápido: Descubrir",
        "schnell_matching": "🎯 Inicio rápido: Coincidencia",
        "abmelden": "Cerrar sesión",
        "eingeloggt": "Conectado:",
        "nicht_eingeloggt": "No conectado."
    },
    "Français": {
        "titel": "✈️ Travel Buddy",
        "menue_titel": "📌 Menu",
        "nav_entdecken": "🔍 Découvrir & Filtrer",
        "nav_matching": "🎯 Matching de Buddies",
        "nav_profil": "👤 Créer mon profil",
        "nav_postfach": "💬 Boîte de réception & Chat",
        "nav_login": "🔐 Connexion / Inscription",
        "nav_admin": "🛠️ Espace Admin",
        "suche_header": "🌍 Qui veut aller où et quand ?",
        "suche_sub": "Trouvez instantanément des compagnons de voyage pour votre période.",
        "label_monat": "📅 Quand partir ? (Mois de voyage)",
        "label_land": "✈️ Où aller ? (Pays de destination)",
        "expander_filter": "⚙️ Filtres avancés (Âge & Style)",
        "label_alter": "Tranche d'âge :",
        "label_stil": "Style de voyage :",
        "ergebnis_titel": "📋 Travel Buddies compatibles",
        "keine_treffer": "Aucun profil ne correspond exactement à cette combinaison.",
        "details": "Afficher les détails",
        "ueber_mich": "💬 **À propos de moi :**",
        "stil": "🎒 **Style :**",
        "ziel": "✈️ **Destination :**",
        "geplant": "📅 **Prévu :**",
        "schnell_entdecken": "🔍 Démarrage rapide : Découvrir",
        "schnell_matching": "🎯 Démarrage rapide : Matching",
        "abmelden": "Se déconnecter",
        "eingeloggt": "Connecté :",
        "nicht_eingeloggt": "Non connecté."
    },
    "中文": {
        "titel": "✈️ Travel Buddy",
        "menue_titel": "📌 菜单",
        "nav_entdecken": "🔍 发现与筛选",
        "nav_matching": "🎯 结伴匹配",
        "nav_profil": "👤 创建我的个人资料",
        "nav_postfach": "💬 消息与实时聊天",
        "nav_login": "🔐 登录 / 注册",
        "nav_admin": "🛠️ 管理员区域",
        "suche_header": "🌍 谁想去哪儿，什么时候去？",
        "suche_sub": "立即找到计划在指定月份出行或前往心仪目的地的伙伴。",
        "label_monat": "📅 何时出发？（旅行月份）",
        "label_land": "✈️ 目的地去哪里？（国家）",
        "expander_filter": "⚙️ 高级筛选（年龄与旅行风格）",
        "label_alter": "年龄范围：",
        "label_stil": "旅行风格：",
        "ergebnis_titel": "📋 匹配的旅游伙伴",
        "keine_treffer": "未找到符合此组合的个人资料。",
        "details": "显示详情",
        "ueber_mich": "💬 **关于我：**",
        "stil": "🎒 **风格：**",
        "ziel": "✈️ **目的地：**",
        "geplant": "📅 **计划时间：**",
        "schnell_entdecken": "🔍 快速开始：发现与筛选",
        "schnell_matching": "🎯 快速开始：结伴匹配",
        "abmelden": "登出",
        "eingeloggt": "已登录：",
        "nicht_eingeloggt": "未登录。"
    },
    "ไทย": {
        "titel": "✈️ Travel Buddy",
        "menue_titel": "📌 เมนู",
        "nav_entdecken": "🔍 ค้นหา & กรอง",
        "nav_matching": "🎯 จับคู่เพื่อนร่วมทริป",
        "nav_profil": "👤 สร้างโปรไฟล์ของฉัน",
        "nav_postfach": "💬 กล่องข้อความ & แชทสด",
        "nav_login": "🔐 เข้าสู่ระบบ / ลงทะเบียน",
        "nav_admin": "🛠️ พื้นที่ผู้ดูแลระบบ",
        "suche_header": "🌍 ใครต้องการไปไหนและเมื่อไหร่?",
        "suche_sub": "ค้นหาเพื่อนร่วมเดินทางในเดือนที่คุณต้องการทันที",
        "label_monat": "📅 ต้องการเดินทางเมื่อไหร่? (เดือน)",
        "label_land": "✈️ ต้องการไปที่ไหน? (ประเทศปลายทาง)",
        "expander_filter": "⚙️ ตัวกรองขั้นสูง (อายุ & สไตล์การเดินทาง)",
        "label_alter": "ช่วงอายุ:",
        "label_stil": "สไตล์การเดินทาง:",
        "ergebnis_titel": "📋 เพื่อนร่วมทริปที่ตรงกัน",
        "keine_treffer": "ไม่พบโปรไฟล์ที่ตรงกับเงื่อนไขนี้",
        "details": "แสดงรายละเอียด",
        "ueber_mich": "💬 **เกี่ยวกับฉัน:**",
        "stil": "🎒 **สไตล์:**",
        "ziel": "✈️ **จุดหมายปลายทาง:**",
        "geplant": "📅 **วางแผนไว้:**",
        "schnell_entdecken": "🔍 เริ่มต้นด่วน: ค้นหา",
        "schnell_matching": "🎯 เริ่มต้นด่วน: จับคู่",
        "abmelden": "ออกจากระบบ",
        "eingeloggt": "เข้าสู่ระบบแล้ว:",
        "nicht_eingeloggt": "ยังไม่ได้เข้าสู่ระบบ."
    },
    "日本語": {
        "titel": "✈️ Travel Buddy",
        "menue_titel": "📌 メニュー",
        "nav_entdecken": "🔍 検索 & フィルター",
        "nav_matching": "🎯 バディ・マッチング",
        "nav_profil": "👤 プロフィール作成",
        "nav_postfach": "💬 メッセージ & チャット",
        "nav_login": "🔐 ログイン / 登録",
        "nav_admin": "🛠️ 管理画面",
        "suche_header": "🌍 いつ、どこに行きたいですか？",
        "suche_sub": "希望の月や旅行先を共有しているトラベルバディをすぐに見つけられます。",
        "label_monat": "📅 出発希望月 (旅行月)",
        "label_land": "✈️ 希望の目的地 (国)",
        "expander_filter": "⚙️ 詳細フィルター (年齢 & 旅行スタイル)",
        "label_alter": "年齢層:",
        "label_stil": "旅行スタイル:",
        "ergebnis_titel": "📋 マッチングしたトラベルバディ",
        "keine_treffer": "条件に一致するプロフィールが見つかりませんでした。",
        "details": "詳細を表示",
        "ueber_mich": "💬 **自己紹介:**",
        "stil": "🎒 **スタイル:**",
        "ziel": "✈️ **目的地:**",
        "geplant": "📅 **予定時期:**",
        "schnell_entdecken": "🔍 クイックスタート: 検索",
        "schnell_matching": "🎯 クイックスタート: マッチング",
        "abmelden": "ログアウト",
        "eingeloggt": "ログイン中:",
        "nicht_eingeloggt": "未ログイン"
    },
    "Português": {
        "titel": "✈️ Travel Buddy",
        "menue_titel": "📌 Menu",
        "nav_entdecken": "🔍 Descobrir & Filtrar",
        "nav_matching": "🎯 Matching de Buddies",
        "nav_profil": "👤 Criar meu perfil",
        "nav_postfach": "💬 Caixa de entrada & Chat",
        "nav_login": "🔐 Entrar / Cadastrar",
        "nav_admin": "🛠️ Área Admin",
        "suche_header": "🌍 Quem quer ir para onde e quando?",
        "suche_sub": "Encontre instantaneamente quem quer viajar no mês desejado ou qual destino está em alta.",
        "label_monat": "📅 Quando você quer ir? (Mês de viagem)",
        "label_land": "✈️ Para onde você quer ir? (País de destino)",
        "expander_filter": "⚙️ Filtros avançados (Idade & Estilo)",
        "label_alter": "Faixa etária:",
        "label_stil": "Estilo de viagem:",
        "ergebnis_titel": "📋 Travel Buddies compatíveis",
        "keine_treffer": "Nenhum perfil encontrado com esta combinação exata.",
        "details": "Mostrar detalhes",
        "ueber_mich": "💬 **Sobre mim:**",
        "stil": "🎒 **Estilo:**",
        "ziel": "✈️ **Destino:**",
        "geplant": "📅 **Planeado:**",
        "schnell_entdecken": "🔍 Início rápido: Descobrir",
        "schnell_matching": "🎯 Início rápido: Matching",
        "abmelden": "Sair",
        "eingeloggt": "Conectado:",
        "nicht_eingeloggt": "Não conectado."
    },
    "Русский": {
        "titel": "✈️ Travel Buddy",
        "menue_titel": "📌 Меню",
        "nav_entdecken": "🔍 Поиск и фильтры",
        "nav_matching": "🎯 Подбор бадди",
        "nav_profil": "👤 Создать профиль",
        "nav_postfach": "💬 Чат и сообщения",
        "nav_login": "🔐 Вход / Регистрация",
        "nav_admin": "🛠️ Админ-панель",
        "suche_header": "🌍 Кто хочет поехать куда и когда?",
        "suche_sub": "Мгновенно находите попутчиков на нужный месяц или в желаемую страну.",
        "label_monat": "📅 Когда едем? (Месяц поездки)",
        "label_land": "✈️ Куда едем? (Страна назначения)",
        "expander_filter": "⚙️ Расширенные фильтры (возраст и стиль)",
        "label_alter": "Возрастной диапазон:",
        "label_stil": "Стиль поездки:",
        "ergebnis_titel": "📋 Подходящие Travel Buddies",
        "keine_treffer": "Профилей под данную комбинацию не найдено.",
        "details": "Показать детали",
        "ueber_mich": "💬 **О себе:**",
        "stil": "🎒 **Стиль:**",
        "ziel": "✈️ **Направление:**",
        "geplant": "📅 **План:**",
        "schnell_entdecken": "🔍 Быстрый старт: Поиск",
        "schnell_matching": "🎯 Быстрый старт: Подбор",
        "abmelden": "Выйти",
        "eingeloggt": "Вход выполнен:",
        "nicht_eingeloggt": "Не вошел."
    }
}

t = TEXTE[st.session_state.sprache]

# ---------------------------------------------------------
# CSS-OPTIMIERUNG FÜR MODERNE 20:9 SMARTPHONE-PROFILBILDER
# ---------------------------------------------------------
st.markdown("""
    <style>
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
    .profile-card-img {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover !important;
        object-position: center top !important;
    }
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
                {"name": "Anna", "alter": 28, "profil_text": "Liebe die Natur und das Meer!", "reise_stil": "Strand & Wellness", "budget": "Mittelklasse", "tempo": "Entspannt", "wunsch_kontinent": "Europa", "wunsch_land": "Spanien", "reisemonat": "April", "charakter": "Spontan & Offen", "avatar_url": ""},
                {"name": "Maximilian", "alter": 32, "profil_text": "Backpacking in Asien.", "reise_stil": "Backpacking", "budget": "Günstig", "tempo": "Actionreich", "wunsch_kontinent": "Asien", "wunsch_land": "Thailand", "reisemonat": "April", "charakter": "Aktiv & Sportlich", "avatar_url": ""},
                {"name": "Sophie", "alter": 27, "profil_text": "Städtetrips und Kultur.", "reise_stil": "Kultur & Städtetrip", "budget": "Mittelklasse", "tempo": "Ausgewogen", "wunsch_kontinent": "Europa", "wunsch_land": "Italien", "reisemonat": "Mai", "charakter": "Genießer & Entspannt", "avatar_url": ""}
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

def profil_speichern(name, alter, profil_text, reise_stil, budget, tempo, wunsch_kontinent, wunsch_land, reisemonat, charakter, avatar_url):
    daten = {
        "name": name, "alter": alter, "profil_text": profil_text,
        "reise_stil": reise_stil, "budget": budget, "tempo": tempo,
        "wunsch_kontinent": wunsch_kontinent, "wunsch_land": wunsch_land,
        "reisemonat": reisemonat, "charakter": charakter, "avatar_url": avatar_url
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
# OBERER HEADER: TITEL, SPRACHWAHL & MENÜ RECHTS OBEN
# ---------------------------------------------------------
col_title, col_lang, col_menu = st.columns([2, 1, 1])

with col_title:
    st.title(t["titel"])

with col_lang:
    sprachen_liste = ["Deutsch", "English", "Español", "Français", "中文", "ไทย", "日本語", "Português", "Русский"]
    neue_sprache = st.selectbox("🌐 Sprache", sprachen_liste, index=sprachen_liste.index(st.session_state.sprache), label_visibility="collapsed")
    if neue_sprache != st.session_state.sprache:
        st.session_state.sprache = neue_sprache
        st.rerun()

with col_menu:
    is_admin = (st.session_state.user == ADMIN_EMAIL)
    
    menue_optionen_anzeige = [
        t["nav_entdecken"], 
        t["nav_matching"], 
        t["nav_profil"], 
        t["nav_postfach"], 
        t["nav_login"]
    ]
    if is_admin:
        menue_optionen_anzeige.append(t["nav_admin"])

    mapping_umkehr = {
        t["nav_entdecken"]: "Entdecken & Filtern",
        t["nav_matching"]: "Buddy-Matching",
        t["nav_profil"]: "Mein Profil erstellen",
        t["nav_postfach"]: "Postfach & Live-Chat",
        t["nav_login"]: "Login / Registrierung",
        t["nav_admin"]: "Admin-Bereich"
    }

    aktuelle_anzeige_wahl = [k for k, v in mapping_umkehr.items() if v == st.session_state.nav_auswahl][0]

    with st.popover(t["menue_titel"]):
        st.markdown("### Navigation")
        auswahl_anzeige = st.radio("Navigation:", menue_optionen_anzeige, index=menue_optionen_anzeige.index(aktuelle_anzeige_wahl), label_visibility="collapsed")
        
        neue_interne_wahl = mapping_umkehr[auswahl_anzeige]
        if neue_interne_wahl != st.session_state.nav_auswahl:
            st.session_state.nav_auswahl = neue_interne_wahl
            st.rerun()

        st.markdown("---")
        if st.session_state.user:
            st.success(f"{t['eingeloggt']}\n{st.session_state.user}")
            if st.button(t["abmelden"]):
                st.session_state.user = None
                st.toast("Abgemeldet.", icon="👋")
                st.rerun()
        else:
            st.info(t["nicht_eingeloggt"])

menue = st.session_state.nav_auswahl

# ---------------------------------------------------------
# SCHNELLSTART-BUTTONS BEIM START
# ---------------------------------------------------------
st.markdown("---")
col_s1, col_s2 = st.columns(2)
with col_s1:
    if st.button(t["schnell_entdecken"], use_container_width=True):
        st.session_state.nav_auswahl = "Entdecken & Filtern"
        st.rerun()
with col_s2:
    if st.button(t["schnell_matching"], use_container_width=True):
        st.session_state.nav_auswahl = "Buddy-Matching"
        st.rerun()
st.markdown("---")

# ---------------------------------------------------------
# BEREICH 1: ENTDECKEN & FILTERN
# ---------------------------------------------------------
if menue == "Entdecken & Filtern":
    st.header(t["suche_header"])
    st.markdown(t["suche_sub"])
    
    profile = alle_profile_laden()

    if not profile:
        st.info("Keine Profile in der Cloud.")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            monate = ["Alle"] + list(set([p.get('reisemonat', 'April') for p in profile if p.get('reisemonat')]))
            filter_monat = st.selectbox(t["label_monat"], monate)
        with col_f2:
            laender = ["Alle"] + list(set([p.get('wunsch_land', 'Thailand') for p in profile if p.get('wunsch_land')]))
            filter_land = st.selectbox(t["label_land"], laender)

        with st.expander(t["expander_filter"]):
            col_q1, col_q2 = st.columns(2)
            with col_q1:
                filter_alter = st.slider(t["label_alter"], 18, 80, (18, 50))
            with col_q2:
                stile = ["Alle"] + list(set([p.get('reise_stil', 'Strand & Wellness') for p in profile if p.get('reise_stil')]))
                filter_stil = st.selectbox(t["label_stil"], stile)

        st.markdown("---")
        st.subheader(t["ergebnis_titel"])

        gefilterte_profile = [
            p for p in profile 
            if (filter_monat == "Alle" or p.get('reisemonat') == filter_monat) and
               (filter_land == "Alle" or p.get('wunsch_land') == filter_land) and
               (filter_alter[0] <= int(p.get('alter', 25)) <= filter_alter[1]) and
               (filter_stil == "Alle" or p.get('reise_stil') == filter_stil)
        ]

        if not gefilterte_profile:
            st.warning(t["keine_treffer"])
        else:
            for i in range(0, len(gefilterte_profile), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(gefilterte_profile):
                        p = gefilterte_profile[i + j]
                        with cols[j]:
                            with st.container(border=True):
                                avatar_url = p.get('avatar_url', '')
                                if avatar_url and avatar_url.startswith('http'):
                                    st.markdown(f'''<div class="profile-card-img-container"><img src="{avatar_url}" class="profile-card-img"></div>''', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'''<div class="profile-card-img-container"><span class="profile-placeholder">👤</span></div>''', unsafe_allow_html=True)

                                st.markdown(f"**{p['name']}**, {p['alter']} Jahre")
                                st.markdown(f"{t['ziel']} {p.get('wunsch_land', 'Offen')} ({p.get('wunsch_kontinent', 'Weltweit')})")
                                st.markdown(f"{t['geplant']} {p.get('reisemonat', 'Flexibel')}")
                                
                                with st.expander(t["details"]):
                                    st.write(f"{t['ueber_mich']} {p['profil_text']}")
                                    st.write(f"{t['stil']} {p['reise_stil']}")

# ---------------------------------------------------------
# BEREICH 2: BUDDY-MATCHING
# ---------------------------------------------------------
elif menue == "Buddy-Matching":
    st.header("🎯 Buddy-Matching")
    profile = alle_profile_laden()
    if profile:
        profil_namen = {p['name']: p['id'] for p in profile}
        eigenes_profil_name = st.selectbox("Wer sucht?", list(profil_namen.keys()))
        eigenes_id = profil_namen[eigenes_profil_name]

        for mp in profile:
            if mp['id'] == eigenes_id: continue
            with st.expander(f"⭐ {mp['name']} ({mp['alter']} J.) – {mp.get('wunsch_land', 'Weltweit')} im {mp.get('reisemonat', 'Flexibel')}"):
                avatar_url = mp.get('avatar_url', '')
                if avatar_url and avatar_url.startswith('http'):
                    st.markdown(f'''<div style="width: 110px; height: 160px; border-radius: 8px; overflow: hidden; background: #222; display: flex; align-items: center; justify-content: center;"><img src="{avatar_url}" style="width: 100%; height: 100%; object-fit: cover; object-position: center top;"></div>''', unsafe_allow_html=True)
                st.write(f"💬 {mp['profil_text']}")

# ---------------------------------------------------------
# BEREICH 3: MEIN PROFIL ERSTELLEN
# ---------------------------------------------------------
elif menue == "Mein Profil erstellen":
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
                reise_monat = st.selectbox("Wunsch-Reisemonat:", ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"])
                wunsch_land = st.text_input("Wunsch-Reiseziel (Land):", "Thailand")
                bild = st.file_uploader("Bild:", type=["jpg", "jpeg", "png"])
                if st.form_submit_button("Zuschnitt starten ➡️"):
                    if name and bild:
                        st.session_state.p_name = name
                        st.session_state.p_alter = alter
                        st.session_state.p_reisemonat = reise_monat
                        st.session_state.p_wunschland = wunsch_land
                        st.session_state.raw_image = Image.open(bild)
                        st.session_state.step = 1.5
                        st.rerun()
        elif st.session_state.step == 1.5:
            cropped = st_cropper(st.session_state.raw_image, realtime_update=True, aspect_ratio=(9, 20))
            if st.button("Übernehmen 💾"):
                st.session_state.p_cropped_img = cropped
                st.session_state.step = 2
                st.rerun()
        elif st.session_state.step == 2:
            if st.button("In Cloud speichern 🚀"):
                url = zugeschnittenes_bild_hochladen(st.session_state.p_cropped_img)
                profil_speichern(
                    st.session_state.p_name, 
                    st.session_state.p_alter, 
                    "Reise-Bio folgt.", 
                    "Strand & Wellness", 
                    "Mittelklasse", 
                    "Ausgewogen", 
                    "Asien", 
                    st.session_state.get('p_wunschland', 'Thailand'), 
                    st.session_state.get('p_reisemonat', 'April'), 
                    "Spontan", 
                    url
                )
                st.success("Gespeichert!")
                st.session_state.step = 1
                st.rerun()

# ---------------------------------------------------------
# BEREICH 4: POSTFACH & INTERAKTIVER LIVE-CHAT
# ---------------------------------------------------------
elif menue == "Postfach & Live-Chat":
    st.header("💬 Postfach & Live-Chat")

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
                    
                    # 1. Interaktive Eisbrecher-Fragen (Feature 1)
                    st.markdown("💡 **Eisbrecher (Klick zum Senden):**")
                    b1, b2, b3 = st.columns(3)
                    if b1.button("🏖️ Strand oder Städtetrip?"):
                        nachricht_senden(a_id, e_id, "Hey! 👋 Strandurlaub oder lieber Städtetrip?")
                        st.rerun()
                    if b2.button("🎒 Hostel oder Hotel?"):
                        nachricht_senden(a_id, e_id, "Hi! Bist du eher Team Hostel & Backpacker oder Hotel & Komfort?")
                        st.rerun()
                    if b3.button("🗺️ Wohin als nächstes?"):
                        nachricht_senden(a_id, e_id, "Hey! Welches Reiseziel steht ganz oben auf deiner Liste?")
                        st.rerun()

                    st.markdown("---")

                    # Nachrichten laden (mit st.fragment für automatisches Refresh/Live-Chat - Feature 4)
                    @st.fragment(run_every=5)
                    def chat_fenster_anzeigen():
                        nachrichten = chat_laden(a_id, e_id)
                        
                        with st.container(height=350):
                            if not nachrichten:
                                st.info("Noch keine Nachrichten vorhanden. Schreib die erste Nachricht! 👋")
                            
                            for msg in nachrichten:
                                if msg['absender_id'] == a_id:
                                    with st.chat_message("user", avatar="👤"):
                                        st.write(msg['nachricht'])
                                        st.caption(f"<div style='text-align: right; font-size: 0.75rem;'>{msg.get('zeitstempel', '')} ✓✓</div>", unsafe_allow_html=True)
                                else:
                                    with st.chat_message("assistant", avatar="✈️"):
                                        st.write(msg['nachricht'])
                                        st.caption(f"<div style='font-size: 0.75rem;'>{msg.get('zeitstempel', '')}</div>", unsafe_allow_html=True)

                    chat_fenster_anzeigen()

                    # 2. Quick Replies / Schnellantworten (Feature 2)
                    st.markdown("⚡ **Schnellantworten:**")
                    qr1, qr2, qr3, qr4 = st.columns(4)
                    if qr1.button("Passt perfekt! 👍"):
                        nachricht_senden(a_id, e_id, "Passt perfekt! 👍")
                        st.rerun()
                    if qr2.button("Lass uns telefonieren 📞"):
                        nachricht_senden(a_id, e_id, "Lass uns am besten mal kurz telefonieren oder schreiben! 📞")
                        st.rerun()
                    if qr3.button("Welches Datum? 📅"):
                        nachricht_senden(a_id, e_id, "Welches Datum genau hattest du im Kopf? 📅")
                        st.rerun()
                    if qr4.button("Bin dabei! 🚀"):
                        nachricht_senden(a_id, e_id, "Bin absolut dabei! 🚀")
                        st.rerun()

                    # 3. Mini-Umfrage direkt im Chat starten (Feature 3)
                    with st.expander("📊 Mini-Umfrage im Chat starten"):
                        umfrage_frage = st.selectbox("Thema:", ["Reiseziel: Thailand vs. Bali", "Unterkunft: Hostel vs. Hotel", "Reisetempo: Entspannt vs. Actionreich"])
                        if st.button("Umfrage abschicken 🗳️"):
                            nachricht_senden(a_id, e_id, f"📊 **Mini-Umfrage gestartet:** {umfrage_frage} (Stimmt ab!)")
                            st.success("Umfrage gesendet!")
                            st.rerun()

                    # Eingabefeld am unteren Bildschirmrand
                    if prompt := st.chat_input(f"Schreibe an {selected_partner['name']}..."):
                        if prompt.strip():
                            nachricht_senden(a_id, e_id, prompt)
                            st.rerun()

# ---------------------------------------------------------
# BEREICH 5: ADMIN-BEREICH
# ---------------------------------------------------------
elif menue == "Admin-Bereich":
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
elif menue == "Login / Registrierung":
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
                    supabase.from_("reise_profil").insert({"name": r_name, "alter": 25, "reisemonat": "April", "wunsch_land": "Thailand", "profil_text": "Neu!"}).execute()
                    st.success("Erfolgreich!")
                except Exception as e:
                    st.error(f"Fehler: {e}")
