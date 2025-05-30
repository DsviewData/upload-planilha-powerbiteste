
import requests
import streamlit as st

# Obter token da aplicação
from msal import ConfidentialClientApplication
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
TENANT_ID = st.secrets["TENANT_ID"]

def obter_token():
    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    token_response = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return token_response.get("access_token")

token = obter_token()
headers = {"Authorization": f"Bearer {token}"}

# === LISTAR TODOS OS SITES DISPONÍVEIS ===
resp_sites = requests.get(
    "https://graph.microsoft.com/v1.0/sites?search=*",
    headers=headers
)
st.write("📋 Lista de Sites que você tem acesso:")
st.json(resp_sites.json())
