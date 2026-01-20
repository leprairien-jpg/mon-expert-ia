import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Configuration de base ultra-rapide
st.set_page_config(page_title="Retouche Rapide", layout="centered")

# On cache la configuration pour ne pas ralentir le démarrage
@st.cache_resource
def init_genai():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel('gemini-2.5-flash')

model = init_genai()

st.title("📸 Master Retouche")

# 2. Zone d'upload avec "st.empty" pour éviter le gel de l'écran
upload_placeholder = st.empty()
uploaded_file = upload_placeholder.file_uploader("Choisir une photo", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # On affiche un message de chargement local pour rassurer l'utilisateur
    with st.status("📥 Réception de l'image...", expanded=False) as status:
        try:
            # On utilise BytesIO pour ne pas saturer la RAM du téléphone
            image_bytes = uploaded_file.getvalue()
            image = Image.open(io.BytesIO(image_bytes))
            status.update(label="✅ Image reçue !", state="complete")
            
            # Affichage de l'image réduite pour économiser la bande passante
            st.image(image, use_container_width=True)
            
            user_text = st.text_input("Tes modifications (ex: blond, plage...)")

            if st.button("🔥 GÉNÉRER", type="primary"):
                if user_text:
                    with st.spinner("L'IA analyse..."):
                        instruction = f"CONSIGNE : Garde le visage à 100%. MODIFS : {user_text}. Donne le prompt positif et négatif en anglais."
                        response = model.generate_content([instruction, image])
                        st.code(response.text)
                else:
                    st.warning("Écris tes modifs !")
                    
        except Exception as e:
            st.error("Connexion perdue pendant l'envoi. Réessaie.")
            if st.button("🔄 Relancer la connexion"):
                st.rerun()

# 3. Bouton pour forcer le nettoyage du serveur si ça bloque
st.sidebar.button("Réinitialiser l'App", on_click=lambda: st.cache_data.clear())
