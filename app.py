import streamlit as st
import pandas as pd
import os
import requests
from msal import ConfidentialClientApplication
from datetime import datetime

# === CREDENCIAIS via st.secrets (para Streamlit Cloud) ===
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
TENANT_ID = st.secrets["TENANT_ID"]
EMAIL_ONEDRIVE = st.secrets["EMAIL_ONEDRIVE"]
PASTA_ONEDRIVE = "uploads"

def obter_token():
    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return result.get("access_token")

def mover_arquivo_existente(nome_arquivo, token):
    url = f"https://graph.microsoft.com/v1.0/users/{EMAIL_ONEDRIVE}/drive/root:/{PASTA_ONEDRIVE}/{nome_arquivo}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_id = response.json().get("id")
        timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%M")
        novo_nome = nome_arquivo.replace(".xlsx", f"_backup_{timestamp}.xlsx")
        patch_url = f"https://graph.microsoft.com/v1.0/users/{EMAIL_ONEDRIVE}/drive/items/{file_id}"
        patch_body = {"name": novo_nome}
        patch_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        requests.patch(patch_url, headers=patch_headers, json=patch_body)

def upload_onedrive(nome_arquivo, conteudo_arquivo, token):
    mover_arquivo_existente(nome_arquivo, token)
    url = f"https://graph.microsoft.com/v1.0/users/{EMAIL_ONEDRIVE}/drive/root:/{PASTA_ONEDRIVE}/{nome_arquivo}:/content"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream"
    }
    response = requests.put(url, headers=headers, data=conteudo_arquivo)
    st.text(f"Status: {response.status_code}")
    st.text(f"Resposta: {response.text}")
    return response.status_code in [200, 201]

st.set_page_config(page_title="Upload para OneDrive com st.secrets", layout="wide")
st.title("📤 Upload Seguro com Backup no OneDrive (Streamlit Cloud)")

uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])
if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        sheets = xls.sheet_names
        sheet = st.selectbox("Selecione a aba:", sheets) if len(sheets) > 1 else sheets[0]
        df = pd.read_excel(uploaded_file, sheet_name=sheet)
        st.dataframe(df.head(5), use_container_width=True, height=200)
        if st.button("📧 Enviar"):
            with st.spinner("Enviando..."):
                token = obter_token()
                if not token:
                    st.error("Erro ao obter token.")
                else:
                    sucesso = upload_onedrive(uploaded_file.name, uploaded_file.getbuffer(), token)
                    if sucesso:
                        st.success("✅ Enviado com sucesso!")
                    else:
                        st.error("❌ Falha no envio.")
    except Exception as e:
        st.error(f"Erro ao processar: {e}")