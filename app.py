import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Upload de Planilha", layout="wide")
st.title("📤 Upload de Planilha Excel")

# Criar pasta de uploads
upload_dir = "uploads"
os.makedirs(upload_dir, exist_ok=True)

# Listar arquivos já enviados com botão de download
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

# Upload de novo arquivo
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
            file_path = os.path.join(upload_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("📤 Arquivo enviado e salvo com sucesso!")

            # Atualizar lista com botões de download
            st.subheader("📂 Arquivos atualizados:")
            updated_files = os.listdir(upload_dir)
            for file in updated_files:
                path = os.path.join(upload_dir, file)
                with open(path, "rb") as f:
                    st.download_button(
                        label=f"⬇️ Baixar {file}",
                        data=f,
                        file_name=file,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")
