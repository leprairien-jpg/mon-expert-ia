import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- CONFIGURATION SÉCURISÉE ---
try:
    # On récupère la clé dans les Secrets de Streamlit pour éviter le ban Google
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("❌ Erreur : GEMINI_API_KEY non trouvée dans les Secrets Streamlit.")
    st.stop()

st.set_page_config(page_title="Prompt Master Pro", layout="centered")
st.title("🚀 Prompt Master Engineering")

# --- INTERFACE ---
uploaded_file = st.file_uploader("Choisissez une photo", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    try:
        # Lecture directe pour affichage immédiat
        image_bytes = uploaded_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        st.image(image, caption="Image source chargée", use_container_width=True)
        
        user_text = st.text_input("Concept (ex: blond, bijoux, plage...) :")

        if st.button("GÉNÉRER"):
            if user_text:
                # Utilisation du modèle 2.5 Flash détecté sur ta session
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Consigne stricte pour la ressemblance
                instruction = f"""
                Tu es un Maître Ingénieur en Prompt. 
                CONSIGNE CRITIQUE : Garde le visage EXACT de la personne sur la photo, sans aucune déformation.
                MODIFICATIONS : {user_text}.
                Génère un PROMPT_ULTIME_POSITIF et un PROMPT_ULTIME_NÉGATIF en anglais pour Midjourney/Flux.
                """
                
                with st.spinner("Analyse faciale en cours..."):
                    # On repasse l'image et le texte à l'IA
                    response = model.generate_content([instruction, image])
                    st.markdown("### ✨ Résultat :")
                    # Bloc de code avec bouton de copie intégré
                    st.code(response.text, language="markdown")
            else:
                st.warning("Veuillez saisir un concept.")
                
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        if st.button("Réessayer"):
            st.rerun()

# --- SIDEBAR DE NETTOYAGE ---
st.sidebar.title("Maintenance")
if st.sidebar.button("♻️ Réinitialiser l'App"):
    st.cache_data.clear()
    st.rerun()
