"""
Módulo de Autenticação Simplificado - Streamlit Authenticator

Este módulo usa streamlit-authenticator para gerenciar autenticação de forma
simples e confiável, sem os problemas de timing de cookies.
"""

import logging
import streamlit as st
import streamlit_authenticator as stauth
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from .core import settings
from .models import Coordenador
from .db import get_coordenador_repository, get_auditoria_repository, db_manager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chaves do session state do Streamlit
SESSION_KEYS = {
    "logged_in": "logged_in",
    "user_id": "user_id",
    "user_email": "user_email",
    "user_name": "user_name",
    "is_superadmin": "is_superadmin",
    "login_time": "login_time",
    "last_activity": "last_activity",
    "allowed_cities": "allowed_cities",
}

# Constantes de configuração
SESSION_TIMEOUT_MINUTES = 120  # 2 horas


class AuthManager:
    """Gerenciador de autenticação usando streamlit-authenticator."""

    def __init__(self):
        """Inicializa o gerenciador de autenticação."""
        self.authenticator = None
        self._initialize_authenticator()

    def _initialize_authenticator(self):
        """Inicializa o streamlit-authenticator com dados do banco."""
        try:
            # Buscar todos os coordenadores do banco
            credentials = self._load_credentials_from_db()
            
            if not credentials:
                logger.warning("Nenhum coordenador encontrado no banco de dados")
                credentials = {"usernames": {}}

            # Configurar authenticator
            self.authenticator = stauth.Authenticate(
                credentials,
                cookie_name='pint_auth_cookie',
                key='pint_of_science_auth_key_2024',  # Change this to a secure random key
                cookie_expiry_days=30,
                preauthorized=None
            )
            
            logger.info("✅ Authenticator inicializado com sucesso")

        except Exception as e:
            logger.error(f"❌ Erro ao inicializar authenticator: {e}")
            # Criar authenticator vazio para não quebrar
            self.authenticator = stauth.Authenticate(
                {"usernames": {}},
                cookie_name='pint_auth_cookie',
                key='pint_of_science_auth_key_2024',
                cookie_expiry_days=30
            )

    def _load_credentials_from_db(self) -> Dict:
        """Carrega credenciais do banco de dados."""
        credentials = {"usernames": {}}
        
        try:
            with db_manager.get_db_session() as session:
                coord_repo = get_coordenador_repository(session)
                coordenadores = coord_repo.get_all(Coordenador)
                
                for coord in coordenadores:
                    # streamlit-authenticator espera um formato específico
                    credentials["usernames"][coord.email] = {
                        "email": coord.email,
                        "name": coord.nome,
                        "password": coord.senha_hash,  # Já está hasheada com bcrypt
                    }
                    
                logger.info(f"✅ Carregadas credenciais de {len(coordenadores)} coordenadores")
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar credenciais: {e}")
            
        return credentials

    def show_login_form(self, location: str = "main") -> tuple:
        """
        Exibe o formulário de login usando streamlit-authenticator.
        
        Args:
            location: Onde exibir o form ('main' ou 'sidebar')
            
        Returns:
            Tupla (nome, status_autenticacao, email)
        """
        if not self.authenticator:
            self._initialize_authenticator()
            
        name, authentication_status, username = self.authenticator.login(
            'Login',
            location
        )
        
        return name, authentication_status, username

    def handle_login_result(self, name: str, authentication_status: bool, username: str) -> bool:
        """
        Processa o resultado do login.
        
        Args:
            name: Nome do usuário
            authentication_status: Status da autenticação
            username: Email/username do usuário
            
        Returns:
            True se login bem-sucedido
        """
        if authentication_status:
            # Login bem-sucedido
            logger.info(f"✅ Login bem-sucedido: {username}")
            
            # Carregar dados completos do coordenador do banco
            try:
                with db_manager.get_db_session() as session:
                    coord_repo = get_coordenador_repository(session)
                    auditoria_repo = get_auditoria_repository(session)
                    
                    coordenador = coord_repo.get_by_email(username)
                    
                    if coordenador:
                        # Preencher session state com dados do coordenador
                        st.session_state[SESSION_KEYS["logged_in"]] = True
                        st.session_state[SESSION_KEYS["user_id"]] = coordenador.id
                        st.session_state[SESSION_KEYS["user_email"]] = coordenador.email
                        st.session_state[SESSION_KEYS["user_name"]] = coordenador.nome
                        st.session_state[SESSION_KEYS["is_superadmin"]] = coordenador.is_superadmin
                        st.session_state[SESSION_KEYS["login_time"]] = datetime.now()
                        st.session_state[SESSION_KEYS["last_activity"]] = datetime.now()
                        st.session_state[SESSION_KEYS["allowed_cities"]] = []
                        
                        # Registrar auditoria
                        if settings.enable_audit_logging:
                            auditoria_repo.create_audit_log(
                                coordenador_id=coordenador.id,
                                acao="LOGIN_SUCCESS",
                                detalhes=f"Login realizado via streamlit-authenticator"
                            )
                            
                        return True
                        
            except Exception as e:
                logger.error(f"❌ Erro ao processar login: {e}")
                return False
                
        elif authentication_status == False:
            # Login falhou
            st.error("❌ Email ou senha incorretos")
            return False
        elif authentication_status == None:
            # Ainda não tentou fazer login
            return False
            
        return False

    def show_logout_button(self, location: str = "sidebar"):
        """Exibe o botão de logout."""
        if self.authenticator:
            self.authenticator.logout('Sair', location)

    def is_authenticated(self) -> bool:
        """Verifica se o usuário está autenticado."""
        return st.session_state.get(SESSION_KEYS["logged_in"], False)

    def is_session_valid(self) -> bool:
        """Verifica se a sessão é válida (não expirou)."""
        if not self.is_authenticated():
            return False

        try:
            last_activity = st.session_state.get(SESSION_KEYS["last_activity"])
            if not last_activity:
                return False

            # Verificar timeout
            time_diff = datetime.now() - last_activity
            if time_diff > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                logger.info(f"⏰ Sessão expirada por timeout")
                self.clear_session()
                return False

            # Atualizar última atividade
            st.session_state[SESSION_KEYS["last_activity"]] = datetime.now()
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao validar sessão: {e}")
            return False

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Retorna informações do usuário atual."""
        if not self.is_session_valid():
            return None

        return {
            "id": st.session_state.get(SESSION_KEYS["user_id"]),
            "email": st.session_state.get(SESSION_KEYS["user_email"]),
            "name": st.session_state.get(SESSION_KEYS["user_name"]),
            "is_superadmin": st.session_state.get(SESSION_KEYS["is_superadmin"]),
            "login_time": st.session_state.get(SESSION_KEYS["login_time"]),
            "allowed_cities": st.session_state.get(SESSION_KEYS["allowed_cities"], []),
        }

    def clear_session(self):
        """Limpa a sessão do usuário."""
        try:
            user_email = st.session_state.get(SESSION_KEYS["user_email"])
            
            # Registrar auditoria de logout
            if user_email:
                try:
                    with db_manager.get_db_session() as session:
                        coord_repo = get_coordenador_repository(session)
                        auditoria_repo = get_auditoria_repository(session)
                        
                        coordenador = coord_repo.get_by_email(user_email)
                        if coordenador and settings.enable_audit_logging:
                            auditoria_repo.create_audit_log(
                                coordenador_id=coordenador.id,
                                acao="LOGOUT",
                                detalhes="Logout realizado"
                            )
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao registrar auditoria de logout: {e}")
            
            # Limpar session state
            for key in SESSION_KEYS.values():
                if key in st.session_state:
                    del st.session_state[key]
                    
            logger.info(f"✅ Sessão limpa para: {user_email}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar sessão: {e}")

    def require_authentication(self):
        """Verifica se o usuário está autenticado. Se não, mostra erro e para."""
        if not self.is_session_valid():
            st.error("⚠️ Você precisa estar logado para acessar esta página.")
            if st.button("↩️ Ir para Login", type="primary", use_container_width=True):
                st.switch_page("Home.py")
            st.stop()

    def require_superadmin(self):
        """Verifica se o usuário é superadmin."""
        self.require_authentication()
        
        if not st.session_state.get(SESSION_KEYS["is_superadmin"], False):
            st.error("⚠️ Acesso negado. Você não tem permissão de superadmin.")
            st.stop()


# Instância global do gerenciador de autenticação
auth_manager = AuthManager()


# ============= FUNÇÕES DE CONVENIÊNCIA =============

def show_login() -> bool:
    """Exibe formulário de login e retorna True se login bem-sucedido."""
    name, authentication_status, username = auth_manager.show_login_form()
    
    if authentication_status:
        return auth_manager.handle_login_result(name, authentication_status, username)
    elif authentication_status == False:
        return False
    
    return False


def logout():
    """Realiza logout do usuário."""
    auth_manager.clear_session()
    auth_manager.show_logout_button()


def is_user_logged_in() -> bool:
    """Verifica se o usuário está logado."""
    return auth_manager.is_session_valid()


def get_current_user_info() -> Optional[Dict[str, Any]]:
    """Retorna informações do usuário atual."""
    return auth_manager.get_current_user()


def require_login():
    """Exige que o usuário esteja logado para continuar."""
    auth_manager.require_authentication()


def require_superadmin():
    """Exige que o usuário seja superadmin para continuar."""
    auth_manager.require_superadmin()


def criar_coordenador(nome: str, email: str, senha: str, is_superadmin: bool = False) -> bool:
    """
    Cria um novo coordenador no sistema.
    
    Args:
        nome: Nome do coordenador
        email: Email do coordenador
        senha: Senha do coordenador (será hasheada)
        is_superadmin: Se é superadmin ou não
        
    Returns:
        True se criado com sucesso, False caso contrário
    """
    try:
        # Hash da senha usando o método do streamlit-authenticator
        senha_hash = stauth.Hasher([senha]).generate()[0]
        
        with db_manager.get_db_session() as session:
            coord_repo = get_coordenador_repository(session)
            auditoria_repo = get_auditoria_repository(session)
            
            # Verificar se email já existe
            existing = coord_repo.get_by_email(email)
            if existing:
                raise ValueError("Este email já está cadastrado")
            
            # Criar coordenador
            coordenador = coord_repo.create_coordenador(
                nome=nome,
                email=email,
                senha_hash=senha_hash,
                is_superadmin=is_superadmin,
            )
            
            # Registrar auditoria
            current_user = get_current_user_info()
            if current_user and settings.enable_audit_logging:
                auditoria_repo.create_audit_log(
                    coordenador_id=current_user["id"],
                    acao="CREATE_COORDENADOR",
                    detalhes=f"Criado coordenador: {nome} ({email})",
                )
            
            # Reinicializar authenticator para carregar novo usuário
            auth_manager._initialize_authenticator()
            
            logger.info(f"✅ Coordenador criado: {email}")
            return True
            
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao criar coordenador: {e}")
        raise ValueError("Erro ao criar coordenador")
