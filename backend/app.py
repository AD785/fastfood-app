import streamlit as st
import psycopg2
from datetime import datetime
import pandas as pd
import os

# ================= CONFIG =================
DB_NAME = st.secrets["DB_NAME"]
DB_USER = st.secrets["DB_USER"]
DB_PASS = st.secrets["DB_PASS"]
DB_HOST = st.secrets["DB_HOST"]
DB_PORT = "5432"

ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# ================= IMAGE SAFE =================
def safe_image(path):
    if os.path.exists(path):
        return path
    return "https://via.placeholder.com/300?text=Image+indisponible"

# ================= MENU =================
MENU = {
    'Koki + Banane': (2000, 'https://www.facebook.com/100070331942704/posts/2669937416563027/?locale=fr_FR'),
    'Eru': (2500, 'image.jpg/image2.jpeg'),
    'Okok + Tubercule de Manioc': (2200, 'image.jpg/image3.jpeg'),
    'Riz + Poulet + Sauce': (3000, 'image.jpg/image4.jpeg'),
    'Riz Sauté + Poulet Braisé': (3500, 'image.jpg/image5.jpeg'),
    'Ndole': (1800, 'image.jpg/image6.jpg'),
    'Banane Malaxé': (2800, 'image.jpg/image7.jpeg'),
    'Taro + Sauce Jaune': (4000, 'image.jpg/image8.jpg'),
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
            st.image(safe_image(img), use_container_width=True)
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

    st.image(safe_image(MENU[plat][1]), width=300)

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
