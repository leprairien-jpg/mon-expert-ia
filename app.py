import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. CONFIGURATION ---
# On utilise un cache de ressource pour ne pas ralentir le script au chargement
@st.cache_resource
def load_model():
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="Retouche Pro", layout="centered")

# --- 2. FIX RADICAL POUR ANDROID ---
# On désactive le cache de données de Streamlit pour cette session
st.cache_data.clear()

st.title("📸 Master Retouche Identité")

# On utilise un widget simple sans fioritures pour maximiser la compatibilité
uploaded_file = st.file_uploader("Sélectionnez votre photo", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # TECHNIQUE COMMANDO : On lit le fichier et on l'affiche immédiatement
    # sans passer par des fonctions intermédiaires qui font "bugger" Chrome
    file_container = st.container()
    
    try:
        # Lecture directe des octets
        raw_data = uploaded_file.getvalue()
        
        # Affichage immédiat du flux
        file_container.image(raw_data, caption="Photo détectée", use_container_width=True)
        
        # Une fois affichée, on prépare la transformation
        user_text = st.text_input("Tes modifications (ex: blond, bijoux...) :")

        if st.button("🚀 GÉNÉRER LE PROMPT", type="primary"):
            if user_text:
                # Conversion en image PIL seulement au moment du clic
                img = Image.open(io.BytesIO(raw_data))
                model = load_model()
                
                instruction = f"CONSIGNE : Garde le visage à 100%. MODIFS : {user_text}. Donne le prompt positif et négatif."
                
                with st.spinner("Analyse faciale..."):
                    response = model.generate_content([instruction, img])
                    st.code(response.text, language="markdown")
            else:
                st.warning("Précise ce que tu veux changer.")
                
    except Exception as e:
        st.error(f"Erreur de flux : {e}")
        st.button("🔄 Réessayer la sélection", on_click=lambda: st.rerun())

# Bouton de secours en sidebar pour vider le cache du navigateur
if st.sidebar.button("Nettoyer l'App"):
    st.rerun()
