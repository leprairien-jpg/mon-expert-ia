import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps, ExifTags
import io
import sys
from datetime import datetime

# --- CONFIGURATION OPTIMISÉE POUR ANDROID ---
st.set_page_config(
    page_title="Retouche Pro",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Désactivation des caches
st.cache_data.clear()

# --- MODÈLE ---
@st.cache_resource(ttl=3600)
def load_model():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash-latest')
    except Exception:
        st.error("Erreur de configuration")
        return None

# --- FONCTION AMÉLIORÉE POUR LES PHOTOS ANDROID ---
def process_android_image(image_bytes):
    """
    Traite spécifiquement les photos Android avec problèmes d'EXIF
    et de format
    """
    try:
        # Ouvrir l'image avec PIL
        img = Image.open(io.BytesIO(image_bytes))
        
        # 1. CORRECTION D'ORIENTATION EXIF (problème fréquent sur Android)
        try:
            # Vérifier et corriger l'orientation EXIF
            exif = img._getexif()
            if exif:
                orientation_key = 274  # clé EXIF pour l'orientation
                if orientation_key in exif:
                    orientation = exif[orientation_key]
                    
                    # Appliquer la rotation nécessaire
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
        except:
            pass  # Si échec, on continue avec l'image originale
        
        # 2. CONVERSION FORMAT SÛR
        # Forcer la conversion en RGB pour éviter les problèmes de canaux alpha
        if img.mode in ('RGBA', 'LA', 'P'):
            # Créer un fond blanc pour les images transparentes
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 3. RÉDUCTION PROGRESSIVE (seulement si nécessaire)
        max_dimension = 1200  # Bon compromis pour Android
        
        if max(img.size) > max_dimension:
            ratio = max_dimension / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # 4. COMPRESSION OPTIMISÉE POUR ANDROID
        output = io.BytesIO()
        img.save(
            output,
            format='JPEG',
            quality=80,  # Qualité réduite pour meilleure performance
            optimize=True,
            progressive=True  # Meilleur chargement progressif
        )
        
        return output.getvalue(), True
        
    except Exception as e:
        st.error(f"Erreur traitement: {str(e)[:50]}")
        # En cas d'échec, retourner les données originales
        return image_bytes, False

# --- INTERFACE AMÉLIORÉE ---
st.title("📸 Master Retouche")

# Indicateur de chargement initial
with st.spinner("Initialisation..."):
    model = load_model()

# File uploader avec options spécifiques
uploaded_file = st.file_uploader(
    "📁 Choisir une photo de votre bibliothèque",
    type=['jpg', 'jpeg', 'png', 'heic', 'heif', 'webp'],  # Formats supportés Android
    help="Conseil : Sélectionnez 2 fois si la photo ne s'affiche pas",
    key="file_uploader"
)

# Gestionnaire d'état pour suivre les tentatives
if 'upload_attempts' not in st.session_state:
    st.session_state.upload_attempts = 0

if uploaded_file is not None:
    # Augmenter le compteur de tentatives
    st.session_state.upload_attempts += 1
    
    try:
        # Lire les données brutes
        raw_data = uploaded_file.getvalue()
        
        # Afficher un indicateur
        with st.spinner(f"Traitement de la photo (essai {st.session_state.upload_attempts})..."):
            # Traiter l'image spécifiquement pour Android
            processed_data, success = process_android_image(raw_data)
            
            if success:
                # Afficher l'image traitée
                st.image(
                    processed_data,
                    caption=f"✅ Photo chargée (taille: {len(processed_data)//1024} KB)",
                    use_container_width=True
                )
                
                # Afficher un message de succès
                if st.session_state.upload_attempts > 1:
                    st.success(f"Photo chargée après {st.session_state.upload_attempts} essais !")
                
                # Réinitialiser le compteur
                st.session_state.upload_attempts = 0
                
                # --- SECTION MODIFICATIONS ---
                st.markdown("---")
                
                # Champ de texte sans limite
                user_text = st.text_input(
                    "**Tes modifications :**",
                    placeholder="Ex: cheveux blonds, ajouter des lunettes, changer couleur yeux...",
                    key="modifications"
                )
                
                # Bouton de génération
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button("🚀 Générer le prompt", use_container_width=True, type="primary"):
                        if user_text.strip():
                            if model:
                                with st.spinner("Analyse avec IA..."):
                                    try:
                                        img = Image.open(io.BytesIO(processed_data))
                                        instruction = f"CONSIGNE : Garde le visage à 100%. MODIFS : {user_text}. Donne le prompt positif et négatif."
                                        response = model.generate_content([instruction, img])
                                        
                                        # Affichage du résultat
                                        st.markdown("### ✨ Résultat :")
                                        st.code(response.text, language="markdown")
                                        
                                        # Option de copie
                                        if st.button("📋 Copier le prompt", use_container_width=True):
                                            st.code(response.text)
                                            st.success("Prompt copié !")
                                            
                                    except Exception as e:
                                        st.error(f"Erreur IA : {str(e)[:100]}")
                            else:
                                st.error("Modèle non disponible")
                        else:
                            st.warning("⚠️ Décris les modifications souhaitées")
                
                with col2:
                    if st.button("🔄 Nouvelle photo", use_container_width=True):
                        st.session_state.upload_attempts = 0
                        st.rerun()
            
            else:
                st.warning("⚠️ Photo non traitée correctement. Essayez à nouveau.")
                
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement : {str(e)[:100]}")
        
        # Boutons de récupération
        st.markdown("### 🔧 Solutions :")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Réessayer", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("📸 Prendre une photo", use_container_width=True):
                st.info("Utilisez l'appareil photo si possible")
        
        with col3:
            if st.button("📁 Sélectionner à nouveau", use_container_width=True):
                st.session_state.file_uploader = None
                st.session_state.upload_attempts = 0
                st.rerun()

# --- SECTION DÉPANNAGE AVANCÉ ---
with st.expander("🔧 SOLUTIONS POUR PHOTOS ANDROID", expanded=False):
    st.markdown("""
    ### **Problème : Photos anciennes ne se chargent pas**
    
    **Causes possibles :**
    1. **Métadonnées EXIF corrompues** (très fréquent sur Android)
    2. **Format HEIC/HEIF** non bien supporté
    3. **Taille trop importante** (>10MB)
    4. **Permissions de stockage** limitées
    
    **Solutions :**
    
    **🎯 SOLUTION RAPIDE :**
    - Sélectionnez la photo **2 fois de suite**
    - Ou prenez une **screenshot** de la photo et uploadez-la
    
    **📱 SUR VOTRE ANDROID :**
    1. **Redimensionner avant** :
       - Ouvrir la photo dans Google Photos
       - Taper "Modifier" → "Recadrer" → Enregistrer
       - La photo sera convertie en format standard
    
    2. **Convertir en JPG** :
       - Utiliser l'app "Photo & Picture Resizer"
       - Choisir "Convert to JPG"
    
    3. **Mode navigation privée** :
       - Ouvrir Chrome en navigation privée
       - Aller sur votre app Streamlit
       - Les caches sont désactivés
    
    **🌐 SOLUTION STREAMIT :**
    - Activez cette option si disponible :
    """)
    
    # Option pour désactiver le traitement EXIF
    disable_exif = st.checkbox("Désactiver la correction EXIF (essayez si échec)")
    if disable_exif:
        st.info("La correction EXIF sera désactivée au prochain chargement")

# --- BOUTONS DE RÉCUPÉRATION ---
st.sidebar.markdown("### Outils de dépannage")

if st.sidebar.button("🔄 Réinitialiser complètement", type="secondary"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

if st.sidebar.button("📱 Mode compatibilité Android", type="secondary"):
    st.info("Mode compatibilité activé - utilisez des photos récentes")

# CSS optimisé pour Android
st.markdown("""
<style>
    /* Optimisations pour Android */
    @media (max-width: 768px) {
        .stApp {
            overflow-x: hidden;
        }
        .element-container {
            padding: 5px !important;
        }
        /* Désactiver les animations lourdes */
        * {
            animation: none !important;
            transition: none !important;
        }
    }
    
    /* Style pour les boutons Android */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        padding: 12px !important;
    }
    
    /* Meilleur contraste pour mobile */
    .stTextInput > div > div > input {
        font-size: 18px !important;
        padding: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# Message d'information
st.sidebar.info("""
**Conseil :**
Les photos récentes (screenshots, photos prises maintenant) fonctionnent toujours mieux que les anciennes photos de la bibliothèque.
""")
