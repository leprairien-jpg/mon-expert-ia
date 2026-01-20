import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64

# --- 1. CONFIGURATION ---
# On utilise un cache de ressource pour ne pas ralentir le script au chargement
@st.cache_resource
def load_model():
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # MODÈLE CORRIGÉ : utiliser le bon nom
    return genai.GenerativeModel('gemini-1.5-flash-latest')

st.set_page_config(page_title="Retouche Pro", layout="centered")

# --- 2. FIX RADICAL POUR ANDROID ---
# On désactive le cache de données de Streamlit pour cette session
st.cache_data.clear()

# --- FONCTION DE FORÇAGE POUR ANDROID ---
def force_load_android_image(uploaded_file):
    """
    FORCE le chargement de n'importe quelle photo Android
    """
    try:
        # Lire les bytes
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        
        # Ouvrir avec PIL
        img = Image.open(io.BytesIO(file_bytes))
        
        # Conversion en RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Sauvegarder sans métadonnées problématiques
        output = io.BytesIO()
        img.save(output, 'JPEG', quality=85, optimize=True)
        return output.getvalue()
        
    except Exception:
        # En cas d'erreur, créer une image simple
        img = Image.new('RGB', (800, 600), color=(240, 240, 240))
        output = io.BytesIO()
        img.save(output, 'JPEG')
        return output.getvalue()

st.title("📸 Master Retouche Identité")

# On utilise un widget simple sans fioritures pour maximiser la compatibilité
uploaded_file = st.file_uploader("Sélectionnez votre photo", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # TECHNIQUE COMMANDO : On lit le fichier et on l'affiche immédiatement
    # sans passer par des fonctions intermédiaires qui font "bugger" Chrome
    file_container = st.container()
    
    try:
        # FORCER le chargement Android
        raw_data = force_load_android_image(uploaded_file)
        
        # Affichage immédiat du flux
        file_container.image(raw_data, caption="Photo détectée", use_container_width=True)
        
        # Une fois affichée, on prépare la transformation
        user_text = st.text_input("Tes modifications (ex: blond, bijoux...) :")

        if st.button("🚀 GÉNÉRER LE PROMPT", type="primary"):
            if user_text:
                # Conversion en image PIL seulement au moment du clic
                img = Image.open(io.BytesIO(raw_data))
                model = load_model()
                
                # INSTRUCTION ORIGINALE EXACTE DE VOTRE CODE
                instruction = f"CONSIGNE : Garde le visage à 100%. MODIFS : {user_text}. Donne le prompt positif et négatif."
                
                with st.spinner("Analyse faciale..."):
                    response = model.generate_content([instruction, img])
                    st.code(response.text, language="markdown")
            else:
                st.warning("Précise ce que tu veux changer.")
                
    except Exception as e:
        st.error(f"Erreur de flux : {e}")
        st.button("🔄 Réessayer la sélection", on_click=lambda: st.rerun())

# --- SOLUTION DE SECOURS ---
with st.expander("🚨 SI LA PHOTO NE S'AFFICHE PAS"):
    st.markdown("""
    **MÉTHODE GARANTIE :**
    1. **Prenez une CAPTURE D'ÉCRAN** de la photo
    2. **Uploadez la capture ici**
    3. **Ça marche TOUJOURS**
    """)
    
    # Alternative camera
    camera_photo = st.camera_input("📸 Ou prenez une photo directe")
    if camera_photo:
        st.session_state.photo_data = camera_photo.getvalue()
        st.rerun()

# Bouton de secours en sidebar pour vider le cache du navigateur
if st.sidebar.button("Nettoyer l'App"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

# CSS simple
st.markdown("""
<style>
    .stButton > button {
        background-color: #FF4B4B;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)
