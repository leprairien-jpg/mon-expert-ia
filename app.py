import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURATION SÉCURISÉE ---
# Ta clé est intégrée ici, mais pense à utiliser les Secrets Streamlit plus tard
API_KEY = "AIzaSyC76UhzkSGVJ2S4IhjULgVm3HwAqkZa5ag" 
genai.configure(api_key=API_KEY)

# Configuration de l'interface
st.set_page_config(page_title="Prompt Master Pro", layout="centered")

st.title("🚀 Prompt Master Engineering")
st.write("Expert IA Multimodal pour la génération de prompts optimisés")

# --- ZONE D'UPLOAD ---
uploaded_file = st.file_uploader("Choisissez une photo de référence (JPG, PNG)", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # Lecture et affichage de l'image
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Image source détectée", use_container_width=True)
        
        user_text = st.text_input("Votre concept de base :", placeholder="Ex: Un guerrier cyberpunk dans une ruelle...")

        if st.button("GÉNÉRER L'EXPERTISE", type="primary"):
            if user_text:
                # Utilisation du modèle flash-latest pour éviter l'erreur 404
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                # Instruction structurée pour l'Expert IA
                instruction = """Tu es un Maître Ingénieur en Prompt Multimodal. 
                Analyse l'IMAGE et le TEXTE fournis. 
                Génère deux sections précises :
                
                1. PROMPT_ULTIME_POSITIF : Une description ultra-détaillée intégrant le style visuel de l'image, 
                les réglages de caméra (f/1.8, 85mm), l'éclairage cinématique et les textures.
                
                2. PROMPT_ULTIME_NÉGATIF : Une liste de mots-clés pour éviter les déformations, le flou et les erreurs d'IA.
                
                Réponds en français avec une structure claire."""
                
                with st.spinner("Analyse technique en cours..."):
                    try:
                        # Appel à l'IA avec le modèle mis à jour
                        response = model.generate_content([instruction, image, user_text])
                        
                        st.success("Analyse terminée !")
                        st.markdown("---")
                        # Affichage du résultat
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"Erreur lors de la génération : {e}")
                        st.info("Astuce : Vérifiez que votre quota API n'est pas dépassé.")
            else:
                st.warning("⚠️ Veuillez saisir un texte pour guider l'IA.")
    except Exception as e:
        st.error(f"Erreur de chargement de l'image : {e}")

else:
    st.info("📸 Veuillez uploader une image pour commencer l'analyse.")
