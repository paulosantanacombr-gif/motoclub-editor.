import streamlit as st
from PIL import Image, ImageEnhance
import google.generativeai as genai
import io
import json

# --- CONFIGURAÇÃO ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Configure a API Key nos 'Secrets' do Streamlit!")
    st.stop()

# MODELO 2025 (Oficial e Estável)
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="MotoClub Pro", page_icon="🏍️", layout="centered")

# Visual Dark Mode
st.markdown("""
    <style>
    .stApp { background-color: #0e0e0e; color: #f0f0f0; }
    .stButton>button { background-color: #D2B48C; color: #000; font-weight: bold; border-radius: 8px; height: 50px; width: 100%; border:none; }
    div[data-testid="stFileUploader"] { background-color: #1a1a1a; border: 1px solid #333; padding: 20px; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏍️ MotoClub Editor 2.5")

uploaded_file = st.file_uploader("Enviar Foto", type=['jpg', 'png', 'jpeg'])
prompt = st.text_area("Instruções:", "Estilo Café Racer: nitidez comercial, contraste marcante e cores vibrantes.")

if uploaded_file and st.button("⚡ PROCESSAR AGORA"):
    with st.spinner('A IA está analisando os pixels...'):
        try:
            image = Image.open(uploaded_file).convert('RGB')
            buf = io.BytesIO()
            image.save(buf, format='JPEG')
            
            # --- O PULO DO GATO: FORÇAR JSON ---
            response = model.generate_content(
                [
                    {'mime_type': 'image/jpeg', 'data': buf.getvalue()},
                    f"Atue como editor de imagem. Pedido: {prompt}. Retorne JSON com chaves: brightness, contrast, saturation, sharpness (float, 1.0 é neutro)."
                ],
                generation_config={"response_mime_type": "application/json"}
            )
            
            # Debug: Se a IA falhar, mostraremos o texto real
            try:
                filtros = json.loads(response.text)
            except ValueError:
                st.error("A IA respondeu texto em vez de código. Veja abaixo:")
                st.write(response.text)
                st.stop()
            
            # Aplicação
            edit = image
            if 'brightness' in filtros: edit = ImageEnhance.Brightness(edit).enhance(filtros['brightness'])
            if 'contrast' in filtros: edit = ImageEnhance.Contrast(edit).enhance(filtros['contrast'])
            if 'saturation' in filtros: edit = ImageEnhance.Color(edit).enhance(filtros['saturation'])
            if 'sharpness' in filtros: edit = ImageEnhance.Sharpness(edit).enhance(filtros['sharpness'])
            
            # Antes/Depois
            col1, col2 = st.columns(2)
            with col1: st.image(image, caption='Original', use_container_width=True)
            with col2: st.image(edit, caption='Editada IA', use_container_width=True)
            
            st.success(f"Ajustes usados: {filtros}")
            
            # Download
            buf_out = io.BytesIO()
            edit.save(buf_out, format="JPEG", quality=95)
            st.download_button("💾 BAIXAR FOTO", data=buf_out.getvalue(), file_name="motoclub_final.jpg", mime="image/jpeg")
            
        except Exception as e:
            st.error(f"Erro Técnico: {e}")
