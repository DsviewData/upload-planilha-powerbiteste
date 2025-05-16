
import requests
from msal import ConfidentialClientApplication
from datetime import datetime

# === CONFIGURAÇÕES SEGURAS ===
CLIENT_ID = "f9c5914b-2940-4edf-8364-1178052836ce"
CLIENT_SECRET = "4gx8Q~F4-zmN-NNgPlGWLNW.M4LvEr.WL4xCaaRj"
TENANT_ID = "6e1d8e0e-e910-48dc-80d2-112fc3cf3a7d"
PASTA_ONEDRIVE = "Uploads"  # Pasta de teste no OneDrive

# === OBTER TOKEN ===
def obter_token():
    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" in result:
        return result["access_token"]
    else:
        print("Erro ao obter token:")
        print(result)
        return None

# === OBTER LISTA DE DRIVES ===
def obter_drive_id(token):
    url = "https://graph.microsoft.com/v1.0/drives"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    print("Lista de Drives:")
    for drive in data.get("value", []):
        print(f"- {drive['name']} | ID: {drive['id']}")
    return data.get("value", [{}])[0].get("id")  # Retorna o primeiro drive

# === FAZER UPLOAD DE TESTE ===
def upload_arquivo(drive_id, token):
    nome_arquivo = f"upload_teste_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    conteudo = b"Este é um teste de envio para o OneDrive com drive_id."
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{PASTA_ONEDRIVE}/{nome_arquivo}:/content"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream"
    }
    response = requests.put(url, headers=headers, data=conteudo)
    print(f"Status Upload: {response.status_code}")
    print("Resposta:", response.text)

if __name__ == "__main__":
    token = obter_token()
    if token:
        drive_id = obter_drive_id(token)
        if drive_id:
            upload_arquivo(drive_id, token)
        else:
            print("Não foi possível obter o drive_id.")
