import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Ta Clé API
API_KEY = "AIzaSyC76UhzkSGVJ2S4IhjULgVm3HwAqkZa5ag" 
genai.configure(api_key=API_KEY)

# 2. Les instructions de l'Expert
SYSTEM_INSTRUCTION = "Tu es un Maître Ingénieur en Prompt. Analyse l'image et le texte pour créer un PROMPT_ULTIME_POSITIF (détaillé, technique) et un PROMPT_ULTIME_NÉGATIF (erreurs à éviter)."

st.set_page_config(page_title="Prompt Master", layout="wide")
st.title("🎨 Prompt Master App")

# 3. L'Interface
img_file = st.file_uploader("Charge ton image de référence", type=['jpg', 'png', 'jpeg'])
user_text = st.text_input("Ton idée de base", "Un paysage futuriste")

if st.button("Générer l'ingénierie"):
    if img_file and user_text:
        img = Image.open(img_file)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        with st.spinner("L'expert travaille..."):
            response = model.generate_content([SYSTEM_INSTRUCTION, img, user_text])
            st.markdown(response.text)
    else:
        st.error("Ajoute une image et un texte !")
