import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from msal import ConfidentialClientApplication

# === CREDENCIAIS via st.secrets ===
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
TENANT_ID = st.secrets["TENANT_ID"]
EMAIL_ONEDRIVE = st.secrets["EMAIL_ONEDRIVE"]
PASTA = "ProjetosBI/Limpar Auto/fontededados/dados_geral/faturamento"

# === AUTENTICAÇÃO ===
def obter_token():
    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return result.get("access_token")

# === UPLOAD E BACKUP ===
def mover_arquivo_existente(nome_arquivo, token):
    url = f"https://graph.microsoft.com/v1.0/users/{EMAIL_ONEDRIVE}/drive/root:/{PASTA}/{nome_arquivo}"
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
        requests.patch(patch_url, headers=patch_headers, json=patch_body)

def upload_onedrive(nome_arquivo, conteudo_arquivo, token):
    mover_arquivo_existente(nome_arquivo, token)
    url = f"https://graph.microsoft.com/v1.0/users/{EMAIL_ONEDRIVE}/drive/root:/{PASTA}/{nome_arquivo}:/content"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/octet-stream"
    }
    response = requests.put(url, headers=headers, data=conteudo_arquivo)
    return response.status_code in [200, 201], response.status_code, response.text

# === GERENCIAMENTO DE ARQUIVOS ===
def listar_arquivos(token):
    url = f"https://graph.microsoft.com/v1.0/users/{EMAIL_ONEDRIVE}/drive/root:/{PASTA}:/children"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json().get("value", [])
    else:
        st.error(f"Erro ao listar: {r.status_code}")
        st.code(r.text)
        return []

def deletar_arquivo(token, file_id):
    url = f"https://graph.microsoft.com/v1.0/users/{EMAIL_ONEDRIVE}/drive/items/{file_id}"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.delete(url, headers=headers)
    return r.status_code == 204

# === INTERFACE STREAMLIT ===
st.set_page_config(page_title="Upload e Gestão de Planilhas", layout="wide")
aba = st.sidebar.radio("📂 Navegar", ["📤 Upload de planilha", "📁 Gerenciar arquivos"])

token = obter_token()

if aba == "📤 Upload de planilha":
    st.title("📤 Upload de Planilha Excel para OneDrive")

    uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])
    if uploaded_file:
        try:
            xls = pd.ExcelFile(uploaded_file)
            sheets = xls.sheet_names
            sheet = st.selectbox("Selecione a aba:", sheets) if len(sheets) > 1 else sheets[0]
            df = pd.read_excel(uploaded_file, sheet_name=sheet)
            st.dataframe(df.head(5), use_container_width=True, height=200)

# === RESUMO AUTOMÁTICO DA PLANILHA ===
st.subheader("📊 Resumo dos dados")

# Tamanho
st.write(f"📏 Linhas: {df.shape[0]} | Colunas: {df.shape[1]}")

# Nulos
colunas_nulas = df.columns[df.isnull().any()].tolist()
if colunas_nulas:
    st.warning(f"⚠️ Colunas com valores nulos: {', '.join(colunas_nulas)}")
else:
    st.success("✅ Nenhuma coluna com valores nulos.")

# Nomes inválidos
import unicodedata
def nome_invalido(col):
    col_ascii = unicodedata.normalize("NFKD", col).encode("ASCII", "ignore").decode()
    return not col_ascii.replace("_", "").isalnum()

colunas_invalidas = [col for col in df.columns if nome_invalido(col)]
if colunas_invalidas:
    st.error(f"🚫 Nomes de colunas inválidos: {', '.join(colunas_invalidas)}")
else:
    st.success("✅ Todos os nomes de colunas são válidos.")

            if st.button("📧 Enviar"):
                with st.spinner("Enviando..."):
                    sucesso, status, resposta = upload_onedrive(uploaded_file.name, uploaded_file.getbuffer(), token)
                    if sucesso:
                        st.success("✅ Arquivo enviado com sucesso!")
                    else:
                        st.error(f"❌ Erro {status}")
                        st.code(resposta)
        except Exception as e:
            st.error(f"Erro ao processar: {e}")

elif aba == "📁 Gerenciar arquivos":
    st.title("📂 Painel de Arquivos - Pasta uploads")

    if token:
        arquivos = listar_arquivos(token)
        if arquivos:
            for arq in arquivos:
                with st.expander(f"📄 {arq['name']}"):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"[🔗 Acessar arquivo]({arq['@microsoft.graph.downloadUrl']})")
                        st.write(f"Tamanho: {round(arq['size']/1024, 2)} KB")
                    with col2:
                        if st.button("🗑️ Excluir", key=arq["id"]):
                            sucesso = deletar_arquivo(token, arq["id"])
                            if sucesso:
                                st.success(f"{arq['name']} removido com sucesso.")
                                st.experimental_rerun()
                            else:
                                st.error("Erro ao excluir o arquivo.")
        else:
            st.info("Nenhum arquivo encontrado na pasta uploads.")
    else:
        st.error("Erro ao autenticar.")