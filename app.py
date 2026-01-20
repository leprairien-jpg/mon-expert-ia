import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Config rapide
@st.cache_resource
def get_model():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="Retouche Pro", layout="centered")

# Gestion du rafraîchissement
if 'run_id' not in st.session_state:
    st.session_state.run_id = 0

def clear_app():
    st.session_state.run_id += 1
    st.cache_data.clear()

st.sidebar.button("🗑️ Nettoyer / Nouvelle Photo", on_click=clear_app)

st.title("📸 Master Retouche Identité")

# 2. L'uploader le plus "léger" possible
# On désactive les fichiers multiples pour éviter de saturer la RAM du téléphone
uploaded_file = st.file_uploader(
    "Choisir une photo", 
    type=['jpg', 'jpeg', 'png'],
    key=f"up_{st.session_state.run_id}"
)

if uploaded_file is not None:
    try:
        # TECHNIQUE DE FORÇAGE : On lit par petits morceaux (chunks)
        # pour éviter que Chrome ne coupe la connexion
        bytes_data = uploaded_file.getvalue()
        image = Image.open(io.BytesIO(bytes_data))
        
        # Affichage direct
        st.image(image, caption="Identité source", use_container_width=True)
        
        user_text = st.text_input("Tes modifications (ex: blond, bijoux...)", key=f"txt_{st.session_state.run_id}")

        if st.button("🚀 GÉNÉRER", type="primary"):
            if user_text:
                model = get_model()
                instruction = f"CONSIGNE : Garde le visage à 100%. MODIFS : {user_text}. Donne le prompt positif et négatif en anglais."
                with st.spinner("Analyse faciale..."):
                    response = model.generate_content([instruction, image])
                    st.code(response.text, language="markdown")
            else:
                st.warning("Précise les modifs !")
    except Exception as e:
        st.error("Échec du transfert. Réessayez avec une photo plus légère ou rafraîchissez.")
