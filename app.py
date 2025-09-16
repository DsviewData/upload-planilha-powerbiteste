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

# === CSS CUSTOMIZADO PARA INTERFACE MODERNA ===
def load_custom_css():
    """Carrega CSS customizado para melhorar a interface visual"""
    st.markdown("""
    <style>
    /* Importar fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset e configurações globais */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Fonte global */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header personalizado */
    .custom-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .custom-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    .custom-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .custom-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    /* Cards modernos */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2d3748;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #718096;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Alertas personalizados */
    .custom-alert {
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid;
        position: relative;
        overflow: hidden;
    }
    
    .alert-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left-color: #28a745;
        color: #155724;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left-color: #ffc107;
        color: #856404;
    }
    
    .alert-error {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left-color: #dc3545;
        color: #721c24;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-left-color: #17a2b8;
        color: #0c5460;
    }
    
    /* Botões modernos */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar moderna */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Tabelas modernas */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    /* Progress bar personalizada */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    /* Upload area */
    .uploadedFile {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%);
        transition: all 0.3s ease;
    }
    
    .uploadedFile:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, #f0f2ff 0%, #e8ebff 100%);
    }
    
    /* Seções com separadores visuais */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
        border-radius: 1px;
    }
    
    /* Animações suaves */
    .element-container {
        animation: fadeInUp 0.6s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    .status-success { background-color: #28a745; }
    .status-warning { background-color: #ffc107; }
    .status-error { background-color: #dc3545; }
    .status-info { background-color: #17a2b8; }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Tooltips */
    .tooltip {
        position: relative;
        cursor: help;
    }
    
    .tooltip:hover::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        background: #333;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 0.8rem;
        white-space: nowrap;
        z-index: 1000;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .custom-header h1 {
            font-size: 2rem;
        }
        
        .metric-card {
            margin-bottom: 1rem;
        }
        
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

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
        """
        Valida se o schema das colunas está compatível com o Power BI
        NOVA LÓGICA: Permite novas colunas, mas verifica se as colunas existentes estão corretas
        """
        expected_columns = Config.get_expected_schema(filename)
        
        if expected_columns is None:
            return {
                "is_valid": True,
                "has_schema": False,
                "message": "Schema não definido para este arquivo - upload permitido",
                "allow_consolidation": True
            }
        
        current_columns = list(df.columns)
        
        # NOVA LÓGICA: Verifica se todas as colunas esperadas estão presentes
        # Permite colunas extras (novas colunas)
        missing_columns = [col for col in expected_columns if col not in current_columns]
        extra_columns = [col for col in current_columns if col not in expected_columns]
        
        # Válido se não há colunas faltando (colunas extras são permitidas)
        is_valid = len(missing_columns) == 0
        allow_consolidation = is_valid  # Permite consolidação se não há colunas faltando
        
        if is_valid and extra_columns:
            message = f"Schema compatível com novas colunas detectadas: {', '.join(extra_columns)}"
        elif is_valid:
            message = "Schema totalmente compatível"
        else:
            message = f"Schema incompatível - colunas obrigatórias ausentes: {', '.join(missing_columns)}"
        
        return {
            "is_valid": is_valid,
            "has_schema": True,
            "expected_columns": expected_columns,
            "current_columns": current_columns,
            "missing_columns": missing_columns,
            "extra_columns": extra_columns,
            "allow_consolidation": allow_consolidation,
            "message": message
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
    """Exibe cabeçalho moderno da aplicação"""
    st.markdown(
        """
        <div class="custom-header">
            <h1>📊 DSView BI</h1>
            <p>Sistema Inteligente de Upload e Gestão de Planilhas</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_custom_metric(label: str, value: str, icon: str = "📊"):
    """Exibe métrica personalizada com design moderno"""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{icon} {label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_custom_alert(message: str, alert_type: str = "info", icon: str = "ℹ️"):
    """Exibe alerta personalizado com design moderno"""
    st.markdown(
        f"""
        <div class="custom-alert alert-{alert_type}">
            <span class="status-indicator status-{alert_type}"></span>
            <strong>{icon}</strong> {message}
        </div>
        """,
        unsafe_allow_html=True
    )

def show_schema_validation(df: pd.DataFrame, filename: str) -> bool:
    """Exibe validação de schema melhorada e retorna se é válido para upload"""
    schema_result = DataValidator.validate_schema(df, filename)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🔍 Validação de Schema (Power BI)")
    
    if not schema_result["has_schema"]:
        show_custom_alert(
            "Schema não definido - Este arquivo não possui validação de schema configurada. Upload permitido.",
            "info", "ℹ️"
        )
        return True
    
    if schema_result["is_valid"]:
        if schema_result["extra_columns"]:
            show_custom_alert(
                f"✅ Schema compatível! Novas colunas detectadas: {', '.join(schema_result['extra_columns'][:3])}{'...' if len(schema_result['extra_columns']) > 3 else ''}",
                "success", "🆕"
            )
        else:
            show_custom_alert(
                "✅ Schema totalmente compatível - Estrutura das colunas está perfeita para o Power BI",
                "success", "✅"
            )
        return True
    
    # Schema inválido - mostrar detalhes com design melhorado
    show_custom_alert(
        "🚫 ERRO: Schema incompatível com Power BI - Colunas obrigatórias ausentes",
        "error", "🚫"
    )
    
    # Container com detalhes do erro
    with st.container():
        st.markdown("#### 🔍 Análise Detalhada da Incompatibilidade")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📋 Colunas Esperadas (Power BI):**")
            expected_df = pd.DataFrame({
                "Coluna": schema_result["expected_columns"],
                "Status": ["✅ Presente" if col in schema_result["current_columns"] else "❌ Ausente" 
                          for col in schema_result["expected_columns"]]
            })
            st.dataframe(expected_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("**📊 Colunas do Seu Arquivo:**")
            current_df = pd.DataFrame({
                "Coluna": schema_result["current_columns"],
                "Status": ["✅ Esperada" if col in schema_result["expected_columns"] else "🆕 Nova" 
                          for col in schema_result["current_columns"]]
            })
            st.dataframe(current_df, use_container_width=True, hide_index=True)
        
        # Problemas específicos com design melhorado
        if schema_result["missing_columns"]:
            st.markdown("#### ❌ Colunas Obrigatórias Ausentes")
            missing_df = pd.DataFrame({
                "Coluna Ausente": schema_result["missing_columns"],
                "Impacto": ["Alto"] * len(schema_result["missing_columns"])
            })
            st.dataframe(missing_df, use_container_width=True, hide_index=True)
        
        if schema_result["extra_columns"]:
            st.markdown("#### 🆕 Novas Colunas Detectadas")
            extra_df = pd.DataFrame({
                "Nova Coluna": schema_result["extra_columns"],
                "Ação": ["Será consolidada"] * len(schema_result["extra_columns"])
            })
            st.dataframe(extra_df, use_container_width=True, hide_index=True)
    
    # Aviso importante com design melhorado
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #ffebcd 0%, #ffd6a5 100%);
            border-left: 5px solid #ff6b6b;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.2);
        ">
            <h4 style="color: #d63031; margin: 0 0 15px 0;">⚠️ UPLOAD BLOQUEADO</h4>
            <p style="margin: 0; color: #2d3436; line-height: 1.6;">
                <strong>A estrutura das colunas não está compatível com o Power BI.</strong><br>
                Entre em contato com a <strong>DSViewData</strong> para informar que houve mudança no nome das colunas.<br><br>
                📧 <strong>Ação necessária:</strong> Solicite a atualização do schema no sistema.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    return False

def show_duplicate_analysis(df: pd.DataFrame) -> str:
    """Exibe análise de duplicatas melhorada"""
    duplicate_info = DataValidator.get_duplicate_analysis(df)
    
    if not duplicate_info["has_duplicates"]:
        return "keep_all"
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🔄 Análise de Duplicatas")
    
    # Métricas de duplicatas com design moderno
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_custom_metric(
            "Linhas Duplicadas", 
            str(duplicate_info["total_duplicated_rows"]), 
            "🔄"
        )
    
    with col2:
        show_custom_metric(
            "Padrões Únicos", 
            str(duplicate_info["unique_duplicate_patterns"]), 
            "🎯"
        )
    
    with col3:
        show_custom_metric(
            "Impacto", 
            f"{(duplicate_info['total_duplicated_rows']/len(df)*100):.1f}%", 
            "📊"
        )
    
    # Opções de tratamento
    st.markdown("#### ⚙️ Opções de Tratamento")
    
    action = st.radio(
        "Como deseja tratar as duplicatas?",
        options=["keep_all", "remove_all"],
        format_func=lambda x: {
            "keep_all": "🔄 Manter todas as linhas (incluindo duplicatas)",
            "remove_all": "🧹 Remover todas as duplicatas"
        }[x],
        key="duplicate_action"
    )
    
    # Preview das duplicatas
    if st.checkbox("👀 Visualizar duplicatas encontradas"):
        st.markdown("#### 🔍 Duplicatas Detectadas")
        
        # Mostra apenas as primeiras duplicatas para não sobrecarregar
        preview_df = duplicate_info["duplicated_df"].head(20)
        st.dataframe(preview_df, use_container_width=True)
        
        if len(duplicate_info["duplicated_df"]) > 20:
            st.info(f"Mostrando 20 de {len(duplicate_info['duplicated_df'])} linhas duplicadas")
    
    return action

def show_upload_tab(onedrive_manager: OneDriveManager):
    """Interface de upload melhorada"""
    st.markdown("## 📤 Upload de Planilha")
    
    # Upload de arquivo com design melhorado
    uploaded_file = st.file_uploader(
        "📁 Selecione sua planilha",
        type=Config.SUPPORTED_FORMATS,
        help=f"Formatos suportados: {', '.join(Config.SUPPORTED_FORMATS)} | Tamanho máximo: {Config.MAX_FILE_SIZE_MB}MB"
    )
    
    if not uploaded_file:
        # Instruções visuais quando não há arquivo
        st.markdown(
            """
            <div style="
                text-align: center;
                padding: 3rem;
                background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%);
                border-radius: 15px;
                border: 2px dashed #667eea;
                margin: 2rem 0;
            ">
                <h3 style="color: #667eea; margin-bottom: 1rem;">📁 Arraste e solte sua planilha aqui</h3>
                <p style="color: #718096; margin: 0;">
                    Ou clique no botão acima para selecionar um arquivo<br>
                    <small>Formatos aceitos: Excel (.xlsx, .xls) e CSV (.csv)</small>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return
    
    # Validação de tamanho
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > Config.MAX_FILE_SIZE_MB:
        show_custom_alert(
            f"Arquivo muito grande ({file_size_mb:.1f}MB). Limite: {Config.MAX_FILE_SIZE_MB}MB",
            "error", "⚠️"
        )
        return
    
    # Informações do arquivo com design moderno
    st.markdown("### 📋 Informações do Arquivo")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        show_custom_metric("Nome", uploaded_file.name, "📄")
    with col2:
        show_custom_metric("Tamanho", f"{file_size_mb:.2f} MB", "💾")
    with col3:
        show_custom_metric("Tipo", uploaded_file.type or "Desconhecido", "🔧")
    
    # Leitura do arquivo
    try:
        if uploaded_file.name.lower().endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            sheet_name = None
        else:
            # Para arquivos Excel, verificar múltiplas abas
            excel_file = pd.ExcelFile(uploaded_file)
            sheets = excel_file.sheet_names
            
            if len(sheets) > 1:
                st.markdown("#### 📋 Seleção de Aba")
                sheet_name = st.selectbox("Escolha a aba:", sheets)
            else:
                sheet_name = sheets[0]
                show_custom_alert(f"Aba selecionada: {sheet_name}", "info", "📋")
            
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
    
    except Exception as e:
        show_custom_alert(f"Erro ao ler arquivo: {str(e)}", "error", "❌")
        return
    
    # Preview dos dados com design melhorado
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 👀 Preview dos Dados")
    
    # Container para o preview
    with st.container():
        st.dataframe(
            df.head(10), 
            use_container_width=True, 
            height=350
        )
        
        if len(df) > 10:
            st.caption(f"Mostrando 10 de {len(df)} linhas")
    
    # Análise de qualidade dos dados com métricas modernas
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📊 Análise de Qualidade")
    
    analysis = DataValidator.analyze_data_quality(df)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        show_custom_metric("Linhas", f"{analysis['total_rows']:,}", "📏")
    with col2:
        show_custom_metric("Colunas", str(analysis["total_columns"]), "📊")
    with col3:
        show_custom_metric("Duplicatas", str(analysis["duplicate_rows"]), "🔄")
    with col4:
        show_custom_metric("Memória", f"{analysis['memory_usage']:.2f} MB", "💾")
    
    # Validação de colunas
    valid_columns, invalid_columns = DataValidator.validate_column_names(df)
    
    if invalid_columns:
        show_custom_alert(
            f"Colunas com nomes inválidos: {', '.join(invalid_columns)}",
            "error", "🚫"
        )
        st.info("💡 **Dica:** Renomeie as colunas para conter apenas letras, números e sublinhados")
    
    if analysis["null_columns"]:
        show_custom_alert(
            f"Colunas com valores nulos: {', '.join(analysis['null_columns'])}",
            "warning", "⚠️"
        )
    
    # VALIDAÇÃO DE SCHEMA MELHORADA
    schema_valid = show_schema_validation(df, uploaded_file.name)
    
    # Se schema inválido, bloquear upload
    if not schema_valid:
        st.stop()  # Para a execução aqui
    
    # Análise de duplicatas aprimorada
    duplicate_action = "keep_all"  # Valor padrão
    
    if analysis["duplicate_rows"] > 0:
        duplicate_action = show_duplicate_analysis(df)
    
    # Opções de upload com design moderno
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### ⚙️ Opções de Upload")
    
    show_custom_alert(
        "Backup automático: O sistema fará backup automaticamente de qualquer arquivo existente com o mesmo nome",
        "info", "📦"
    )
    
    confirmar_upload = st.checkbox("✅ Confirmo que os dados estão corretos e autorizo o upload")
    
    # Botão de upload
    if not confirmar_upload:
        show_custom_alert("Marque a confirmação para habilitar o upload", "warning", "⚠️")
        return
    
    if st.button("📤 Realizar Upload", type="primary", use_container_width=True):
        token = onedrive_manager.get_token()
        if not token:
            show_custom_alert("Erro na autenticação", "error", "❌")
            return
        
        with st.spinner("📤 Enviando arquivo..."):
            progress_bar = st.progress(0)
            
            # Processa o arquivo baseado na ação escolhida para duplicatas
            df_final = df.copy()
            
            if duplicate_action == "remove_all" and analysis["duplicate_rows"] > 0:
                df_final = df.drop_duplicates()
                show_custom_alert(
                    f"Duplicatas removidas: {len(df) - len(df_final)} linhas eliminadas",
                    "info", "🧹"
                )
            
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
                show_custom_alert("🎉 Arquivo enviado com sucesso!", "success", "🎉")
                
                # Mostra estatísticas do upload
                if duplicate_action == "remove_all" and analysis["duplicate_rows"] > 0:
                    st.markdown(
                        f"""
                        **📊 Estatísticas do Upload:**
                        - Linhas originais: {len(df):,}
                        - Linhas enviadas: {len(df_final):,}
                        - Duplicatas removidas: {len(df) - len(df_final):,}
                        """
                    )
                
                st.balloons()
                
                # Log da operação
                logger.info(f"Upload bem-sucedido: {uploaded_file.name} ({file_size_mb:.2f}MB)")
                
            else:
                show_custom_alert(f"Erro no upload (Código: {status})", "error", "❌")
                st.code(resposta, language="text")

def show_management_tab(onedrive_manager: OneDriveManager):
    """Interface para gerenciar arquivos melhorada"""
    st.markdown("## 📂 Gerenciar Arquivos")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Atualizar Lista", type="secondary"):
            st.rerun()
    
    token = onedrive_manager.get_token()
    if not token:
        show_custom_alert("Erro na autenticação", "error", "❌")
        return
    
    with st.spinner("📂 Carregando arquivos..."):
        arquivos = onedrive_manager.list_files(token)
    
    if not arquivos:
        st.markdown(
            """
            <div style="
                text-align: center;
                padding: 3rem;
                background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%);
                border-radius: 15px;
                margin: 2rem 0;
            ">
                <h3 style="color: #667eea;">📭 Nenhum arquivo encontrado</h3>
                <p style="color: #718096;">Nenhum arquivo de planilha foi encontrado na pasta configurada.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return
    
    show_custom_alert(f"{len(arquivos)} arquivo(s) encontrado(s)", "info", "📊")
    
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
    
    # Exibe a tabela com design melhorado
    st.markdown("### 📋 Lista de Arquivos")
    st.dataframe(
        df_arquivos[["📄 Nome", "📊 Tamanho", "📅 Modificado"]], 
        use_container_width=True,
        hide_index=True
    )
    
    # Seção para ações nos arquivos
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🛠️ Ações nos Arquivos")
    
    arquivo_selecionado = st.selectbox(
        "Selecione um arquivo:",
        options=range(len(arquivos)),
        format_func=lambda x: f"📄 {arquivos[x]['name']}"
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
                    show_custom_alert("Link não disponível", "error", "❌")
        
        with col2:
            if st.button("📋 Copiar Link", use_container_width=True):
                download_url = arq.get('@microsoft.graph.downloadUrl')
                if download_url:
                    st.code(download_url)
                    show_custom_alert("Link exibido acima", "success", "✅")
        
        with col3:
            if st.button("🗑️ Deletar", use_container_width=True, type="secondary"):
                if st.checkbox(f"⚠️ Confirmar exclusão de '{arq['name']}'"):
                    with st.spinner("🗑️ Deletando..."):
                        sucesso = onedrive_manager.delete_file(token, arq['id'])
                        if sucesso:
                            show_custom_alert("Arquivo deletado!", "success", "✅")
                            st.rerun()
                        else:
                            show_custom_alert("Erro ao deletar arquivo", "error", "❌")

# === FUNÇÃO PRINCIPAL ===
def main():
    """Função principal da aplicação"""
    # Carrega CSS customizado
    load_custom_css()
    
    # Exibe cabeçalho moderno
    show_header()
    
    # Inicializa o gerenciador OneDrive
    onedrive_manager = OneDriveManager()
    
    # Sidebar moderna para navegação
    with st.sidebar:
        st.markdown("### 🧭 Navegação")
        aba = st.radio(
            "Escolha uma opção:",
            ["📤 Upload de Planilha", "📂 Gerenciar Arquivos"],
            key="navigation_radio"
        )
        
        st.markdown("---")
        st.markdown("### ℹ️ Configurações")
        
        # Informações em cards
        st.markdown(
            f"""
            <div style="
                background: white;
                padding: 1rem;
                border-radius: 8px;
                margin: 0.5rem 0;
                border-left: 4px solid #667eea;
            ">
                <strong>📁 Pasta:</strong><br>
                <small>{Config.PASTA}</small>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown(
            f"""
            <div style="
                background: white;
                padding: 1rem;
                border-radius: 8px;
                margin: 0.5rem 0;
                border-left: 4px solid #28a745;
            ">
                <strong>📊 Formatos:</strong><br>
                <small>{', '.join(Config.SUPPORTED_FORMATS)}</small>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown(
            f"""
            <div style="
                background: white;
                padding: 1rem;
                border-radius: 8px;
                margin: 0.5rem 0;
                border-left: 4px solid #ffc107;
            ">
                <strong>📏 Limite:</strong><br>
                <small>{Config.MAX_FILE_SIZE_MB}MB</small>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Mostra schemas disponíveis
        st.markdown("---")
        st.markdown("### 📋 Schemas Configurados")
        if Config.EXPECTED_SCHEMAS:
            for filename, columns in Config.EXPECTED_SCHEMAS.items():
                with st.expander(f"📄 {filename}", expanded=False):
                    st.markdown(f"**Total de colunas:** {len(columns)}")
                    for i, col in enumerate(columns[:5]):  # Mostra apenas as primeiras 5
                        st.markdown(f"• `{col}`")
                    if len(columns) > 5:
                        st.markdown(f"... e mais {len(columns) - 5} colunas")
        else:
            st.info("Nenhum schema configurado")
    
    # Exibe a aba selecionada
    if aba == "📤 Upload de Planilha":
        show_upload_tab(onedrive_manager)
    elif aba == "📂 Gerenciar Arquivos":
        show_management_tab(onedrive_manager)

if __name__ == "__main__":
    main()

