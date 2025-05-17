import streamlit as st
import requests
from msal import ConfidentialClientApplication

# Carregar segredos do Streamlit Cloud
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
TENANT_ID = st.secrets["TENANT_ID"]
EMAIL = st.secrets["EMAIL_ONEDRIVE"]

def obter_token():
    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return result.get("access_token")

def listar_conteudo_raiz(token):
    url = f"https://graph.microsoft.com/v1.0/users/{EMAIL}/drive/root/children"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        st.subheader("📁 Conteúdo da raiz do OneDrive")
        for item in response.json().get("value", []):
            tipo = "📂 Pasta" if "folder" in item else "📄 Arquivo"
            st.write(f"{tipo}: {item['name']}")
    else:
        st.error("❌ Erro ao listar conteúdo:")
        st.code(response.text)

# Interface Streamlit
st.set_page_config(page_title="Listar OneDrive", layout="wide")
st.title("🔍 Verificar conteúdo da raiz do OneDrive (via API)")

if st.button("🔄 Listar pastas e arquivos"):
    with st.spinner("Conectando com o OneDrive..."):
        token = obter_token()
        if token:
            listar_conteudo_raiz(token)
        else:
            st.error("Erro ao obter token.")