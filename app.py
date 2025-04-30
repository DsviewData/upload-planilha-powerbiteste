import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Upload de Planilha", layout="wide")
st.title("📤 Upload de Planilha Excel")

# Criar pasta de destino, se não existir
output_dir = "planilhas_enviadas"
os.makedirs(output_dir, exist_ok=True)

uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])

if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        sheets = xls.sheet_names
        if len(sheets) > 1:
            sheet = st.selectbox("Selecione a aba da planilha:", sheets)
        else:
            sheet = sheets[0]
        df = pd.read_excel(uploaded_file, sheet_name=sheet)

        st.subheader("🔍 Preview das Primeiras 5 Linhas")
        st.dataframe(df.head(5), use_container_width=True, height=200)

        if st.button("📧 Enviar"):
            file_path = os.path.join(output_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("📤 Arquivo enviado e salvo com sucesso!")

    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
