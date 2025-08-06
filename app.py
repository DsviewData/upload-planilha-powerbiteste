import streamlit as st
import pandas as pd
import requests
import logging
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
from msal import ConfidentialClientApplication
import unicodedata
import io
from pathlib import Path

# === CONFIGURAÇÃO DE LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURAÇÃO DA PÁGINA ===
st.set_page_config(
    page_title="DSView BI - Upload e Gestão de Planilhas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CONSTANTES ===
class Config:
    PASTA = "Documentos Compartilhados/LimparAuto/FontedeDados"
    MAX_FILE_SIZE_MB = 50
    SUPPORTED_FORMATS = ["xlsx", "xls", "csv"]
    GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
    
    # Schema das colunas esperadas por arquivo (baseado na planilha real)
    EXPECTED_SCHEMAS = {
        "faturamento_geral_consolidado_limpar.xlsx": [
            "GRUPO", "CONCESSIONÁRIA", "LOJA", "MARCA", "UF", "MUNICIPIO", "RESPONSÁVEL", "CNPJ",
            "VLR_DUTOS", "QTD_DUTOS", "TOTAL_DUTOS", "VLR_FREIO", "QTD_FREIO", "TOTAL_FREIO",
            "VLR_SANITIZANTE", "QTD_SANITIZANTE", "TOTAL_SANITIZANTE", "VLR_VERNIZ", "QTD_VERNIZ", "TOTAL_VERNIZ",
            "VLR_CX EVAP", "QTD_CX EVAP", "TOTAL_CX EVAP", "VLR_PROTEC", "QTD_PROTEC", "TOTAL_PROTEC",
            "VLR_NITROGÊNIO", "QTD_NITROGÊNIO", "TOTAL_CX EVAP.1", "QTD_TOTAL", "VLR_TOTAL",
            "DATA_MES", "EMPRESA", "DATA FATURA", "ATRASO", "VENCIMENTO", "FAT OU NF", "NF",
            "RESP/ LEVA", "RECEBIDO", "VLR_RECEBIDO", "A RECEBER", "ENVIAR PARA", "OBS",
            "IMPOSTO", "IMP TOTAL", "BONIF UNIT", "EXTRA", "BONIF TOTAL", "INDIC UNIT", "INDIC",
            "PROV UNIT", "PROVISÃO", "BACKOFFICE (R$2)", "REEMBOLSO", "DIVERSOS", "MÁQUINAS", "GASTOS",
            "GABRIEL", "MAN", "HYUNDAI", "JEEP", "VW", "PSA", "GWM", "LUCRO LIQ", "%", "VALOR",
            "DESCONTOS", "A RECEBER.1", "QTD_MAQ DUTO", "QTD_MAQ FREIO", "QTD_MAQ SANITIZANTE",
            "QTD_MAQ VERNIZ", "QTD_CX EVAP.1", "TOTAL_MAQ", "CT", "SUP", "APLC", "FACILIT",
            "CH OFIC", "AGEND", "CONTR", "OUTROS", "GPV", "DIR", "DIR GERAL", "POR TMO", "INDICAÇÃO", "PROVIS."
        ]
    }
    
    @classmethod
    def get_credentials(cls) -> Dict[str, str]:
        """Obtém credenciais dos secrets do Streamlit com validação"""
        required_secrets = ["CLIENT_ID", "CLIENT_SECRET", "TENANT_ID", "EMAIL_ONEDRIVE", "SITE_ID", "DRIVE_ID"]
        credentials = {}
        
        for secret in required_secrets:
            if secret not in st.secrets:
                st.error(f"❌ Credencial '{secret}' não encontrada nos secrets!")
                st.stop()
            credentials[secret] = st.secrets[secret]
        
        return credentials
    
    @classmethod
    def get_expected_schema(cls, filename: str) -> Optional[List[str]]:
        """Obtém o schema esperado para um arquivo específico"""
        filename_lower = filename.lower()
        
        # Busca exata primeiro
        if filename_lower in cls.EXPECTED_SCHEMAS:
            return cls.EXPECTED_SCHEMAS[filename_lower]
        
        # Busca por palavras-chave no nome do arquivo
        for schema_file, columns in cls.EXPECTED_SCHEMAS.items():
            schema_name = schema_file.split('.')[0]  # Remove extensão
            if schema_name in filename_lower:
                return columns
        
        return None

# === CLASSE PARA GERENCIAR ONEDRIVE ===
class OneDriveManager:
    def __init__(self):
        self.credentials = Config.get_credentials()
        self._token_cache = None
        self._token_expiry = None
    
    def get_token(self) -> Optional[str]:
        """Obtém token de acesso com cache"""
        try:
            # Verifica se o token ainda está válido
            if (self._token_cache and self._token_expiry and 
                datetime.now() < self._token_expiry):
                return self._token_cache
            
            app = ConfidentialClientApplication(
                self.credentials["CLIENT_ID"],
                authority=f"https://login.microsoftonline.com/{self.credentials['TENANT_ID']}",
                client_credential=self.credentials["CLIENT_SECRET"]
            )
            
            result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
            
            if "access_token" in result:
                self._token_cache = result["access_token"]
                # Define expiração para 50 minutos (tokens geralmente duram 60min)
                from datetime import timedelta
                self._token_expiry = datetime.now() + timedelta(minutes=50)
                return self._token_cache
            else:
                logger.error(f"Erro na autenticação: {result.get('error_description', 'Erro desconhecido')}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao obter token: {str(e)}")
            st.error(f"❌ Erro na autenticação: {str(e)}")
            return None
    
    def backup_existing_file(self, nome_arquivo: str, token: str) -> bool:
        """Move arquivo existente para backup"""
        try:
            url = f"{Config.GRAPH_API_BASE}/sites/{self.credentials['SITE_ID']}/drives/{self.credentials['DRIVE_ID']}/root:/{Config.PASTA}/{nome_arquivo}"
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                file_id = response.json().get("id")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_stem = Path(nome_arquivo).stem
                file_suffix = Path(nome_arquivo).suffix
                novo_nome = f"{file_stem}_backup_{timestamp}{file_suffix}"
                
                patch_url = f"{Config.GRAPH_API_BASE}/sites/{self.credentials['SITE_ID']}/drives/{self.credentials['DRIVE_ID']}/items/{file_id}"
                patch_body = {"name": novo_nome}
                patch_headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                patch_response = requests.patch(patch_url, headers=patch_headers, json=patch_body, timeout=30)
                return patch_response.status_code == 200
            
            return True  # Se arquivo não existe, não há problema
            
        except requests.exceptions.Timeout:
            st.warning("⏱️ Timeout ao fazer backup - prosseguindo com upload")
            return True
        except Exception as e:
            logger.error(f"Erro no backup: {str(e)}")
            return False
    
    def upload_file(self, nome_arquivo: str, conteudo: bytes, token: str, fazer_backup: bool = True) -> Tuple[bool, int, str]:
        """Faz upload do arquivo para o OneDrive"""
        try:
            # Fazer backup se solicitado
            if fazer_backup:
                backup_success = self.backup_existing_file(nome_arquivo, token)
                if not backup_success:
                    st.warning("⚠️ Não foi possível fazer backup do arquivo existente")
            
            url = f"{Config.GRAPH_API_BASE}/sites/{self.credentials['SITE_ID']}/drives/{self.credentials['DRIVE_ID']}/root:/{Config.PASTA}/{nome_arquivo}:/content"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/octet-stream"
            }
            
            response = requests.put(url, headers=headers, data=conteudo, timeout=60)
            return response.status_code in [200, 201], response.status_code, response.text
            
        except requests.exceptions.Timeout:
            return False, 408, "Timeout durante o upload"
        except Exception as e:
            logger.error(f"Erro no upload: {str(e)}")
            return False, 500, str(e)
    
    def list_files(self, token: str) -> List[Dict[str, Any]]:
        """Lista arquivos na pasta do OneDrive"""
        try:
            url = f"{Config.GRAPH_API_BASE}/users/{self.credentials['EMAIL_ONEDRIVE']}/drive/root:/{Config.PASTA}:/children"
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                files = response.json().get("value", [])
                # Filtrar apenas arquivos de planilha
                return [f for f in files if any(f['name'].lower().endswith(f'.{ext}') for ext in Config.SUPPORTED_FORMATS)]
            else:
                st.error(f"❌ Erro ao listar arquivos: {response.status_code}")
                return []
                
        except requests.exceptions.Timeout:
            st.error("⏱️ Timeout ao listar arquivos")
            return []
        except Exception as e:
            logger.error(f"Erro ao listar arquivos: {str(e)}")
            st.error(f"❌ Erro ao listar arquivos: {str(e)}")
            return []
    
    def delete_file(self, token: str, file_id: str) -> bool:
        """Deleta um arquivo do OneDrive"""
        try:
            url = f"{Config.GRAPH_API_BASE}/users/{self.credentials['EMAIL_ONEDRIVE']}/drive/items/{file_id}"
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.delete(url, headers=headers, timeout=30)
            return response.status_code == 204
            
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo: {str(e)}")
            return False

