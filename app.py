
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import BytesIO
from datetime import datetime
import time
import uuid

# Configuração da página
st.set_page_config(page_title="Upload Power BI", page_icon="📊", layout="wide")

# Criar pastas se não existirem
if not os.path.exists("uploads"):
    os.makedirs("uploads")
if not os.path.exists("base_geral"):
    os.makedirs("base_geral")

# Corpo principal
col1, col2 = st.columns([2, 3])
with col1:
    st.title("📊 Upload de Dados")
with col2:
    

# Session State para histórico
if 'upload_history' not in st.session_state:
    st.session_state.upload_history = []

if uploaded_file:
    file_ext = uploaded_file.name.split('.')[-1].lower()

    # Ler arquivo
    if file_ext == 'csv':
        df = pd.read_csv(uploaded_file)
    else:
        sheets = pd.ExcelFile(uploaded_file).sheet_names
        if len(sheets) > 1:
            sheet = st.selectbox("Selecione a aba da planilha:", sheets)
        else:
            sheet = sheets[0]
        df = pd.read_excel(uploaded_file, sheet_name=sheet)

    # Mostrar preview
    st.subheader("🔍 Preview dos Dados")
    st.dataframe(df.head(5), use_container_width=True, height=200)

    # Botão para confirmar upload
    if st.button("✅ Confirmar Upload e Tratar Dados"):
        with st.spinner('Processando arquivo...'):
            time.sleep(1.5)
            file_id = str(uuid.uuid4())[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_name = f"{timestamp}_{file_id}.{file_ext}"
            save_path = os.path.join("uploads", save_name)

            # Salvar arquivo bruto
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Salvar no histórico
            st.session_state.upload_history.append({
                "file": uploaded_file.name,
                "saved_as": save_name,
                "time": datetime.now().strftime("%d/%m/%Y %H:%M")
            })

            # Validação
            required_cols = ['RESPONSÁVEL', 'TMO - Total']
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                st.error(f"🚫 Faltando colunas obrigatórias: {', '.join(missing_cols)}")
            else:
                # Tratamento
                df['RESPONSÁVEL'] = df['RESPONSÁVEL'].astype(str).str.capitalize()
                df['TMO - Total'] = pd.to_numeric(df['TMO - Total'], errors='coerce')

                st.success('🎯 Dados tratados com sucesso! Vamos para a análise.')

                                st.subheader("📊 Análise")

                # Cards de Métricas
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="💰 Total TMO (R$)", value=f"R$ {df['TMO - Total'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                with col2:
                    st.metric(label="📈 Total de Registros", value=len(df))

                # Gráfico
                vendas = df.groupby('RESPONSÁVEL')['TMO - Total'].sum().reset_index()
                fig = px.bar(
                    vendas,
                    x='RESPONSÁVEL',
                    y='TMO - Total',
                    text_auto='.2s',
                    template="simple_white",
                    color_discrete_sequence=["#004aad"]
                )
                fig.update_traces(marker_line_width=1.5, marker_line_color="white")
                fig.update_layout(
                    title="TMO por Responsável",
                    xaxis_title="Responsável",
                    yaxis_title="Valor TMO (R$)",
                    title_x=0.5,
                    bargap=0.4
                )
                st.plotly_chart(fig, use_container_width=True)

                # Simular envio para base geral
                output_path = os.path.join("base_geral", f"tratado_{save_name}")
                df.to_excel(output_path, index=False)

                st.success(f"🚀 Arquivo tratado enviado para a base consolidada!")

# Mostrar Histórico
if st.session_state.upload_history:
        st.subheader("🗓 Histórico da Sessão")
    for item in st.session_state.upload_history[::-1]:
        st.write(f"**{item['file']}** salvo como **{item['saved_as']}** em {item['time']}")

# Visualizar Base Geral
st.subheader("📁 Base Geral")
base_files = os.listdir("base_geral")
if base_files:
    for file in base_files:
        with open(os.path.join("base_geral", file), "rb") as f:
            st.download_button(
                label=f"📂 Baixar {file}",
                data=f,
                file_name=file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.info("Nenhum arquivo encontrado na base geral.")

# Rodapé

