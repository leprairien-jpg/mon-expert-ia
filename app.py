import streamlit as st
import google.generativeai as genai
from PIL import Image

# Ta clé API
API_KEY = "AIzaSyC76UhzkSGVJ2S4IhjULgVm3HwAqkZa5ag" 

# Configuration de l'API avec la version stable
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="Prompt Master Pro", layout="centered")
st.title("🚀 Prompt Master Engineering")

uploaded_file = st.file_uploader("Choisissez une photo", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Image source", use_container_width=True)
    
    user_text = st.text_input("Concept :", placeholder="Ex: Cyberpunk city")

    if st.button("GÉNÉRER"):
        if user_text:
            # On utilise ici le nom de modèle le plus standard
            # Si 'gemini-1.5-flash' échoue, 'gemini-pro-vision' est l'ancien standard
            model_name = 'gemini-1.5-flash' 
            
            model = genai.GenerativeModel(model_name)
            
            instruction = "Tu es un Maître Ingénieur en Prompt. Analyse l'image et le texte pour créer un PROMPT_ULTIME_POSITIF et un PROMPT_ULTIME_NÉGATIF."
            
            with st.spinner(f"Analyse avec {model_name}..."):
                try:
                    # Tentative de génération
                    response = model.generate_content([instruction, image, user_text])
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Erreur avec {model_name} : {e}")
                    st.info("Essai du modèle alternatif...")
                    # Tentative de secours (Fallback)
                    try:
                        alt_model = genai.GenerativeModel('gemini-pro-vision')
                        response = alt_model.generate_content([instruction, image, user_text])
                        st.markdown(response.text)
                    except Exception as e2:
                        st.error("Tous les modèles ont échoué. Vérifiez vos restrictions de clé API dans Google AI Studio.")
