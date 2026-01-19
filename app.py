import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Sécurité
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("Clé API manquante dans les Secrets")
    st.stop()

st.title("📸 Master Retouche Identité")

# 2. LA SOLUTION : On utilise le décorateur @st.fragment (si dispo) ou on simplifie le flux
# On vide le cache à chaque exécution pour éviter le blocage Android
st.cache_data.clear()

uploaded_file = st.file_uploader("Sélectionnez la photo", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # On utilise un conteneur vide pour forcer l'affichage en haut
    placeholder = st.empty()
    
    # Lecture des données brutes (plus rapide sur mobile)
    data = uploaded_file.read()
    image = Image.open(io.BytesIO(data))
    
    # Affichage immédiat
    placeholder.image(image, use_container_width=True)
    
    user_text = st.text_input("Modifications (ex: blond, bijoux...)", key="mod_input")

    if st.button("GÉNÉRER LE PROMPT", type="primary"):
        if user_text:
            model = genai.GenerativeModel('gemini-2.5-flash')
            # Instruction STRICTE pour le visage
            instruction = f"CONSIGNE : Garde le visage à 100%. MODIFS : {user_text}. Donne le prompt positif et négatif."
            
            with st.spinner("Analyse en cours..."):
                # On repasse l'image à l'IA
                response = model.generate_content([instruction, image])
                st.code(response.text)
        else:
            st.warning("Écris tes modifs !")
