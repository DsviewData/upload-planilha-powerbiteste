
import requests
from msal import ConfidentialClientApplication
from datetime import datetime

# === CREDENCIAIS DO AZURE ===
CLIENT_ID = "f9c5914b-2940-4edf-8364-1178052836ce"
CLIENT_SECRET = "4gx8Q~F4-zmN-NNgPlGWLNW.M4LvEr.WL4xCaaRj"
TENANT_ID = "6e1d8e0e-e910-48dc-80d2-112fc3cf3a7d"
PASTA_ONEDRIVE = "Uploads"

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

# === BUSCAR O DRIVE PRINCIPAL VIA /sites/root/drive ===
def obter_drive_root(token):
    url = "https://graph.microsoft.com/v1.0/sites/root/drive"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print("📄 Resposta de /sites/root/drive:")
    print("Status:", response.status_code)
    print("Conteúdo:", response.text[:500])
    if response.status_code == 200:
        return response.json().get("id")
    return None

# === UPLOAD DO ARQUIVO DE TESTE ===
def upload_arquivo(drive_id, token):
    nome_arquivo = f"upload_sites_root_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    conteudo = "Teste de envio usando /sites/root/drive.".encode("utf-8")
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{PASTA_ONEDRIVE}/{nome_arquivo}:/content"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream"
    }
    response = requests.put(url, headers=headers, data=conteudo)
    print(f"📤 Status do upload: {response.status_code}")
    print("📤 Resposta:", response.text)

if __name__ == "__main__":
    token = obter_token()
    if token:
        drive_id = obter_drive_root(token)
        if drive_id:
            print("✅ drive_id encontrado:", drive_id)
            upload_arquivo(drive_id, token)
        else:
            print("❌ Não foi possível obter o drive_id via /sites/root/drive.")
