import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Configuration ultra-légère
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Retouche Rapide", layout="centered")

# Bouton de secours pour vider la mémoire
if st.sidebar.button("♻️ Reset"):
    st.cache_data.clear()
    st.rerun()

st.title("📸 Master Retouche")

# 2. Uploader direct sans fioritures
# On enlève tout ce qui pourrait ralentir Android
uploaded_file = st.file_uploader("Choisir photo", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    try:
        # Affichage immédiat du flux brut
        st.image(uploaded_file, use_container_width=True)
        
        user_text = st.text_input("Modifications :", placeholder="ex: blond, plage...")

        if st.button("🚀 GÉNÉRER"):
            if user_text:
                model = genai.GenerativeModel('gemini-2.5-flash')
                # On ouvre l'image seulement ici pour économiser la mémoire
                img = Image.open(uploaded_file)
                
                with st.spinner("Analyse..."):
                    instruction = f"CONSIGNE : Garde le visage à 100%. MODIFS : {user_text}. Prompt positif/négatif en anglais."
                    response = model.generate_content([instruction, img])
                    st.code(response.text)
            else:
                st.warning("Écris tes modifs !")
    except Exception as e:
        st.error("Connexion perdue. Réactualise la page.")
