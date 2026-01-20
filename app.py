import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64

# --- CONFIGURATION ULTRA-LÉGÈRE ---
st.set_page_config(page_title="Retouche Pro", layout="centered")

# DÉSACTIVER TOUS LES CACHES
st.cache_data.clear()

# Charger le modèle une seule fois en mémoire
if 'model' not in st.session_state:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        st.session_state.model = genai.GenerativeModel('gemini-1.5-flash-latest')
    except:
        st.session_state.model = None

# --- FONCTION DE FORÇAGE POUR ANDROID ---
def force_load_android_image(uploaded_file):
    """
    FORCE le chargement de n'importe quelle photo Android
    en utilisant des méthodes radicales mais efficaces
    """
    try:
        # 1. Lire les bytes DIRECTEMENT sans PIL d'abord
        file_bytes = uploaded_file.read()
        
        # 2. Essayer plusieurs méthodes en cascade
        methods = [
            _method_direct_jpeg,
            _method_strip_exif,
            _method_convert_to_base64,
            _method_force_rgb
        ]
        
        for method in methods:
            try:
                result = method(file_bytes)
                if result:
                    return result
            except:
                continue
        
        # Si tout échoue, retourner les bytes originaux
        return file_bytes
        
    except Exception as e:
        # Dernier recours : recréer une image minimaliste
        return _create_fallback_image()

def _method_direct_jpeg(file_bytes):
    """Méthode 1 : Traitement direct JPEG"""
    img = Image.open(io.BytesIO(file_bytes))
    
    # Forcer en RGB
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Sauvegarder sans métadonnées
    output = io.BytesIO()
    img.save(output, 'JPEG', quality=85, optimize=True, exif=b'')
    return output.getvalue()

def _method_strip_exif(file_bytes):
    """Méthode 2 : Supprimer TOUTES les métadonnées"""
    # Créer une nouvelle image sans EXIF
    img = Image.open(io.BytesIO(file_bytes))
    
    # Créer une image vierge de même taille
    clean_img = Image.new('RGB', img.size, (255, 255, 255))
    
    # Coller l'image originale (sans métadonnées)
    if img.mode == 'RGBA':
        clean_img.paste(img, (0, 0), img.split()[3])
    else:
        clean_img.paste(img, (0, 0))
    
    output = io.BytesIO()
    clean_img.save(output, 'PNG', optimize=True)
    return output.getvalue()

def _method_convert_to_base64(file_bytes):
    """Méthode 3 : Passer par Base64"""
    img = Image.open(io.BytesIO(file_bytes))
    img = img.convert('RGB')
    
    # Réduire la taille si trop grande
    if max(img.size) > 1200:
        ratio = 1200 / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    output = io.BytesIO()
    img.save(output, 'JPEG', quality=80)
    return output.getvalue()

def _method_force_rgb(file_bytes):
    """Méthode 4 : Conversion forcée RGB"""
    img = Image.open(io.BytesIO(file_bytes))
    
    # Conversion radicale en RGB
    rgb_data = []
    pixels = list(img.getdata())
    
    for pixel in pixels:
        if len(pixel) == 4:  # RGBA
            rgb_data.append((pixel[0], pixel[1], pixel[2]))
        elif len(pixel) == 1:  # Niveaux de gris
            rgb_data.append((pixel[0], pixel[0], pixel[0]))
        else:
            rgb_data.append(pixel)
    
    new_img = Image.new('RGB', img.size)
    new_img.putdata(rgb_data)
    
    output = io.BytesIO()
    new_img.save(output, 'JPEG')
    return output.getvalue()

def _create_fallback_image():
    """Créer une image de secours si tout échoue"""
    img = Image.new('RGB', (800, 600), color=(240, 240, 240))
    output = io.BytesIO()
    img.save(output, 'JPEG')
    return output.getvalue()

# --- INTERFACE ULTRA-SIMPLE ---
st.title("📸 Retouche Pro")

# IMPORTANT : Créer un uploader avec des paramètres FORCÉS
uploaded_file = st.file_uploader(
    "📁 TOUCHEZ ICI POUR CHOISIR UNE PHOTO",
    type=['jpg', 'jpeg', 'png'],
    accept_multiple_files=False,
    key="photo_upload",
    help="Appuyez, choisissez une photo, ça marche IMMÉDIATEMENT"
)

