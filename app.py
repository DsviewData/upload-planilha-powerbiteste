
import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px
import os
from datetime import datetime
import time
import uuid

st.set_page_config(page_title="Upload de Planilhas Power BI", page_icon="📊", layout="centered")

# Estilo customizado
st.markdown(
    """
    <style>
    .title {color: #0057b7; font-size: 38px; text-align: center;}
    .subtitle {color: #5a5a5a; font-size: 20px; text-align: center; margin-bottom: 30px;}
    .metric-card {background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;}
    .stButton>button {
        background-color: #0057b7;
        color: white;
        border-radius: 10px;
        padding: 0.5em 1em;
        font-size: 16px;
    }
    .footer {color: #999; font-size: 13px; text-align: center; margin-top: 50px;}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 class="title">📊 Plataforma de Upload e Integração de Planilhas</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Envie e integre seus dados para análise no Power BI</p>', unsafe_allow_html=True)

page = st.sidebar.selectbox("📄 Navegar:", ["🏠 Início", "📂 Upload e Integração"])

if page == "🏠 Início":
    st.header("🚀 Bem-vindo!")
    st.write("""
    Esta plataforma permite enviar planilhas Excel (.xlsx), integrá-las simuladamente em um servidor de dados e preparar para análise no Power BI.

    **Funcionalidades:**  
    - Upload de múltiplos arquivos.  
    - Simulação de envio para servidor de dados.  
    - Visualização e tratamento de dados.  
    - Geração de métricas e gráficos.

    Selecione **Upload e Integração** no menu lateral para começar!
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/201/201623.png", width=250)

elif page == "📂 Upload e Integração":
    uploaded_files = st.file_uploader("**📂 Envie suas planilhas Excel (.xlsx)**", type=["xlsx"], accept_multiple_files=True)

    if uploaded_files:
        if not os.path.exists("uploads"):
            os.makedirs("uploads")

        for uploaded_file in uploaded_files:
            st.divider()
            st.header(f"📄 {uploaded_file.name}")

            try:
                with st.spinner('🚀 Enviando arquivo para o servidor de dados...'):
                    time.sleep(2)  # Simula tempo de upload
                    file_id = str(uuid.uuid4())[:8]
                    save_path = os.path.join("uploads", f"{file_id}_{uploaded_file.name}")
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    upload_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                st.success(f"✅ Arquivo '{uploaded_file.name}' armazenado com sucesso no servidor!")
                st.info(f"🆔 ID do Upload: {file_id} | 📅 Data/Hora: {upload_time}")

                df = pd.read_excel(uploaded_file)
                st.subheader('🔍 Dados Recebidos')
                st.dataframe(df, use_container_width=True)

                required_cols = ['RESPONSÁVEL', 'TMO - Total']
                missing_cols = [col for col in required_cols if col not in df.columns]

                if missing_cols:
                    st.error(f"🚫 Faltando colunas obrigatórias: {', '.join(missing_cols)}")
                else:
                    df['RESPONSÁVEL'] = df['RESPONSÁVEL'].str.capitalize()
                    df['TMO - Total'] = pd.to_numeric(df['TMO - Total'], errors='coerce')

                    st.success('🎯 Dados tratados com sucesso!')

                    st.divider()
                    st.subheader('📈 Relatório Visual')

                    # Cards com métricas
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('<div class="metric-card"><h3>Total de Vendas (R$)</h3><p style="font-size:26px;">{:,.2f}</p></div>'.format(df['TMO - Total'].sum()).replace(",", "X").replace(".", ",").replace("X", "."), unsafe_allow_html=True)
                    with col2:
                        st.markdown('<div class="metric-card"><h3>Quantidade de Registros</h3><p style="font-size:26px;">{}</p></div>'.format(len(df)), unsafe_allow_html=True)

                    st.divider()

                    vendas_por_regiao = df.groupby('Reponsável')['TMO - Total'].sum().reset_index()
                    fig = px.bar(vendas_por_regiao, x='Reponsável', y='TMO - Total', text_auto=True, template="simple_white")
                    fig.update_traces(marker_color="#0057b7")
                    fig.update_layout(title="Vendas por Responsável", xaxis_title="Responsável", yaxis_title="Valor da Venda (R$)", title_x=0.5)
                    st.plotly_chart(fig, use_container_width=True)

                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)

                    st.download_button(
                        label="📥 Baixar Planilha Tratada",
                        data=output.getvalue(),
                        file_name=f"tratado_{uploaded_file.name}",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            except Exception as e:
                st.error(f"❌ Erro ao processar o arquivo: {e}")

st.markdown('<p class="footer">Desenvolvido com ❤️ por Daniel Netto | Integração Simulada de Dados</p>', unsafe_allow_html=True)
