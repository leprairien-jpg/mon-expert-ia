import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Sécurisation de la Clé API via les Secrets Streamlit
if "AIzaSyC76UhzkSGVJ2S4IhjULgVm3HwAqkZa5ag" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Clé API manquante dans les Secrets !")

st.set_page_config(page_title="Prompt Master Pro", layout="centered")

st.title("🚀 Prompt Master Engineering")

# 2. Zone d'upload avec retour visuel immédiat
uploaded_file = st.file_uploader("Choisissez une photo de référence", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # On charge l'image en mémoire pour s'assurer qu'elle est valide
    image = Image.open(uploaded_file)
    
    # AFFICHAGE DE LA PHOTO (C'est cette partie qui manquait peut-être de robustesse)
    st.image(image, caption="Image chargée avec succès", use_container_width=True)
    
    user_text = st.text_input("Votre concept de base :", placeholder="Ex: Un guerrier cyberpunk...")

    if st.button("GÉNÉRER L'EXPERTISE", type="primary"):
        if user_text:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Système d'instruction pour l'IA
            instruction = """Tu es un Ingénieur Expert. Analyse l'image et le texte. 
            Donne moi :
            PROMPT_ULTIME_POSITIF: (Description technique complète)
            PROMPT_ULTIME_NÉGATIF: (Éléments à bannir)"""
            
            with st.spinner("Analyse technique en cours..."):
                try:
                    # Envoi à l'IA
                    response = model.generate_content([instruction, image, user_text])
                    
                    st.success("Analyse terminée !")
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Erreur lors de l'analyse : {e}")
        else:
            st.warning("Veuillez saisir un concept de base.")
