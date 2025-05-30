
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

# === OBTER SITE_ID ===
resp_site = requests.get(
    "https://graph.microsoft.com/v1.0/sites/dsviewdata0.sharepoint.com:/sites/root",
    headers=headers
)
st.write("📎 SITE ID:")
st.json(resp_site.json())

# === OBTER DRIVE_ID ===
site_id = resp_site.json().get("id")
if site_id:
    resp_drive = requests.get(
        f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives",
        headers=headers
    )
    st.write("📁 DRIVES DISPONÍVEIS:")
    st.json(resp_drive.json())
else:
    st.error("❌ Não foi possível obter o site ID.")
