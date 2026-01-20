import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import sys

# --- CONFIGURATION OPTIMISÉE POUR ANDROID ---
st.set_page_config(
    page_title="Retouche Pro",
    layout="centered",
    initial_sidebar_state="collapsed"  # Réduit le chargement initial
)

# Désactivation des caches problématiques
st.cache_data.clear()

# --- MODÈLE LÉGER ---
@st.cache_resource(ttl=3600)  # Cache 1 heure seulement
def load_model():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash-latest')  # Version plus légère
    except Exception:
        st.error("Erreur de configuration")
        return None

# --- OPTIMISATION DES IMAGES POUR ANDROID ---
def optimize_image_for_mobile(image_bytes, max_size=1024):
    """Réduit la taille de l'image pour Android"""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Réduction progressive si l'image est trop grande
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Compression optimisée
        output = io.BytesIO()
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        img.save(output, format='JPEG', quality=85, optimize=True)
        return output.getvalue()
    except Exception:
        return image_bytes  # Retourne l'original si erreur

# --- INTERFACE SIMPLIFIÉE ---
st.title("📸 Master Retouche")

# File uploader avec paramètres optimisés
uploaded_file = st.file_uploader(
    "📁 Choisir une photo",
    type=['jpg', 'jpeg', 'png'],
    help="Pour Android : choisir des photos de taille moyenne",
    key="file_uploader"  # Clé fixe pour éviter les bugs
)

# Zone d'affichage unique
image_container = st.container()

if uploaded_file is not None:
    try:
        # Lecture et optimisation immédiate
        raw_data = uploaded_file.getvalue()
        
        # Afficher un indicateur de chargement
        with st.spinner("Optimisation de l'image..."):
            optimized_data = optimize_image_for_mobile(raw_data)
        
        # Affichage avec taille fixe pour Android
        image_container.image(
            optimized_data,
            caption="Photo chargée ✓",
            use_container_width=True,
            output_format="JPEG"
        )
        
        # Section de modifications
        with st.container():
            st.markdown("---")
            user_text = st.text_input(
                "**Tes modifications :**",
                placeholder="Ex: cheveux blonds, ajouter des lunettes..."
                # LIMITE SUPPRIMÉE ICI
            )
            
            # Bouton avec feedback immédiat
            if st.button("🚀 Générer le prompt", use_container_width=True, type="primary"):
                if user_text.strip():
                    model = load_model()
                    if model:
                        with st.spinner("Analyse en cours..."):
                            try:
                                img = Image.open(io.BytesIO(optimized_data))
                                instruction = f"CONSIGNE : Garde le visage à 100%. MODIFS : {user_text}. Donne le prompt positif et négatif."
                                response = model.generate_content([instruction, img])
                                
                                # Affichage formaté
                                st.markdown("### ✨ Résultat :")
                                st.code(response.text, language="markdown")
                                
                                # Bouton de copie
                                if st.button("📋 Copier le prompt", use_container_width=True):
                                    st.code(response.text)
                                    st.success("Prompt copié !")
                                    
                            except Exception as e:
                                st.error(f"Erreur de génération : {str(e)}")
                    else:
                        st.error("Modèle non chargé")
                else:
                    st.warning("⚠️ Indique ce que tu veux modifier")

    except Exception as e:
        st.error(f"❌ Erreur : {str(e)[:100]}...")
        
        # Bouton de réessai simplifié
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Réessayer", use_container_width=True):
                st.rerun()
        with col2:
            if st.button("📁 Changer de photo", use_container_width=True):
                st.session_state.file_uploader = None
                st.rerun()

# --- ZONE DE DÉPANNAGE ---
with st.expander("🔧 Problèmes fréquents sur Android"):
    st.markdown("""
    **Si les photos ne se chargent pas :**
    1. 📱 **Redémarrer l'app Chrome**
    2. 🗑️ **Vider le cache** : Chrome → Paramètres → Confidentialité → Effacer données
    3. 📸 **Choisir une photo plus petite** (< 5MB)
    4. 🔄 **Rafraîchir la page** (glisser vers le bas)
    
    **Solution radicale :**
    - Activer le **mode bureau** dans Chrome
    - Désactiver **Data Saver**
    """)

# Bouton de nettoyage simplifié
if st.sidebar.button("🔄 Réinitialiser l'app", type="secondary"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.cache_data.clear()
    st.rerun()

# CSS léger pour Android
st.markdown("""
<style>
    .stButton > button {
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
    }
    /* Désactive certaines animations lourdes */
    @media (max-width: 768px) {
        .element-container {
            animation: none !important;
        }
    }
</style>
""", unsafe_allow_html=True)