# === FUNÇÕES DE VALIDAÇÃO ===
class DataValidator:
    @staticmethod
    def validate_column_names(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Valida nomes de colunas"""
        invalid_columns = []
        
        for col in df.columns:
            # Normaliza para ASCII
            col_ascii = unicodedata.normalize("NFKD", str(col)).encode("ASCII", "ignore").decode()
            
            # Verifica se contém apenas caracteres válidos
            if not col_ascii.replace("_", "").replace(" ", "").isalnum():
                invalid_columns.append(col)
        
        return len(invalid_columns) == 0, invalid_columns
    
    @staticmethod
    def analyze_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
        """Analisa qualidade dos dados"""
        analysis = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "null_columns": df.columns[df.isnull().any()].tolist(),
            "duplicate_rows": df.duplicated().sum(),
            "memory_usage": df.memory_usage(deep=True).sum() / 1024 / 1024,  # MB
            "column_types": df.dtypes.to_dict()
        }
        
        return analysis
    
    @staticmethod
    def validate_schema(df: pd.DataFrame, filename: str) -> Dict[str, Any]:
        """Valida se o schema das colunas está compatível com o Power BI"""
        expected_columns = Config.get_expected_schema(filename)
        
        if expected_columns is None:
            return {
                "is_valid": True,
                "has_schema": False,
                "message": "Schema não definido para este arquivo - upload permitido"
            }
        
        current_columns = list(df.columns)
        
        # Verifica se todas as colunas esperadas estão presentes
        missing_columns = [col for col in expected_columns if col not in current_columns]
        extra_columns = [col for col in current_columns if col not in expected_columns]
        
        is_valid = len(missing_columns) == 0 and len(extra_columns) == 0
        
        return {
            "is_valid": is_valid,
            "has_schema": True,
            "expected_columns": expected_columns,
            "current_columns": current_columns,
            "missing_columns": missing_columns,
            "extra_columns": extra_columns,
            "message": "Schema validado" if is_valid else "Schema incompatível"
        }
    
    @staticmethod
    def get_duplicate_analysis(df: pd.DataFrame) -> Dict[str, Any]:
        if df.duplicated().sum() == 0:
            return {"has_duplicates": False}
        
        # Identifica todas as linhas duplicadas (incluindo a primeira ocorrência)
        duplicated_mask = df.duplicated(keep=False)
        duplicated_df = df[duplicated_mask].copy()
        
        # Adiciona índice original para referência
        duplicated_df['🔢 Linha Original'] = df[duplicated_mask].index + 1
        
        # Agrupa por valores duplicados
        duplicate_groups = []
        for group_idx, (_, group) in enumerate(df[duplicated_mask].groupby(df.columns.tolist())):
            duplicate_groups.append({
                "group_id": group_idx + 1,
                "count": len(group),
                "original_indices": (group.index + 1).tolist(),
                "data": group.iloc[0].to_dict()  # Primeira ocorrência do grupo
            })
        
        return {
            "has_duplicates": True,
            "total_duplicated_rows": duplicated_mask.sum(),
            "unique_duplicate_patterns": len(duplicate_groups),
            "duplicate_groups": duplicate_groups,
            "duplicated_df": duplicated_df
        }

# === FUNÇÕES DA INTERFACE ===
def show_header():
    """Exibe cabeçalho da aplicação"""
    st.markdown(
        """
        <div style="
            background: linear-gradient(90deg, #2E8B57, #3CB371);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
        ">
            <h1 style="margin: 0; font-size: 2rem;">📊 DSView BI</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Sistema de Upload e Gestão de Planilhas</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_schema_validation(df: pd.DataFrame, filename: str) -> bool:
    """Exibe validação de schema e retorna se é válido para upload"""
    schema_result = DataValidator.validate_schema(df, filename)
    
    if not schema_result["has_schema"]:
        st.info("ℹ️ **Schema não definido** - Este arquivo não possui validação de schema configurada")
        return True
    
    if schema_result["is_valid"]:
        st.success("✅ **Schema validado** - Estrutura das colunas está correta para o Power BI")
        return True
    
    # Schema inválido - mostrar detalhes
    st.error("🚫 **ERRO: Schema incompatível com Power BI**")
    
    # Container com detalhes do erro
    with st.container():
        st.markdown("### 🔍 Detalhes da Incompatibilidade")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📋 Colunas Esperadas (Power BI):**")
            for col in schema_result["expected_columns"]:
                st.markdown(f"• `{col}`")
        
        with col2:
            st.markdown("**📊 Colunas Encontradas (Seu Arquivo):**")
            for col in schema_result["current_columns"]:
                # Marca em vermelho se não está na lista esperada
                if col in schema_result["extra_columns"]:
                    st.markdown(f"• `{col}` ❌")
                else:
                    st.markdown(f"• `{col}` ✅")
        
        # Problemas específicos
        if schema_result["missing_columns"]:
            st.error(f"**🚫 Colunas ausentes:** {', '.join(schema_result['missing_columns'])}")
        
        if schema_result["extra_columns"]:
            st.error(f"**➕ Colunas extras:** {', '.join(schema_result['extra_columns'])}")
    
    # Aviso importante
    st.markdown(
        """
        <div style="
            background-color: #ffebcd;
            border-left: 5px solid #ff6b6b;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        ">
            <h4 style="color: #d63031; margin: 0 0 10px 0;">⚠️ UPLOAD BLOQUEADO</h4>
            <p style="margin: 0; color: #2d3436;">
                <strong>A estrutura das colunas não está compatível com o Power BI.</strong><br>
                Entre em contato com a <strong>DSViewData</strong> para informar que houve mudança no nome das colunas.<br><br>
                📧 <strong>Ação necessária:</strong> Solicite a atualização do schema ou corrija os nomes das colunas na planilha.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    return False
def show_duplicate_analysis(df: pd.DataFrame):
    """Exibe análise detalhada das duplicatas"""
    duplicate_analysis = DataValidator.get_duplicate_analysis(df)
    
    if not duplicate_analysis["has_duplicates"]:
        return None
    
    st.markdown("### 🔍 Análise Detalhada das Duplicatas")
    
    # Métricas das duplicatas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Total de Linhas Duplicadas", duplicate_analysis["total_duplicated_rows"])
    with col2:
        st.metric("🎯 Padrões Únicos", duplicate_analysis["unique_duplicate_patterns"])
    with col3:
        st.metric("📝 Linhas a Remover", duplicate_analysis["total_duplicated_rows"] - duplicate_analysis["unique_duplicate_patterns"])
    
    # Tabs para diferentes visualizações
    tab1, tab2, tab3 = st.tabs(["📋 Grupos de Duplicatas", "📊 Todas as Duplicatas", "🔧 Ações"])
    
    with tab1:
        st.markdown("**Grupos de linhas idênticas:**")
        
        for group in duplicate_analysis["duplicate_groups"]:
            with st.expander(f"🔸 Grupo {group['group_id']} - {group['count']} ocorrências (linhas: {', '.join(map(str, group['original_indices']))})", expanded=False):
                # Cria um DataFrame com uma linha para mostrar os dados
                group_df = pd.DataFrame([group["data"]])
                st.dataframe(group_df, use_container_width=True, hide_index=True)
                
                st.info(f"💡 Este padrão aparece {group['count']} vezes nas linhas: {', '.join(map(str, group['original_indices']))}")
    
    with tab2:
        st.markdown("**Todas as linhas duplicadas (com índice original):**")
        
        # Reorganiza as colunas para mostrar o índice primeiro
        display_df = duplicate_analysis["duplicated_df"]
        cols = ['🔢 Linha Original'] + [col for col in display_df.columns if col != '🔢 Linha Original']
        display_df = display_df[cols]
        
        st.dataframe(
            display_df, 
            use_container_width=True, 
            hide_index=True,
            height=400
        )
        
        # Botão para download das duplicatas
        csv_duplicates = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Baixar Duplicatas (CSV)",
            data=csv_duplicates,
            file_name="duplicatas_encontradas.csv",
            mime="text/csv"
        )
    
    with tab3:
        st.markdown("**Escolha como proceder:**")
        
        action = st.radio(
            "Ação a tomar:",
            [
                "🧹 Remover todas as duplicatas (manter apenas primeira ocorrência)",
                "✏️ Remover duplicatas específicas (selecionar manualmente)",
                "📤 Manter todas as linhas (upload sem alteração)"
            ]
        )
        
        if action.startswith("✏️"):
            st.info("🚧 **Funcionalidade em desenvolvimento** - Por ora, use 'Remover todas as duplicatas'")
            return "keep_all"
        elif action.startswith("🧹"):
            return "remove_all"
        else:
            return "keep_all"
    
    # Retorna por padrão "keep_all" se nenhuma ação foi selecionada
    return "keep_all"

def show_upload_tab(onedrive_manager: OneDriveManager):
    """Interface para upload de planilhas"""
    st.markdown("## 📤 Upload de Planilha")
    
    # Informações sobre limites
    st.info(f"📋 **Formatos aceitos:** {', '.join(Config.SUPPORTED_FORMATS)} | **Tamanho máximo:** {Config.MAX_FILE_SIZE_MB}MB")
    
    uploaded_file = st.file_uploader(
        "Escolha um arquivo de planilha",
        type=Config.SUPPORTED_FORMATS,
        help=f"Selecione um arquivo de até {Config.MAX_FILE_SIZE_MB}MB"
    )
    
    if uploaded_file is None:
        return
    
    # Validação de tamanho
    file_size_mb = len(uploaded_file.getbuffer()) / 1024 / 1024
    if file_size_mb > Config.MAX_FILE_SIZE_MB:
        st.error(f"❌ Arquivo muito grande: {file_size_mb:.1f}MB. Limite: {Config.MAX_FILE_SIZE_MB}MB")
        return
    
    try:
        # Lê o arquivo baseado na extensão
        if uploaded_file.name.lower().endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            sheet_name = None
        else:
            xls = pd.ExcelFile(uploaded_file)
            sheets = xls.sheet_names
            
            if len(sheets) > 1:
                sheet_name = st.selectbox("📋 Selecione a aba:", sheets, key="sheet_selector")
            else:
                sheet_name = sheets[0]
                st.info(f"📋 Aba selecionada: **{sheet_name}**")
            
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
    
    except Exception as e:
        st.error(f"❌ Erro ao ler arquivo: {str(e)}")
        return
    
    # Exibe preview dos dados
    st.subheader("👀 Preview dos Dados")
    st.dataframe(df.head(10), use_container_width=True, height=300)
    
    # Análise de qualidade dos dados
    st.subheader("📊 Análise de Qualidade")
    analysis = DataValidator.analyze_data_quality(df)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📏 Linhas", analysis["total_rows"])
    with col2:
        st.metric("📊 Colunas", analysis["total_columns"])
    with col3:
        st.metric("🔄 Duplicatas", analysis["duplicate_rows"])
    with col4:
        st.metric("💾 Tamanho (MB)", f"{analysis['memory_usage']:.2f}")
    
    # Validação de colunas
    valid_columns, invalid_columns = DataValidator.validate_column_names(df)
    
    if invalid_columns:
        st.error(f"🚫 **Colunas com nomes inválidos:** {', '.join(invalid_columns)}")
        st.info("💡 **Dica:** Renomeie as colunas para conter apenas letras, números e sublinhados")
    
    if analysis["null_columns"]:
        st.warning(f"⚠️ **Colunas com valores nulos:** {', '.join(analysis['null_columns'])}")
    
    # VALIDAÇÃO DE SCHEMA - NOVO!
    st.subheader("🔍 Validação de Schema (Power BI)")
    schema_valid = show_schema_validation(df, uploaded_file.name)
    
    # Se schema inválido, bloquear upload
    if not schema_valid:
        st.stop()  # Para a execução aqui
    
    # Análise de duplicatas aprimorada
    duplicate_action = "keep_all"  # Valor padrão
    
    if analysis["duplicate_rows"] > 0:
        st.warning(f"⚠️ **{analysis['duplicate_rows']} linhas duplicadas encontradas**")
        duplicate_action = show_duplicate_analysis(df)
    
    # Opções de upload
    st.subheader("⚙️ Opções de Upload")
    
    st.info("📦 **Backup automático:** O sistema fará backup automaticamente de qualquer arquivo existente com o mesmo nome")
    
    confirmar_upload = st.checkbox("✅ Confirmo que os dados estão corretos e autorizo o upload")
    
    # Botão de upload
    if not confirmar_upload:
        st.info("⚠️ Marque a confirmação para habilitar o upload")
        return
    
    if st.button("📤 Realizar Upload", type="primary", use_container_width=True):
        token = onedrive_manager.get_token()
        if not token:
            st.error("❌ Erro na autenticação")
            return
        
        with st.spinner("📤 Enviando arquivo..."):
            progress_bar = st.progress(0)
            
            # Processa o arquivo baseado na ação escolhida para duplicatas
            df_final = df.copy()
            
            if duplicate_action == "remove_all" and analysis["duplicate_rows"] > 0:
                df_final = df.drop_duplicates()
                st.info(f"🧹 Duplicatas removidas: {len(df) - len(df_final)} linhas eliminadas")
            
            # Salva o arquivo processado
            buffer = io.BytesIO()
            if uploaded_file.name.lower().endswith('.csv'):
                df_final.to_csv(buffer, index=False)
            else:
                df_final.to_excel(buffer, index=False, sheet_name=sheet_name or 'Sheet1')
            file_content = buffer.getvalue()
            
            progress_bar.progress(50)
            
            sucesso, status, resposta = onedrive_manager.upload_file(
                uploaded_file.name, 
                file_content, 
                token, 
                True  # Sempre fazer backup
            )
            
            progress_bar.progress(100)
            
            if sucesso:
                st.success("🎉 **Arquivo enviado com sucesso!**")
                
                # Mostra estatísticas do upload
                if duplicate_action == "remove_all" and analysis["duplicate_rows"] > 0:
                    st.info(f"📊 **Estatísticas do upload:**\n"
                            f"- Linhas originais: {len(df)}\n"
                            f"- Linhas enviadas: {len(df_final)}\n"
                            f"- Duplicatas removidas: {len(df) - len(df_final)}")
                
                st.balloons()
                
                # Log da operação
                logger.info(f"Upload bem-sucedido: {uploaded_file.name} ({file_size_mb:.2f}MB)")
                
            else:
                st.error(f"❌ **Erro no upload** (Código: {status})")
                st.code(resposta, language="text")

def show_management_tab(onedrive_manager: OneDriveManager):
    """Interface para gerenciar arquivos"""
    st.markdown("## 📂 Gerenciar Arquivos")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Atualizar Lista", type="secondary"):
            st.rerun()
    
    token = onedrive_manager.get_token()
    if not token:
        st.error("❌ Erro na autenticação")
        return
    
    with st.spinner("📂 Carregando arquivos..."):
        arquivos = onedrive_manager.list_files(token)
    
    if not arquivos:
        st.info("📭 Nenhum arquivo de planilha encontrado na pasta.")
        return
    
    st.info(f"📊 **{len(arquivos)} arquivo(s) encontrado(s)**")
    
    # Tabela com informações dos arquivos
    arquivos_info = []
    for arq in arquivos:
        arquivos_info.append({
            "📄 Nome": arq['name'],
            "📊 Tamanho": f"{arq['size'] / 1024:.1f} KB",
            "📅 Modificado": datetime.fromisoformat(arq['lastModifiedDateTime'].replace('Z', '+00:00')).strftime("%d/%m/%Y %H:%M"),
            "🔗 Link": arq.get('@microsoft.graph.downloadUrl', ''),
            "🆔 ID": arq['id']
        })
    
    df_arquivos = pd.DataFrame(arquivos_info)
    
    # Exibe a tabela
    st.dataframe(
        df_arquivos[["📄 Nome", "📊 Tamanho", "📅 Modificado"]], 
        use_container_width=True,
        hide_index=True
    )
    
    # Seção para ações nos arquivos
    st.subheader("🛠️ Ações")
    
    arquivo_selecionado = st.selectbox(
        "Selecione um arquivo:",
        options=range(len(arquivos)),
        format_func=lambda x: arquivos[x]['name']
    )
    
    if arquivo_selecionado is not None:
        arq = arquivos[arquivo_selecionado]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔗 Abrir Arquivo", use_container_width=True):
                download_url = arq.get('@microsoft.graph.downloadUrl')
                if download_url:
                    st.markdown(f"[📎 Clique aqui para baixar]({download_url})")
                else:
                    st.error("❌ Link não disponível")
        
        with col2:
            if st.button("📋 Copiar Link", use_container_width=True):
                download_url = arq.get('@microsoft.graph.downloadUrl')
                if download_url:
                    st.code(download_url)
                    st.success("✅ Link exibido acima")
        
        with col3:
            if st.button("🗑️ Deletar", use_container_width=True, type="secondary"):
                if st.checkbox(f"⚠️ Confirmar exclusão de '{arq['name']}'"):
                    with st.spinner("🗑️ Deletando..."):
                        sucesso = onedrive_manager.delete_file(token, arq['id'])
                        if sucesso:
                            st.success("✅ Arquivo deletado!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao deletar arquivo")

# === FUNÇÃO PRINCIPAL ===
def main():
    """Função principal da aplicação"""
    show_header()
    
    # Inicializa o gerenciador OneDrive
    onedrive_manager = OneDriveManager()
    
    # Sidebar para navegação
    with st.sidebar:
        st.markdown("### 🧭 Navegação")
        aba = st.radio(
            "Escolha uma opção:",
            ["📤 Upload de Planilha", "📂 Gerenciar Arquivos"],
            key="navigation_radio"
        )
        
        st.markdown("---")
        st.markdown("### ℹ️ Informações")
        st.markdown(f"📁 **Pasta:** {Config.PASTA}")
        st.markdown(f"📊 **Formatos:** {', '.join(Config.SUPPORTED_FORMATS)}")
        st.markdown(f"📏 **Limite:** {Config.MAX_FILE_SIZE_MB}MB")
        
        # Mostra schemas disponíveis
        st.markdown("---")
        st.markdown("### 📋 Schemas Configurados")
        if Config.EXPECTED_SCHEMAS:
            for filename, columns in Config.EXPECTED_SCHEMAS.items():
                with st.expander(f"📄 {filename}", expanded=False):
                    for col in columns:
                        st.markdown(f"• `{col}`")
        else:
            st.info("Nenhum schema configurado")
    
    # Exibe a aba selecionada
    if aba == "📤 Upload de Planilha":
        show_upload_tab(onedrive_manager)
    elif aba == "📂 Gerenciar Arquivos":
        show_management_tab(onedrive_manager)

if __name__ == "__main__":
    main()