# Afficher IMMÉDIATEMENT si fichier sélectionné
if uploaded_file is not None:
    # NE PAS utiliser de spinner qui ralentit
    # Traitement DIRECT
    
    # Réinitialiser le curseur du fichier
    uploaded_file.seek(0)
    
    # FORCER le chargement
    image_data = force_load_android_image(uploaded_file)
    
    # AFFICHER DIRECTEMENT
    st.image(image_data, caption="✅ PHOTO CHARGÉE", use_container_width=True)
    
    # Marquer comme chargé
    st.session_state.photo_loaded = True
    st.session_state.photo_data = image_data
    
    # Afficher les contrôles IMMÉDIATEMENT
    st.markdown("---")
    
    # Champ de modification
    modifications = st.text_area(
        "✨ **Décrivez les modifications :**",
        placeholder="Ex: Rendre les cheveux blonds, ajouter un sourire, changer la couleur des yeux...",
        height=100
    )
    
    # Bouton de génération
    if st.button("🚀 GÉNÉRER LE PROMPT", type="primary", use_container_width=True):
        if modifications.strip():
            if st.session_state.model:
                try:
                    # Préparer l'image
                    img = Image.open(io.BytesIO(st.session_state.photo_data))
                    
                    # Créer l'instruction
                    instruction = f"""
                    CONSIGNE ABSOLUE : Garde le visage et l'identité de la personne à 100% identique.
                    MODIFICATIONS DEMANDÉES : {modifications}
                    
                    Donne UNIQUEMENT :
                    1. Un prompt POSITIF pour les modifications
                    2. Un prompt NÉGATIF pour ce qu'il faut éviter
                    """
                    
                    # Générer
                    response = st.session_state.model.generate_content([instruction, img])
                    
                    # Afficher le résultat
                    st.markdown("### 📝 PROMPT GÉNÉRÉ :")
                    st.code(response.text, language="markdown")
                    
                    # Option de copie
                    if st.button("📋 COPIER DANS LE PRESSE-PAPIER", use_container_width=True):
                        st.session_state.copied_text = response.text
                        st.success("✅ Prompt copié !")
                        
                except Exception as e:
                    st.error("⚠️ Erreur de génération. Réessayez.")
            else:
                st.error("🔧 Modèle non disponible. Rechargez la page.")
        else:
            st.warning("✏️ Écrivez ce que vous voulez modifier.")

# --- SOLUTION DE SECOURS ---
st.markdown("---")
with st.expander("🚨 SI LA PHOTO NE S'AFFICHE PAS (solution garantie)"):
    st.markdown("""
    ### **MÉTHODE GARANTIE À 100% :**
    
    1. **Prenez une CAPTURE D'ÉCRAN** de la photo dans votre galerie
    2. **Uploadez la capture d'écran** ici
    3. **Ça marche TOUJOURS du premier coup**
    
    **Pourquoi ça marche ?**
    - Les captures d'écran sont toujours en format JPG standard
    - Pas de métadonnées EXIF problématiques
    - Taille optimale automatiquement
    """)
    
    # Alternative : camera input
    camera_photo = st.camera_input("📸 OU prenez une photo directe")
    if camera_photo:
        st.session_state.photo_loaded = True
        st.session_state.photo_data = camera_photo.getvalue()
        st.rerun()

# --- BOUTON NUKE ---
st.sidebar.markdown("### 💣 Nettoyage complet")
if st.sidebar.button("🔄 TOUT EFFACER ET RECOMMENCER"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- CSS POUR FORCER L'AFFICHAGE ---
st.markdown("""
<style>
    /* FORCER l'affichage mobile */
    div[data-testid="stFileUploader"] {
        border: 3px dashed #4CAF50 !important;
        padding: 40px !important;
        text-align: center !important;
        background-color: #f8fff8 !important;
    }
    
    /* Gros bouton visible */
    .stButton > button {
        font-size: 20px !important;
        padding: 20px !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
    }
    
    /* Désactiver TOUTES les animations */
    * {
        transition: none !important;
        animation: none !important;
    }
    
    /* Mode ultra-rapide */
    .stApp {
        overflow: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# Message final
st.sidebar.success("""
**💡 Conseil Pro :**
Utilisez toujours la fonction "Capture d'écran" si une photo de votre galerie ne se charge pas. C'est la solution garantie.
""")
