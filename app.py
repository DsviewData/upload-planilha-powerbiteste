
import requests
from msal import ConfidentialClientApplication
from datetime import datetime
import os

# === CREDENCIAIS DO AZURE ===
CLIENT_ID = "f9c5914b-2940-4edf-8364-1178052836ce"
CLIENT_SECRET = "4gx8Q~F4-zmN-NNgPlGWLNW.M4LvEr.WL4xCaaRj"
TENANT_ID = "6e1d8e0e-e910-48dc-80d2-112fc3cf3a7d"
EMAIL_ONEDRIVE = "daniel@dsviewdata.com"
PASTA_ONEDRIVE = "uploads"

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

# === RENOMEAR ARQUIVO EXISTENTE COM BACKUP ===
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
        patch_response = requests.patch(patch_url, headers=patch_headers, json=patch_body)
        if patch_response.status_code in [200, 204]:
            print(f"🔄 Backup realizado: {novo_nome}")
        else:
            print("⚠️ Falha ao renomear arquivo existente:", patch_response.text)
    else:
        print("ℹ️ Nenhum arquivo anterior com o mesmo nome encontrado.")

# === FAZER UPLOAD PARA ONEDRIVE ===
def upload_arquivo(nome_arquivo_local, token):
    nome_arquivo = os.path.basename(nome_arquivo_local)
    with open(nome_arquivo_local, "rb") as f:
        conteudo = f.read()

    mover_arquivo_existente(nome_arquivo, token)

    url = f"https://graph.microsoft.com/v1.0/users/{EMAIL_ONEDRIVE}/drive/root:/{PASTA_ONEDRIVE}/{nome_arquivo}:/content"
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
        # Substitua pelo caminho do arquivo local a ser enviado
        caminho_arquivo = "Faturamento_geral_consolidado_limpar.xlsx"
        if os.path.exists(caminho_arquivo):
            upload_arquivo(caminho_arquivo, token)
        else:
            print("❌ Arquivo local não encontrado:", caminho_arquivo)
