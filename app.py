
import requests
from msal import ConfidentialClientApplication

# === CREDENCIAIS DO AZURE ===
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

# === BUSCAR O DRIVE PRINCIPAL E SALVAR EM ARQUIVO ===
def salvar_drive_id(token):
    url = "https://graph.microsoft.com/v1.0/sites/root/drive"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print("📄 Resposta de /sites/root/drive:")
    print("Status:", response.status_code)
    print("Conteúdo:", response.text[:300])

    if response.status_code == 200:
        drive_id = response.json().get("id")
        if drive_id:
            with open("drive_id.txt", "w") as f:
                f.write(drive_id)
            print("✅ drive_id salvo em drive_id.txt")
        else:
            print("❌ Não foi possível extrair o drive_id.")
    else:
        print("❌ Erro na requisição:", response.text)

if __name__ == "__main__":
    token = obter_token()
    if token:
        salvar_drive_id(token)
