"""
Configurações centrais do sistema Pint of Science Certificate System

Este módulo é responsável por carregar e gerenciar todas as configurações
do sistema, incluindo variáveis de ambiente e configurações de aplicação.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Settings:
    """Classe de configurações centralizadas do sistema."""

    def __init__(self):
        # Carregar variáveis de ambiente
        env_path = Path(__file__).parent.parent / ".env"
        load_dotenv(env_path)

        # Configurações do Banco de Dados
        self.database_url: str = os.getenv(
            "DATABASE_URL", "sqlite:///./pint_of_science.db"
        )

        # Configurações de Criptografia
        self.encryption_key: Optional[str] = os.getenv("ENCRYPTION_KEY")

        # Configurações do Serviço de E-mail (Brevo)
        self.brevo_api_key: Optional[str] = os.getenv("BREVO_API_KEY")
        self.brevo_sender_email: Optional[str] = os.getenv("BREVO_SENDER_EMAIL")
        self.brevo_sender_name: str = os.getenv(
            "BREVO_SENDER_NAME", "Pint of Science Brasil"
        )

        # Configurações do Streamlit
        self.streamlit_server_port: int = int(
            os.getenv("STREAMLIT_SERVER_PORT", "8501")
        )
        self.streamlit_server_address: str = os.getenv(
            "STREAMLIT_SERVER_ADDRESS", "localhost"
        )

        # Configurações da Aplicação
        self.app_name: str = os.getenv("APP_NAME", "Pint of Science Certificate System")
        self.app_version: str = os.getenv("APP_VERSION", "1.0.0")
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"

        # Configurações de Auditoria
        self.enable_audit_logging: bool = (
            os.getenv("ENABLE_AUDIT_LOGGING", "false").lower() == "true"
        )

        # Configurações do Superadmin Inicial (opcional)
        self.initial_superadmin_email: Optional[str] = os.getenv(
            "INITIAL_SUPERADMIN_EMAIL"
        )
        self.initial_superadmin_password: Optional[str] = os.getenv(
            "INITIAL_SUPERADMIN_PASSWORD"
        )
        self.initial_superadmin_name: Optional[str] = os.getenv(
            "INITIAL_SUPERADMIN_NAME"
        )

        # Validação de configurações obrigatórias
        self._validate_config()

    def _validate_config(self) -> None:
        """Valida se as configurações obrigatórias estão presentes."""
        if not self.encryption_key:
            raise ValueError(
                "ENCRYPTION_KEY não configurada! "
                "Gere uma chave com: from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
            )

        if not self.brevo_api_key:
            print(
                "⚠️ AVISO: BREVO_API_KEY não configurada. Funcionalidades de e-mail estarão desabilitadas."
            )

        if not self.brevo_sender_email:
            print(
                "⚠️ AVISO: BREVO_SENDER_EMAIL não configurado. Funcionalidades de e-mail estarão desabilitadas."
            )

    @property
    def is_email_configured(self) -> bool:
        """Verifica se o serviço de e-mail está configurado."""
        return bool(self.brevo_api_key and self.brevo_sender_email)

    @property
    def db_path(self) -> Path:
        """Retorna o caminho do arquivo do banco de dados."""
        if self.database_url.startswith("sqlite:///"):
            return Path(self.database_url.replace("sqlite:///", ""))
        return Path("pint_of_science.db")


# Instância global de configurações
settings = Settings()
