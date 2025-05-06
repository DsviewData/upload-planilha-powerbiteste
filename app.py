import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Upload de Planilha", layout="wide")
st.title("📤 Upload de Planilha Excel")

# 🧑 Usuário (futuramente você pode trocar isso por autenticação real)
usuario = "daniel"  # Pode ser alterado ou vindo de login futuramente

# 📂 Diretório com subpastas por usuário e data
hoje = datetime.now().strftime("%Y-%m-%d")
upload_dir = os.path.join("uploads", usuario, hoje)
os.makedirs(upload_dir, exist_ok=True)

# Listar arquivos enviados
st.subheader("📂 Arquivos já enviados:")
files = os.listdir(upload_dir)
if files:
    for file in files:
        file_path = os.path.join(upload_dir, file)
        with open(file_path, "rb") as f:
            st.download_button(
                label=f"⬇️ Baixar {file}",
                data=f,
                file_name=file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.info("Nenhum arquivo enviado ainda.")

# Upload
uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])

if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        sheets = xls.sheet_names
        sheet = st.selectbox("Selecione a aba da planilha:", sheets) if len(sheets) > 1 else sheets[0]
        df = pd.read_excel(uploaded_file, sheet_name=sheet)

        st.subheader("🔍 Preview das Primeiras 5 Linhas")
        st.dataframe(df.head(5), use_container_width=True, height=200)

        if st.button("📧 Enviar"):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            filename = f"{uploaded_file.name.split('.')[0]}_{timestamp}.xlsx"
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("📤 Arquivo enviado e salvo com sucesso!")

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")
