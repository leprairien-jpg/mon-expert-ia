import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIGURATION SÉCURISÉE (STRICTE) ---
try:
    # On récupère la clé depuis le menu 'Settings > Secrets' de Streamlit Cloud
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("❌ ERREUR : La clé GEMINI_API_KEY est absente des 'Secrets' de l'application.")
    st.info("Allez dans Settings > Secrets et ajoutez : GEMINI_API_KEY = 'votre_cle'")
    st.stop()

# Configuration de la page pour Android et PC
st.set_page_config(page_title="Expert Retouche Identité", layout="centered", page_icon="📸")

# --- 2. LOGIQUE DE CHARGEMENT IMMÉDIAT ---
# Utilisation d'une clé de session pour forcer le rafraîchissement sur Android
if 'uploader_key' not in st.session_state:
    st.session_state['uploader_key'] = 0

def clear_photo():
    st.session_state['uploader_key'] += 1
    st.rerun()

st.title("📸 Master Face Consistency")
st.markdown("---")

# --- 3. INTERFACE DE SÉLECTION ---
# La clé dynamique permet de forcer le chargement dès la première sélection
uploaded_file = st.file_uploader(
    "Choisissez une photo dans votre bibliothèque", 
    type=['jpg', 'jpeg', 'png'],
    key=f"uploader_{st.session_state['uploader_key']}"
)

if uploaded_file:
    # Lecture directe du fichier pour éviter le bug de double clic
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Référence d'identité (Verrouillée)", use_container_width=True)
        
        # Saisie des modifications
        user_text = st.text_area(
            "🔧 Modifications souhaitées (Tout sauf le visage) :",
            placeholder="Ex: Cheveux blonds, bijoux en or, plage paradisiaque...",
            height=100
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🚀 GÉNÉRER LE PROMPT", type="primary"):
                if user_text:
                    # On utilise le modèle le plus puissant détecté lors du diagnostic (2.5 Flash)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    # INSTRUCTION D'EXPERT : Verrouillage du visage à 100%
                    system_prompt = f"""
                    Tu es un Ingénieur Expert en 'Face Consistency' pour IA générative (Midjourney, Flux, DALL-E).
                    
                    ANALYSE DE L'IMAGE : 
                    Observe précisément la structure osseuse, la forme des yeux, la mâchoire et l'identité unique du visage.
                    
                    MISSION : 
                    Rédige un prompt qui ordonne au générateur d'image de NE PAS MODIFIER LE VISAGE. 
                    Le visage doit rester reconnaissable à 100% (Identical facial mapping).
                    Applique uniquement ces changements sur le reste de la scène : {user_text}.
                    
                    RÉSULTAT :
                    Donne un PROMPT_ULTIME_POSITIF (en anglais technique, 8k, photorealistic)
                    et un PROMPT_ULTIME_NÉGATIF (pour bannir les déformations faciales).
                    """
                    
                    with st.spinner("Analyse faciale et rédaction du prompt..."):
                        try:
                            response = model.generate_content([system_prompt, image])
                            st.markdown("### ✨ Votre Prompt de Retouche")
                            # Bouton de copie automatique intégré au bloc de code
                            st.code(response.text, language="markdown")
                            st.success("✅ Cliquez en haut à droite du bloc gris pour copier.")
                        except Exception as e:
                            st.error(f"Erreur IA : {e}")
                else:
                    st.warning("Veuillez décrire les modifications souhaitées.")

        with col2:
            if st.button("🔄 CHANGER DE PHOTO"):
                clear_photo()

    except Exception as e:
        st.error(f"Erreur lors du chargement de l'image : {e}")

else:
    st.info("Sélectionnez une photo pour commencer. L'IA conservera l'identité du visage à 100%.")

st.markdown("---")
st.caption("Application de retouche optimisée - Maître Ingénieur Prompt 2026")
