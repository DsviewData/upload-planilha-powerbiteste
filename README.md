# DSViewData - Upload para OneDrive com Backup (via Streamlit Cloud)

Este app permite que seus clientes enviem planilhas diretamente para uma pasta do OneDrive. Ele faz backup automático se o arquivo já existir.

## ✅ Requisitos

- Conta do OneDrive for Business (com permissão API configurada no Azure)
- Chaves de acesso definidas no menu "Secrets" do Streamlit Cloud

## 🔐 Como configurar no Streamlit Cloud

1. Vá até [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. Conecte o repositório com este projeto
3. Acesse **Settings > Secrets** e adicione:

```
CLIENT_ID = "..."
CLIENT_SECRET = "..."
TENANT_ID = "..."
EMAIL_ONEDRIVE = "daniel@dsviewdata.com"
```

## ▶️ Rodar localmente (opcional)

Você pode também rodar localmente com um `.env` e `python-dotenv` se preferir.