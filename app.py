import streamlit as st
import google.generativeai as genai
from PIL import Image

# Ta clé API
API_KEY = "AIzaSyC76UhzkSGVJ2S4IhjULgVm3HwAqkZa5ag" 
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="Prompt Master Debug", layout="centered")
st.title("🚀 Prompt Master Pro")

# --- SECTION DIAGNOSTIC ---
with st.expander("🔍 Diagnostic de ta Clé API"):
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.write("Modèles disponibles pour ta clé :", models)
        # On choisit automatiquement le meilleur modèle flash disponible
        default_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in models else models[0]
        st.success(f"Modèle auto-sélectionné : {default_model}")
    except Exception as e:
        st.error(f"Impossible de lister les modèles : {e}")
        default_model = "gemini-1.5-flash"

# --- INTERFACE ---
uploaded_file = st.file_uploader("Photo de référence", type=['jpg', 'jpeg', 'png'])
user_text = st.text_input("Concept :")

if uploaded_file and user_text:
    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)
    
    if st.button("GÉNÉRER LE PROMPT"):
        model = genai.GenerativeModel(default_model)
        try:
            prompt = f"Analyse cette image et ce texte '{user_text}' pour créer un prompt artistique détaillé."
            response = model.generate_content([prompt, image])
            st.markdown("### Résultat :")
            st.write(response.text)
        except Exception as e:
            st.error(f"Erreur de génération : {e}")
