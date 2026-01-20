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

st.set_page_config(page_title="Retouche Pro Ultra", layout="centered")

st.title("📸 Expert Retouche & Identité")
st.write("Optimisé pour Bibliothèque Android / Google Photos")

# --- 2. SYSTÈME DE CAPTURE ROBUSTE ---
# On utilise un conteneur pour stabiliser l'affichage
container = st.container()

uploaded_files = st.file_uploader(
    "Accéder à votre bibliothèque", 
    type=['jpg', 'jpeg', 'png'], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            # FORCE DOWNLOAD : On lit les octets immédiatement pour forcer Android
            # à télécharger la photo depuis le cloud si nécessaire.
            file_bytes = uploaded_file.read() 
            
            if file_bytes:
                # Conversion en image exploitable
                img = Image.open(io.BytesIO(file_bytes))
                
                with container:
                    st.image(img, caption=f"Chargé : {uploaded_file.name}", use_container_width=True)
                    
                    user_text = st.text_input(f"Modifications pour {uploaded_file.name} :", key=uploaded_file.name)

                    if st.button(f"🚀 GÉNÉRER POUR {uploaded_file.name}"):
                        if user_text:
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            instruction = f"CONSIGNE : Garde le visage à 100%. MODIFS : {user_text}. Donne le prompt positif et négatif."
                            
                            with st.spinner("Analyse faciale en cours..."):
                                response = model.generate_content([instruction, img])
                                st.code(response.text)
                        else:
                            st.warning("Écris tes modifs !")
                st.markdown("---")
        except Exception as e:
            st.error(f"Erreur sur {uploaded_file.name} : La photo est peut-être encore en cours de synchronisation sur votre téléphone.")

# Bouton de nettoyage
if st.button("🗑️ Vider tout"):
    st.rerun()
