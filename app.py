import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. SÉCURITÉ & CONFIGURATION ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("❌ Configuration manquante : Ajoutez GEMINI_API_KEY dans les Secrets.")
    st.stop()

st.set_page_config(page_title="Retouche IA Haute Fidélité", layout="centered")
st.title("📸 Expert Retouche & Consistance")

# Sélection du modèle
model_id = "models/gemini-2.5-flash" # Modèle de 2026 ultra-précis

# --- 2. INTERFACE ---
uploaded_file = st.file_uploader("Sélectionnez la photo originale", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Référence originale (Identité source)", use_container_width=True)
    
    user_text = st.text_area("🔧 Modifications de l'environnement / style :", 
                             placeholder="Ex: Rendre blond, ajouter des bijoux en or, décor de plage paradisiaque...")

    if st.button("GÉNÉRER LE PROMPT DE RETOUCHE", type="primary"):
        if user_text:
            model = genai.GenerativeModel(model_id)
            
            # LOGIQUE D'EXPERTISE ACCENTUÉE SUR LE VISAGE
            system_instruction = f"""
            Tu es un Ingénieur Expert en 'Face Consistency' pour IA générative.
            
            ANALYSE PRIORITAIRE :
            - Analyse mathématique et visuelle du visage sur l'IMAGE : structure osseuse, forme des yeux, commissures des lèvres.
            
            MISSION DE RÉDACTION :
            - Créer un prompt où le visage est décrit comme 'Identique à la source, aucune modification des traits faciaux'.
            - Appliquer les modifications demandées : {user_text}.
            
            STRUCTURE DU PROMPT :
            - Utilise 'Photorealistic face mapping' et 'Zero facial alteration'.
            - Décris les nouveaux éléments (cheveux, bijoux, décor) avec une précision chirurgicale.
            - Format : PROMPT_ULTIME_POSITIF et PROMPT_ULTIME_NÉGATIF.
            """
            
            with st.spinner("Analyse faciale et calcul des modifications..."):
                try:
                    response = model.generate_content([system_instruction, image])
                    st.markdown("### 🛠 Votre Prompt de Retouche Optimisé")
                    
                    # Bloc de copie automatique
                    st.code(response.text, language="markdown")
                    
                    st.info("ℹ️ Copiez ce texte dans votre générateur d'images (Flux, Midjourney, etc.) pour obtenir le résultat.")
                except Exception as e:
                    st.error(f"Erreur : {e}")
