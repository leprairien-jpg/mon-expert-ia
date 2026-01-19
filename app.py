import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. SÉCURITÉ ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("❌ Configuration manquante : Ajoutez GEMINI_API_KEY dans les Secrets.")
    st.stop()

st.set_page_config(page_title="Universal Prompt Engine", layout="centered")
st.title("🔬 Maître Ingénieur Multimodal")

# --- 2. LOGIQUE DE SÉLECTION DU MODÈLE ---
try:
    # On force l'utilisation du 2.5 Flash s'il est dispo, sinon le 1.5
    available = [m.name for m in genai.list_models()]
    model_id = "models/gemini-2.5-flash" if "models/gemini-2.5-flash" in available else "models/gemini-1.5-flash"
except:
    model_id = "gemini-1.5-flash"

# --- 3. INTERFACE ---
uploaded_file = st.file_uploader("📸 Choisissez une photo (Galerie)", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    # On s'assure que l'image est chargée proprement
    image = Image.open(uploaded_file)
    st.image(image, caption="Référence chargée", use_container_width=True)
    
    user_text = st.text_area("🔧 Modifications souhaitées :", placeholder="Ex: Rendre blond, ajouter des bijoux, changer le fond...")

    if st.button("GÉNÉRER L'INGÉNIERIE", type="primary"):
        if user_text:
            model = genai.GenerativeModel(model_id)
            
            # CONSIGNE STRICTE : Préservation de l'identité
            system_instruction = f"""
            Tu es un Maître Ingénieur en Prompt. 
            ANALYSE : Étudie précisément les traits faciaux, l'ossature et l'identité de la personne sur l'IMAGE.
            MISSION : Créer un prompt pour une IA génératrice d'image.
            CONDITION CRITIQUE : Le visage doit être conservé à 100%. L'identité doit être immédiatement reconnaissable.
            MODIFICATIONS À APPLIQUER : {user_text}.
            
            FORMAT DE RÉPONSE :
            Donne uniquement le PROMPT_ULTIME_POSITIF et le PROMPT_ULTIME_NÉGATIF.
            Utilise des termes techniques (8k, photorealistic, cinematic lighting, focal length 85mm).
            """
            
            with st.spinner("Analyse et protection de l'identité..."):
                try:
                    response = model.generate_content([system_instruction, image])
                    st.markdown("### ✨ Résultat de l'Expertise")
                    
                    # Utilisation de st.code pour permettre la copie facile (bouton intégré)
                    st.code(response.text, language="markdown")
                    
                    st.info("💡 Cliquez sur l'icône en haut à droite du bloc gris pour copier le prompt.")
                except Exception as e:
                    st.error(f"Erreur : {e}")
        else:
            st.warning("Précisez les modifications voulues.")

