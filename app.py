import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Configuration (Utilise tes Secrets Streamlit pour la clé)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("Ajoute ta clé dans les Secrets !")
    st.stop()

st.title("📸 Retouche Identité")

# 2. L'Uploader le plus basique (plus robuste sur mobile)
uploaded_file = st.file_uploader("Choisir une photo", type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    # On affiche l'image DIRECTEMENT sans passer par des variables complexes
    st.image(uploaded_file, use_container_width=True)
    
    user_text = st.text_input("Modifications (ex: blond, plage...)")

    if st.button("GÉNÉRER LE PROMPT", type="primary"):
        if user_text:
            # On convertit en objet Image seulement au moment de l'envoi à l'IA
            img = Image.open(uploaded_file)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            instruction = f"Garde le visage exact. Applique ces changements : {user_text}. Donne un prompt positif et négatif en anglais."
            
            with st.spinner("Analyse..."):
                response = model.generate_content([instruction, img])
                st.code(response.text)
