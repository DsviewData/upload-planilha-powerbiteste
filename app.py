
import streamlit as st
import pandas as pd
import os
import requests
from msal import ConfidentialClientApplication
from datetime import datetime

# === CONFIGURAÇÕES SEGURAS ===
CLIENT_ID = "f9c5914b-2940-4edf-8364-1178052836ce"
CLIENT_SECRET = "4gx8Q~F4-zmN-NNgPlGWLNW.M4LvEr.WL4xCaaRj"
TENANT_ID = "6e1d8e0e-e910-48dc-80d2-112fc3cf3a7d"
PASTA_ONEDRIVE = "ProjetosBI/Limpar Auto/fontededados/dados_geral/faturamento"

# === AUTENTICAÇÃO ===
def obter_token():
    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return result.get("access_token")

# === RENOMEAR ARQUIVO EXISTENTE SE PRECISO ===
def mover_arquivo_existente(nome_arquivo, token):
    search_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{PASTA_ONEDRIVE}/{nome_arquivo}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(search_url, headers=headers)

    if response.status_code == 200:
        file_id = response.json()['id']
        timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%M")
        novo_nome = nome_arquivo.replace(".xlsx", f"_backup_{timestamp}.xlsx")
        patch_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}"
        patch_body = {
            "name": novo_nome
        }
        patch_response = requests.patch(
            patch_url,
            headers={**headers, "Content-Type": "application/json"},
            json=patch_body
        )
        return patch_response.status_code in [200, 204]
    return True  # Se não existe, segue o fluxo

# === UPLOAD PARA ONEDRIVE ===
def upload_onedrive(nome_arquivo, conteudo_arquivo, token):
    mover_arquivo_existente(nome_arquivo, token)  # Tenta renomear antes de sobrescrever
    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{PASTA_ONEDRIVE}/{nome_arquivo}:/content"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream"
    }
    response = requests.put(url, headers=headers, data=conteudo_arquivo)
    return response.status_code in [200, 201]

# === STREAMLIT UI ===
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

        if st.button("📧 Enviar para OneDrive"):
            with st.spinner("Enviando para o OneDrive..."):
                token = obter_token()
                if not token:
                    st.error("❌ Erro ao obter token. Verifique as credenciais.")
                else:
                    sucesso = upload_onedrive(uploaded_file.name, uploaded_file.getbuffer(), token)
                    if sucesso:
                        st.success("✅ Arquivo enviado com sucesso para o OneDrive!")
                    else:
                        st.error("❌ Falha ao enviar o arquivo. Verifique se o caminho da pasta está correto.")

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")
