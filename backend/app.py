import streamlit as st
import psycopg2
from datetime import datetime
import pandas as pd

# ================= CONFIG =================
DB_NAME = st.secrets["DB_NAME"]
DB_USER = st.secrets["DB_USER"]
DB_PASS = st.secrets["DB_PASS"]
DB_HOST = st.secrets["DB_HOST"]
DB_PORT = "5432"

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# ================= BACKGROUND GLOBAL =================
def set_bg():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1600&q=80");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }

        .block-container {
            background-color: rgba(0, 0, 0, 0.7);
            padding: 2rem;
            border-radius: 15px;
        }

        h1, h2, h3, p, label {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# appliquer le fond partout
set_bg()

# ================= MENU (SANS IMAGES) =================
MENU = {
    "Koki + Banane": 2000,
    "Eru": 2500,
    "Okok + Manioc": 2200,
    "Riz + Poulet": 3000,
    "Riz sauté + Poulet": 3500,
    "Ndole": 1800,
    "Banane malaxée": 2800,
    "Taro + Sauce jaune": 4000
}

# ================= DB =================
def get_conn():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
        sslmode="require"
    )

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS commandes(
        id SERIAL PRIMARY KEY,
        nom TEXT,
        prenom TEXT,
        localisation TEXT,
        plat TEXT,
        quantite INTEGER,
        prix INTEGER,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= NAVIGATION =================
if "page" not in st.session_state:
    st.session_state.page = "home"

# ================= HOME =================
def home():
    st.title("🍔 K-MERFOOD")
    st.subheader("Nos plats")

    for plat, prix in MENU.items():
        st.markdown(f"### 🍽️ {plat}")
        st.write(f"💰 {prix} FCFA")

    st.divider()

    col1, col2, col3 = st.columns(3)

    if col1.button("🛒 Commander"):
        st.session_state.page = "commande"

    if col2.button("🔐 Admin"):
        st.session_state.page = "login"

    if col3.button("📊 Analyse"):
        st.session_state.page = "analyse"

# ================= COMMANDE =================
def commande():
    st.title("🛒 Commander")

    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    loc = st.text_input("Localisation")

    plat = st.selectbox("Plat", list(MENU.keys()))
    qte = st.number_input("Quantité", min_value=1)

    if st.button("Valider"):
        if not nom or not prenom or not loc:
            st.warning("Remplis tous les champs")
            return

        prix = MENU[plat] * qte

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO commandes(nom,prenom,localisation,plat,quantite,prix,created_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            nom, prenom, loc, plat, qte, prix,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

        st.success("Commande enregistrée ✅")

    if st.button("⬅ Retour"):
        st.session_state.page = "home"

# ================= LOGIN =================
def login():
    st.title("🔐 Admin")

    u = st.text_input("Utilisateur")
    p = st.text_input("Mot de passe", type="password")

    if st.button("Connexion"):
        if u == ADMIN_USER and p == ADMIN_PASS:
            st.session_state.page = "dashboard"
        else:
            st.error("Accès refusé")

    if st.button("⬅ Retour"):
        st.session_state.page = "home"

# ================= DASHBOARD =================
def dashboard():
    st.title("📊 Dashboard")

    conn = get_conn()
    df = pd.read_sql("SELECT * FROM commandes", conn)
    conn.close()

    if df.empty:
        st.warning("Aucune donnée")
        return

    st.metric("Total commandes", len(df))
    st.metric("Chiffre total", int(df["prix"].sum()))

    st.dataframe(df)

    if st.button("⬅ Retour"):
        st.session_state.page = "home"

# ================= ANALYSE =================
def analyse():
    st.title("📊 Analyse")

    conn = get_conn()
    df = pd.read_sql("SELECT * FROM commandes", conn)
    conn.close()

    if not df.empty:
        df["date"] = pd.to_datetime(df["created_at"]).dt.date
        st.bar_chart(df.groupby("date")["prix"].sum())

    if st.button("⬅ Retour"):
        st.session_state.page = "home"

# ================= ROUTER =================
if st.session_state.page == "home":
    home()
elif st.session_state.page == "commande":
    commande()
elif st.session_state.page == "login":
    login()
elif st.session_state.page == "dashboard":
    dashboard()
elif st.session_state.page == "analyse":
    analyse()
