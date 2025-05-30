
import requests
import streamlit as st

# === CREDENCIAIS ===
from msal import ConfidentialClientApplication
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
TENANT_ID = st.secrets["TENANT_ID"]
SITE_ID = st.secrets["SITE_ID"]

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

# === OBTER DRIVES DO SITE ===
resp = requests.get(
    f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drives",
    headers=headers
)
st.write("📂 Lista de Drives disponíveis no Site:")
st.json(resp.json())
