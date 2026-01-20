import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. INITIALISATION SILENCIEUSE
if 'app_ready' not in st.session_state:
    st.session_state.app_ready = False

# Configuration via Secrets
try:
    if not st.session_state.app_ready:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        st.session_state.app_ready = True
except Exception:
    st.error("⚠️ Configurer la clé API dans les Secrets Streamlit.")
    st.stop()

st.set_page_config(page_title="Retouche Pro Instantanée", layout="centered")

# 2. LOGIQUE D'UPLOAD DIRECT
st.title("📸 Master Retouche Identité")

# On utilise un conteneur pour éviter les sauts d'affichage
main_placeholder = st.container()

with main_placeholder:
    # accept_multiple_files=False est plus stable pour le téléchargement direct
    uploaded_file = st.file_uploader("Sélectionner une photo", type=['jpg', 'jpeg', 'png'])

    if uploaded_file is not None:
        try:
            # MÉTHODE RADICALE : On convertit tout de suite en Bytes pour stabiliser
            image_bytes = uploaded_file.getvalue()
            img = Image.open(io.BytesIO(image_bytes))
            
            # Affichage immédiat
            st.image(img, caption="Prêt pour l'analyse", use_container_width=True)
            
            user_text = st.text_input("Modifications (Ex: blond, bijoux, plage...) :", key="mod_input")

            if st.button("🔥 GÉNÉRER LE PROMPT", type="primary"):
                if user_text:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    # Force la conservation absolue du visage
                    instruction = f"CONSIGNE : Garde le visage à 100%. MODIFS : {user_text}. Donne le prompt positif et négatif."
                    
                    with st.spinner("Analyse en cours..."):
                        response = model.generate_content([instruction, img])
                        st.code(response.text, language="markdown")
                        st.success("Copié le résultat ci-dessus.")
                else:
                    st.warning("Décrivez les changements voulus.")
                    
        except Exception as e:
            st.error(f"Fichier non reçu : réessayez la sélection.")
            if st.button("Forcer la réactualisation"):
                st.rerun()

# 3. BAS DE PAGE POUR ÉVITER LE CACHE
st.markdown("---")
if st.button("🔄 Nouvelle session (Clean Cache)"):
    st.session_state.clear()
    st.rerun()

