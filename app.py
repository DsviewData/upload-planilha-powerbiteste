
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

# === BUSCAR O DRIVE E SALVAR SAÍDA ===
def salvar_drive_id(token):
    url = "https://graph.microsoft.com/v1.0/sites/root/drive"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print("📡 Status da resposta:", response.status_code)
        print("📄 Resposta (até 300 chars):", response.text[:300])

        with open("resposta_raw.txt", "w", encoding="utf-8") as f:
            f.write(response.text)

        if response.status_code == 200:
            data = response.json()
            drive_id = data.get("id")
            if drive_id:
                with open("drive_id.txt", "w") as f:
                    f.write(drive_id)
                print("✅ drive_id salvo em drive_id.txt")
            else:
                print("⚠️ Nenhum drive_id encontrado na resposta.")
        else:
            print("❌ Erro ao consultar o Graph:", response.text)
    except requests.exceptions.Timeout:
        print("⏰ Timeout: A API não respondeu em 10 segundos.")
    except Exception as e:
        print("❌ Erro inesperado:", e)

if __name__ == "__main__":
    token = obter_token()
    if token:
        salvar_drive_id(token)
