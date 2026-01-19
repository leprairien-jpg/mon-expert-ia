import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. SÉCURITÉ ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("❌ Erreur : GEMINI_API_KEY non configurée.")
    st.stop()

st.set_page_config(page_title="Retouche Haute Fidélité", layout="centered")

# --- 2. LOGIQUE DE CHARGEMENT FORCÉ ---
# Cette astuce permet de vider le cache si une nouvelle photo est choisie
if 'file_uploader_key' not in st.session_state:
    st.session_state['file_uploader_key'] = 0

def reset_uploader():
    st.session_state['file_uploader_key'] += 1

st.title("📸 Expert Retouche & Consistance")

# Uploader avec une clé dynamique pour forcer la prise en compte immédiate
uploaded_file = st.file_uploader(
    "Sélectionnez votre photo", 
    type=['jpg', 'jpeg', 'png'],
    key=st.session_state['file_uploader_key']
)

if uploaded_file:
    # On force la lecture immédiate des octets pour Android
    try:
        image = Image.open(uploaded_file)
        # On affiche tout de suite pour confirmer le chargement
        st.image(image, caption="Identité source verrouillée", use_container_width=True)
        
        user_text = st.text_area("🔧 Modifications (Fond, cheveux, accessoires...)", 
                                 placeholder="Décrivez les changements ici en gardant le visage intact.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 GÉNÉRER LE PROMPT", type="primary"):
                if user_text:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    instruction = f"""
                    Tu es un expert en 'Face Consistency'. 
                    PROMPT SYSTEM : Garde le visage EXACT de l'image (structure, traits). 
                    MODIFICATIONS : {user_text}.
                    Génère un PROMPT_ULTIME_POSITIF et NÉGATIF ultra-détaillé en anglais.
                    """
                    
                    with st.spinner("Analyse faciale..."):
                        response = model.generate_content([instruction, image])
                        st.markdown("### ✨ Résultat")
                        st.code(response.text, language="markdown")
                else:
                    st.warning("Précisez les modifications.")
        
        with col2:
            if st.button("🔄 Changer de photo"):
                reset_uploader()
                st.rerun()

    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
