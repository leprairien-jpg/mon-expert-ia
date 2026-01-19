import streamlit as st
import google.generativeai as genai
from PIL import Image

# CONFIGURATION SÉCURISÉE
# Note : Sur GitHub, utilise st.secrets pour ne pas afficher ta clé publiquement
API_KEY = "AIzaSyC76UhzkSGVJ2S4IhjULgVm3HwAqkZa5ag" 
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="Prompt Master Pro", layout="centered")

st.title("🚀 Prompt Master Engineering")

# Zone d'upload
uploaded_file = st.file_uploader("Choisissez une photo de référence", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # Lecture et affichage immédiat de l'image
    image = Image.open(uploaded_file)
    st.image(image, caption="Image source détectée", use_container_width=True)
    
    user_text = st.text_input("Votre concept de base :", placeholder="Ex: Un paysage cyberpunk...")

    if st.button("GÉNÉRER L'EXPERTISE", type="primary"):
        if user_text:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Ton instruction de Maître Ingénieur
            instruction = """Tu es un Maître Ingénieur en Prompt Multimodal. 
            Analyse l'IMAGE et le TEXTE pour générer :
            1. PROMPT_ULTIME_POSITIF : Ultra-détaillé, technique (optique, lumière, style).
            2. PROMPT_ULTIME_NÉGATIF : Liste d'erreurs à éviter.
            Sois précis et professionnel."""
            
            with st.spinner("L'IA analyse votre image..."):
                try:
                    response = model.generate_content([instruction, image, user_text])
                    st.success("Analyse terminée !")
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Erreur technique : {e}")
        else:
            st.warning("Ajoutez un texte pour guider l'IA.")
