import streamlit as st
from PIL import Image, ImageEnhance
import google.generativeai as genai
import io
import json

# --- CONFIGURAÇÃO DE SEGURANÇA (NUVEM) ---
try:
    # Tenta pegar a chave dos segredos do Streamlit
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ ERRO: API Key não configurada! Vá nas configurações do Streamlit Cloud > Secrets.")
    st.stop()

# Configura o modelo
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="MotoClub Mobile", page_icon="🏍️", layout="centered")

# Estilo CSS para parecer App Nativo Escuro
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #e0e0e0; }
    .stButton>button { 
        background-color: #D2B48C; color: #000; 
        font-weight: bold; border-radius: 12px; 
        height: 55px; width: 100%; font-size: 18px; border: none;
    }
    div[data-testid="stFileUploader"] { 
        background-color: #1e1e1e; border: 1px solid #333; border-radius: 10px; padding: 15px;
    }
    h1 { color: #D2B48C !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏍️ MotoClub Editor")

# --- INTERFACE ---
uploaded_file = st.file_uploader("Toque para enviar foto", type=['jpg', 'png', 'jpeg'])
prompt = st.text_area("Instruções:", "Estilo Café Racer: nitidez alta, contraste comercial e cores vibrantes.")

if uploaded_file and st.button("⚡ PROCESSAR FOTO"):
    with st.spinner('Processando na nuvem...'):
        try:
            # 1. Carregar
            image = Image.open(uploaded_file).convert('RGB')
            
            # 2. Enviar para IA
            buf = io.BytesIO()
            image.save(buf, format='JPEG')
            
            response = model.generate_content([
                {'mime_type': 'image/jpeg', 'data': buf.getvalue()},
                f"Atue como editor. Pedido: {prompt}. Retorne JSON para Pillow: brightness, contrast, saturation, sharpness (float, 1.0 neutro)."
            ])
            
            # 3. Aplicar Filtros
            filtros = json.loads(response.text.replace('```json','').replace('```','').strip())
            
            edit = image
            if 'brightness' in filtros: edit = ImageEnhance.Brightness(edit).enhance(filtros['brightness'])
            if 'contrast' in filtros: edit = ImageEnhance.Contrast(edit).enhance(filtros['contrast'])
            if 'saturation' in filtros: edit = ImageEnhance.Color(edit).enhance(filtros['saturation'])
            if 'sharpness' in filtros: edit = ImageEnhance.Sharpness(edit).enhance(filtros['sharpness'])
            
            # 4. Resultado
            st.image(edit, caption='Resultado', use_container_width=True)
            
            # Download
            buf_out = io.BytesIO()
            edit.save(buf_out, format="JPEG", quality=95)
            st.download_button("💾 BAIXAR AGORA", data=buf_out.getvalue(), file_name="editada_motoclub.jpg", mime="image/jpeg")
            
        except Exception as e:
            st.error(f"Erro: {e}")
