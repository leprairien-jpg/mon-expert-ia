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
    return genai.GenerativeModel('gemini-2.5-flash')  # VOTRE MODÈLE ORIGINAL

st.set_page_config(page_title="Retouche Pro", layout="centered")

# --- 2. FIX RADICAL POUR ANDROID ---
# On désactive le cache de données de Streamlit pour cette session
st.cache_data.clear()

# --- FONCTION OPTIMISÉE POUR ANDROID ---
def force_load_android_image(uploaded_file):
    """
    Force le chargement de n'importe quelle photo Android
    """
    try:
        # Lire les bytes
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        
        # Ouvrir avec PIL
        img = Image.open(io.BytesIO(file_bytes))
        
        # Conversion en RGB (important pour Android)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Sauvegarder sans métadonnées problématiques
        output = io.BytesIO()
        img.save(output, 'JPEG', quality=85, optimize=True)
        return output.getvalue()
        
    except Exception:
        # En cas d'erreur, fallback simple
        return uploaded_file.getvalue()

st.title("📸 Master Retouche Identité")

# On utilise un widget simple sans fioritures pour maximiser la compatibilité
uploaded_file = st.file_uploader("Sélectionnez votre photo", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # TECHNIQUE COMMANDO : On lit le fichier et on l'affiche immédiatement
    # sans passer par des fonctions intermédiaires qui font "bugger" Chrome
    file_container = st.container()
    
    try:
        # OPTIMISATION ANDROID : Chargement forcé
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
                
                # PROMPT ORIGINAL EXACT (inchangé) :
                instruction = f"Tu es un expert en prompt engineering pour l'IA. Ta mission : analyser cette photo et générer un prompt détaillé pour reproduire exactement le visage mais en appliquant ces modifications : {user_text}. Le prompt doit inclure une partie positive (ce qu'il faut) et une partie négative (ce qu'il faut éviter)."
                
                with st.spinner("Analyse faciale..."):
                    response = model.generate_content([instruction, img])
                    st.code(response.text, language="markdown")
            else:
                st.warning("Précise ce que tu veux changer.")
                
    except Exception as e:
        st.error(f"Erreur de flux : {e}")
        
        # SOLUTION ANDROID : Boutons de récupération
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Réessayer", use_container_width=True):
                st.rerun()
        with col2:
            if st.button("📸 Prendre une photo", use_container_width=True):
                st.info("Utilisez la caméra si possible")

# --- SOLUTIONS ANDROID AVANCÉES ---
with st.expander("🚨 SI LA PHOTO NE S'AFFICHE PAS"):
    st.markdown("""
    **SOLUTIONS POUR ANDROID :**
    
    1. **📸 Capture d'écran** : Prenez une capture de la photo → Ça marche toujours
    2. **🔄 Sélectionner 2 fois** : Parfois il faut sélectionner 2 fois la même photo
    3. **🗑️ Vider cache Chrome** : Chrome → Paramètres → Confidentialité → Effacer données
    4. **📱 Mode Bureau** : Activez "Mode site pour ordinateur" dans Chrome
    """)
    
    # Alternative camera (fonctionne mieux sur Android)
    camera_photo = st.camera_input("📸 Ou prendre une photo directe")
    if camera_photo:
        st.session_state.photo_data = camera_photo.getvalue()
        st.rerun()

# --- BOUTONS DE DÉPANNAGE ANDROID ---
st.sidebar.markdown("### 🔧 Outils Android")

if st.sidebar.button("🔄 Nettoyer et Redémarrer", type="secondary"):
    st.cache_data.clear()
    st.cache_resource.clear()
    for key in list(st.session_state.keys()):
        if key != 'model':  # Garder le modèle en mémoire
            del st.session_state[key]
    st.rerun()

if st.sidebar.button("📱 Mode Compatibilité", type="secondary"):
    st.info("Mode compatibilité Android activé")

# --- CSS OPTIMISÉ POUR ANDROID ---
st.markdown("""
<style>
    /* Meilleure compatibilité Android */
    .stApp {
        overflow-x: hidden;
    }
    
    /* Boutons plus visibles sur mobile */
    .stButton > button {
        font-size: 16px !important;
        padding: 12px 24px !important;
        border-radius: 10px !important;
    }
    
    /* Désactiver certaines animations lourdes */
    @media (max-width: 768px) {
        .element-container {
            animation: none !important;
            transition: none !important;
        }
    }
    
    /* File uploader plus visible */
    div[data-testid="stFileUploader"] {
        border: 2px dashed #4CAF50 !important;
        padding: 30px !important;
        text-align: center !important;
    }
</style>
""", unsafe_allow_html=True)

# Message d'aide Android
st.sidebar.info("""
**💡 Conseil Android :**
Les captures d'écran marchent toujours mieux que les photos anciennes de la galerie.
""")
