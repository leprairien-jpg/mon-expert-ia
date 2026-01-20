import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. CONFIGURATION ---
@st.cache_resource
def load_model():
    # Utilisation sécurisée via Secrets
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="Retouche Pro Identité", layout="centered")

# --- 2. LOGIQUE DE NETTOYAGE (FIX) ---
# On crée une clé unique pour l'uploader basée sur le session_state
if 'clear_key' not in st.session_state:
    st.session_state.clear_key = 0

def full_cleanup():
    # On change la clé pour forcer Streamlit à recréer le widget
    st.session_state.clear_key += 1
    # On vide les fichiers en cache
    st.cache_data.clear()

# Barre latérale avec le bouton corrigé
with st.sidebar:
    st.title("Options")
    if st.button("🗑️ Nettoyer l'App", on_click=full_cleanup):
        st.success("Application réinitialisée")

# --- 3. INTERFACE PRINCIPALE ---
st.title("📸 Master Retouche Identité")

# Utilisation de la clé dynamique pour l'uploader
uploaded_file = st.file_uploader(
    "Sélectionnez votre photo", 
    type=['jpg', 'jpeg', 'png'],
    key=f"uploader_{st.session_state.clear_key}"
)

if uploaded_file is not None:
    try:
        # Lecture robuste des octets
        raw_data = uploaded_file.getvalue()
        image = Image.open(io.BytesIO(raw_data))
        
        # Affichage direct
        st.image(image, caption="Photo source verrouillée", use_container_width=True)
        
        user_text = st.text_input("Tes modifications (ex: blond, bijoux, plage...) :", key=f"text_{st.session_state.clear_key}")

        if st.button("🚀 GÉNÉRER LE PROMPT", type="primary"):
            if user_text:
                model = load_model()
                # Instruction de Face Consistency
                instruction = f"CONSIGNE : Garde le visage à 100%. MODIFS : {user_text}. Donne le prompt positif et négatif en anglais."
                
                with st.spinner("Analyse faciale..."):
                    response = model.generate_content([instruction, image])
                    st.code(response.text, language="markdown")
            else:
                st.warning("Précise ce que tu veux changer.")
                
    except Exception as e:
        st.error("Erreur de flux. Utilisez le bouton 'Nettoyer' à gauche.")
