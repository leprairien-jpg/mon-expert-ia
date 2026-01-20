import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Config rapide
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
st.set_page_config(page_title="Retouche Pro", layout="centered")

st.title("📸 Master Retouche")

# 2. LOGIQUE DE STABILISATION
# On utilise le session_state pour "fixer" l'image une fois qu'elle est enfin lue
if 'img_buffer' not in st.session_state:
    st.session_state.img_buffer = None

# Bouton de nettoyage propre
if st.sidebar.button("♻️ Nouvelle Photo"):
    st.session_state.img_buffer = None
    st.cache_data.clear()
    st.rerun()

# 3. L'UPLOADER (Configuré pour être plus patient)
uploaded_file = st.file_uploader("Choisir une photo", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    # Si on détecte un changement, on tente de lire le buffer
    try:
        # On force la lecture complète du fichier en mémoire RAM
        st.session_state.img_buffer = uploaded_file.getvalue()
    except:
        st.error("Transfert instable... réessayez la sélection.")

# 4. AFFICHAGE DEPUIS LE BUFFER (Mémoire fixe)
if st.session_state.img_buffer:
    try:
        # On affiche l'image depuis la RAM, plus de bug de connexion ici
        image = Image.open(io.BytesIO(st.session_state.img_buffer))
        st.image(image, use_container_width=True)
        
        user_text = st.text_input("Modifications :", placeholder="ex: blond, plage...")

        if st.button("🚀 GÉNÉRER"):
            if user_text:
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Analyse..."):
                    instruction = f"CONSIGNE : Garde le visage à 100%. MODIFS : {user_text}. Prompt positif/négatif en anglais."
                    response = model.generate_content([instruction, image])
                    st.code(response.text)
            else:
                st.warning("Écris tes modifs !")
    except Exception as e:
        st.error("Erreur de lecture du fichier.")
