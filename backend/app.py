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

# ================= BACKGROUND =================
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
            background-color: rgba(0, 0, 0, 0.65);
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

# ================= MENU =================
MENU = {
    "Koki + Banane": (2000, "https://images.unsplash.com/photo-1604908176997-4319b60c2f3c?auto=format&fit=crop&w=600&q=80"),
    "Eru": (2500, "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80"),
    "Okok + Manioc": (2200, "https://images.unsplash.com/photo-1600891964599-f61ba0e24092?auto=format&fit=crop&w=600&q=80"),
    "Riz + Poulet": (3000, "https://images.unsplash.com/photo-1604908554007-9f5bfa2b4c5b?auto=format&fit=crop&w=600&q=80"),
    "Riz sauté + Poulet": (3500, "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=600&q=80"),
    "Ndole": (1800, "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=600&q=80"),
    "Banane malaxée": (2800, "https://images.unsplash.com/photo-1589302168068-964664d93dc0?auto=format&fit=crop&w=600&q=80"),
    "Taro + Sauce jaune": (4000, "https://images.unsplash.com/photo-1604908177522-402be3e38c60?auto=format&fit=crop&w=600&q=80")
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

    cols = st.columns(4)

    for i, (plat, (prix, img)) in enumerate(MENU.items()):
        with cols[i % 4]:
            st.image(img, use_container_width=True)
            st.markdown(f"**{plat}**")
            st.write(f"{prix} FCFA")

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

    st.image(MENU[plat][1], width=300)

    if st.button("Valider"):
        if not nom or not prenom or not loc:
            st.warning("Remplis tous les champs")
            return

        prix = MENU[plat][0] * qte

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
    set_bg()

    st.title("🔐 Admin Login")

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
