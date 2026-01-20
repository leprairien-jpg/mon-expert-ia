import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. CONFIGURATION RAPIDE & CACHÉE ---
@st.cache_resource
def get_ai_model():
    # Utilisation sécurisée de la clé API via Secrets
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="Retouche Identité Pro", layout="centered")

# --- 2. LOGIQUE D'AFFICHAGE DIRECT ---
st.title("📸 Master Retouche Identité")

# On utilise l'uploader standard mais avec une lecture de bytes immédiate
uploaded_file = st.file_uploader("Sélectionnez votre photo", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    try:
        # On lit les données tout de suite pour éviter le "Connecting"
        image_data = uploaded_file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # AFFICHAGE AUTOMATIQUE : On affiche l'image dès qu'elle est lue
        st.image(image, caption="Identité source détectée", use_container_width=True)
        
        # Interface de modification
        user_text = st.text_input("Modifications (ex: blond, bijoux, plage...) :", key="mod_input")

        if st.button("🔥 GÉNÉRER LE PROMPT", type="primary"):
            if user_text:
                model = get_ai_model()
                # La consigne pour garder le visage à 100%
                instruction = f"CONSIGNE : Garde le visage à 100%. MODIFS : {user_text}. Donne le prompt positif et négatif en anglais."
                
                with st.spinner("L'IA prépare votre expertise..."):
                    response = model.generate_content([instruction, image])
                    st.markdown("### ✨ Résultat à copier :")
                    st.code(response.text, language="markdown")
            else:
                st.warning("Veuillez décrire vos changements.")
                
    except Exception as e:
        st.error(f"Erreur d'affichage : {e}")
        if st.button("🔄 Réactualiser l'envoi"):
            st.rerun()

# --- 3. MAINTENANCE ---
st.sidebar.markdown("---")
if st.sidebar.button("♻️ Nettoyer la session"):
    st.cache_data.clear()
    st.rerun()
