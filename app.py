import streamlit as st
import pandas as pd

st.set_page_config(page_title="Upload de Planilha", layout="wide")
st.title("📤 Upload de Planilha Excel")

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
            st.success("📤 Arquivo enviado com sucesso!")

    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
