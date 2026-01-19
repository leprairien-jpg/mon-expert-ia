import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. CONFIGURATION ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("Configurez la clé API dans les Secrets.")
    st.stop()

st.set_page_config(page_title="Retouche Pro", layout="centered")

# --- 2. FIX STABILITÉ ANDROID ---
# On utilise le session_state pour garder la photo en mémoire même si le sélecteur "saute"
if 'image_fix' not in st.session_state:
    st.session_state.image_fix = None

st.title("📸 Expert Retouche Identité")

# Uploader avec gestion de cache
uploaded_file = st.file_uploader("Sélectionnez votre photo", type=['jpg', 'jpeg', 'png'])

# Si un fichier est sélectionné, on le verrouille immédiatement dans la session
if uploaded_file is not None:
    st.session_state.image_fix = uploaded_file.getvalue()

# Affichage et traitement uniquement si nous avons des données en session
if st.session_state.image_fix is not None:
    try:
        # On reconstruit l'image depuis la session pour éviter les pertes
        img_data = st.session_state.image_fix
        image = Image.open(io.BytesIO(img_data))
        
        st.image(image, caption="Photo chargée avec succès", use_container_width=True)
        
        user_text = st.text_input("Modifications (ex: blond, bijoux...)", key="input_text")

        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 GÉNÉRER", type="primary"):
                if user_text:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    instruction = f"CONSIGNE : Garde le visage à 100%. MODIFS : {user_text}. Donne le prompt positif et négatif."
                    with st.spinner("Analyse..."):
                        response = model.generate_content([instruction, image])
                        st.code(response.text)
                else:
                    st.warning("Écris tes modifs !")
        
        with col2:
            if st.button("🗑️ Effacer / Nouvelle photo"):
                st.session_state.image_fix = None
                st.rerun()

    except Exception as e:
        st.error(f"Erreur technique : {e}")
        if st.button("Réessayer"):
            st.rerun()
