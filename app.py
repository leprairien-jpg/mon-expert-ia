import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. CONFIGURATION ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("Configurez la clé API dans les Secrets.")
    st.stop()

st.set_page_config(page_title="Retouche Pro Multimodale", layout="centered")

# Initialisation de la mémoire tampon pour les photos
if 'gallery' not in st.session_state:
    st.session_state.gallery = []

st.title("📸 Expert Retouche & Identité")

# --- 2. SYSTÈME DE SÉLECTION AMÉLIORÉ ---
# 'accept_multiple_files' stabilise le sélecteur Android
uploaded_files = st.file_uploader(
    "Accéder à votre bibliothèque", 
    type=['jpg', 'jpeg', 'png'], 
    accept_multiple_files=True
)

if uploaded_files:
    # On stocke les fichiers dans la session pour éviter les pertes de connexion mobile
    st.session_state.gallery = uploaded_files

# --- 3. AFFICHAGE ET TRAITEMENT ---
if st.session_state.gallery:
    # On affiche la dernière photo sélectionnée (ou on peut faire une boucle)
    last_file = st.session_state.gallery[-1]
    
    try:
        image = Image.open(last_file)
        st.image(image, caption=f"Cible : {last_file.name}", use_container_width=True)
        
        user_text = st.text_input("Modifications souhaitées (Visage intouchable) :")

        if st.button("🚀 GÉNÉRER L'INGÉNIERIE", type="primary"):
            if user_text:
                model = genai.GenerativeModel('gemini-2.5-flash')
                instruction = f"""
                Tu es un expert en Face Consistency. 
                Garde le visage EXACT de cette personne. 
                Applique ces retouches : {user_text}. 
                Génère un PROMPT_ULTIME_POSITIF et NÉGATIF en anglais.
                """
                with st.spinner("Analyse faciale..."):
                    response = model.generate_content([instruction, image])
                    st.code(response.text)
            else:
                st.warning("Veuillez décrire vos retouches.")

    except Exception as e:
        st.error(f"Erreur d'accès à la bibliothèque : {e}")

    if st.button("🗑️ Vider la sélection"):
        st.session_state.gallery = []
        st.rerun()
