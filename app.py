
import streamlit as st
import pandas as pd
from io import BytesIO

# Configuração da página
st.set_page_config(page_title="Upload de Planilhas para Power BI", page_icon="📊", layout="centered")

# Estilo visual
st.markdown(
    """
    <style>
    .title {color: #0078d4; font-size: 40px;}
    .subtitle {color: #fabd00; font-size: 24px;}
    .stButton>button {
        background-color: #0078d4;
        color: white;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Cabeçalho
st.markdown('<p class="title">📊 Upload de Planilhas para Power BI</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Envie seus arquivos Excel e prepare seus dados para análise!</p>', unsafe_allow_html=True)

# Upload de múltiplos arquivos
uploaded_files = st.file_uploader("**Envie uma ou mais planilhas (.xlsx)**", type=["xlsx"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.divider()
        st.header(f"📄 {uploaded_file.name}")

        # Lê a planilha
        df = pd.read_excel(uploaded_file)

        # Exibe os dados originais
        st.subheader('🔍 Dados Recebidos')
        st.dataframe(df)

        # Simulação de tratamento
        st.subheader('🛠️ Tratamento dos Dados')

        if 'Região' in df.columns:
            df['Região'] = df['Região'].str.capitalize()

        if 'Valor da Venda' in df.columns:
            df['Valor da Venda'] = pd.to_numeric(df['Valor da Venda'], errors='coerce')

        # Exibe os dados tratados
        st.dataframe(df)

        # Download do arquivo tratado
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        st.download_button(
            label="📥 Baixar Planilha Tratada",
            data=output.getvalue(),
            file_name=f"tratado_{uploaded_file.name}",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success('✅ Tratamento concluído! Planilha pronta para o Power BI.')
