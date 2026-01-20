import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Config logicielle ultra-rapide
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Retouche Fix", layout="centered")

# Fonction pour forcer le nettoyage si ça bug
def reset_session():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

st.title("📸 Retouche Haute Fidélité")

# 2. Utilisation d'un FORMULAIRE pour stabiliser l'envoi sur Android
with st.form("upload_form", clear_on_submit=False):
    uploaded_file = st.file_uploader("Choisir une photo (Galerie/Dossiers)", type=['jpg', 'jpeg', 'png'])
    user_text = st.text_input("Modifications (ex: blond, plage...)")
    submit_button = st.form_submit_button("🚀 CHARGER ET GÉNÉRER")

# 3. Traitement après soumission du formulaire
if submit_button:
    if uploaded_file is not None and user_text != "":
        try:
            # On traite tout d'un coup pour éviter les déconnexions entre étapes
            image_bytes = uploaded_file.read()
            image = Image.open(io.BytesIO(image_bytes))
            
            # Affichage
            st.image(image, caption="Photo reçue", use_container_width=True)
            
            # IA
            model = genai.GenerativeModel('gemini-2.5-flash')
            instruction = f"CONSIGNE : Garde le visage à 100%. MODIFS : {user_text}. Prompt positif/négatif en anglais."
            
            with st.spinner("Analyse faciale..."):
                response = model.generate_content([instruction, image])
                st.markdown("### ✨ Résultat :")
                st.code(response.text)
                
        except Exception as e:
            st.error("La connexion a sauté. Réessayez avec le bouton Reset en bas.")
    else:
        st.warning("Photo ET texte obligatoires.")

st.markdown("---")
if st.button("♻️ RESET COMPLET (Si l'app tourne en rond)"):
    reset_session()
