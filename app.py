
import requests
from msal import ConfidentialClientApplication

# === CREDENCIAIS ===
CLIENT_ID = "f9c5914b-2940-4edf-8364-1178052836ce"
CLIENT_SECRET = "4gx8Q~F4-zmN-NNgPlGWLNW.M4LvEr.WL4xCaaRj"
TENANT_ID = "6e1d8e0e-e910-48dc-80d2-112fc3cf3a7d"

# === OBTER TOKEN ===
def obter_token():
    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" in result:
        print("✅ Token obtido!")
        return result["access_token"]
    else:
        print("❌ Erro ao obter token:", result)
        return None

# === TESTAR API COM TIMEOUT ===
def testar_conexao(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://graph.microsoft.com/v1.0/drives"
        response = requests.get(url, headers=headers, timeout=10)
        print("📡 Status da resposta:", response.status_code)
        print("📄 Conteúdo:", response.text[:500])
    except requests.exceptions.Timeout:
        print("⏰ Erro: Timeout - a API demorou mais de 10 segundos para responder.")
    except Exception as e:
        print("❌ Erro inesperado:", e)

if __name__ == "__main__":
    token = obter_token()
    if token:
        testar_conexao(token)
