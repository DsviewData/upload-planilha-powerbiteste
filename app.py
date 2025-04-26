
import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px

st.set_page_config(page_title="Plataforma de Upload Power BI", page_icon="📊", layout="centered")

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

st.markdown('<h1 class="title">📊 Plataforma de Upload de Planilhas</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Organize e trate seus dados para o Power BI com facilidade</p>', unsafe_allow_html=True)

page = st.sidebar.selectbox("📄 Navegar:", ["🏠 Início", "📂 Upload de Planilhas"])

if page == "🏠 Início":
    st.header("🚀 Bem-vindo!")
    st.write("""
    Este aplicativo permite que você envie suas planilhas Excel (.xlsx), visualize os dados, aplique tratamentos automáticos e baixe o arquivo pronto para análise.

    **Funcionalidades:**  
    - Upload de múltiplos arquivos.  
    - Visualização limpa dos dados.  
    - Tratamento inteligente de campos padrão.  
    - Resumo visual com métricas e gráficos.

    Selecione **Upload de Planilhas** no menu à esquerda para começar!
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/201/201623.png", width=250)

elif page == "📂 Upload de Planilhas":
    uploaded_files = st.file_uploader("**📂 Envie suas planilhas Excel (.xlsx)**", type=["xlsx"], accept_multiple_files=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.divider()
            st.header(f"📄 {uploaded_file.name}")

            try:
                df = pd.read_excel(uploaded_file)
                st.subheader('🔍 Dados Recebidos')
                st.dataframe(df, use_container_width=True)

                required_cols = ['Região', 'Valor da Venda']
                missing_cols = [col for col in required_cols if col not in df.columns]

                if missing_cols:
                    st.error(f"🚫 Faltando colunas obrigatórias: {', '.join(missing_cols)}")
                else:
                    df['Região'] = df['Região'].str.capitalize()
                    df['Valor da Venda'] = pd.to_numeric(df['Valor da Venda'], errors='coerce')

                    st.success('🎯 Dados tratados com sucesso!')

                    st.divider()
                    st.subheader('📈 Relatório Visual')

                    # Cards com métricas
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('<div class="metric-card"><h3>Total de Vendas (R$)</h3><p style="font-size:26px;">{:,.2f}</p></div>'.format(df['Valor da Venda'].sum()).replace(",", "X").replace(".", ",").replace("X", "."), unsafe_allow_html=True)
                    with col2:
                        st.markdown('<div class="metric-card"><h3>Quantidade de Registros</h3><p style="font-size:26px;">{}</p></div>'.format(len(df)), unsafe_allow_html=True)

                    st.divider()

                    vendas_por_regiao = df.groupby('Região')['Valor da Venda'].sum().reset_index()
                    fig = px.bar(vendas_por_regiao, x='Região', y='Valor da Venda', text_auto=True, template="simple_white")
                    fig.update_traces(marker_color="#0057b7")
                    fig.update_layout(title="Vendas por Região", xaxis_title="Região", yaxis_title="Valor da Venda (R$)", title_x=0.5)
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

st.markdown('<p class="footer">Desenvolvido com ❤️ por Daniel Netto | Plataforma Clean Moderno</p>', unsafe_allow_html=True)
