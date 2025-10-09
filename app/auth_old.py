"""
Módulo de Autenticação e Gerenciamento de Sessão

Este módulo é responsável por gerenciar a autenticação de coordenadores,
incluindo login, logout, verificação de permissões e gerenciamento de sessão
do Streamlit.
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import bcrypt
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

from .core import settings
from .models import Coordenador, CoordenadorLogin
from .db import get_coordenador_repository, get_auditoria_repository, db_manager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize cookie manager
cookies = EncryptedCookieManager(
    prefix="pint_app_", password="pint_of_science_super_secret_cookie_key_2024"
)

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
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15


def validar_credenciais_login(email: str, senha: str) -> str:
    """
    Valida as credenciais de login e retorna uma mensagem de erro amigável se houver problemas.

    Args:
        email: Email fornecido
        senha: Senha fornecida

    Returns:
        String vazia se válido, ou mensagem de erro amigável
    """
    # Validar email
    if not email or not email.strip():
        return "Por favor, informe seu endereço de e-mail."

    email = email.strip().lower()

    # Verificar formato básico do email
    if "@" not in email:
        return "O e-mail deve conter o símbolo @."

    if "." not in email.split("@")[1]:
        return "O e-mail deve ter um domínio válido (exemplo: gmail.com)."

    # Verificar se tem pelo menos um ponto após o @
    dominio = email.split("@")[1]
    if not dominio or dominio.startswith(".") or dominio.endswith("."):
        return "O domínio do e-mail não parece válido."

    # Validar senha
    if not senha:
        return "Por favor, informe sua senha."

    if len(senha) < 6:
        return "A senha deve ter pelo menos 6 caracteres."

    return ""  # Sem erros


class AuthManager:
    """Gerenciador central de autenticação."""

    def __init__(self):
        self._login_attempts: Dict[str, Dict[str, Any]] = {}

    def hash_password(self, password: str) -> str:
        """Gera um hash seguro para a senha usando bcrypt."""
        try:
            # Gerar salt e hash
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
            return hashed.decode("utf-8")
        except Exception as e:
            logger.error(f"❌ Erro ao gerar hash da senha: {e}")
            raise ValueError("Erro ao processar senha")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifica se a senha corresponde ao hash armazenado."""
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"), hashed_password.encode("utf-8")
            )
        except Exception as e:
            logger.error(f"❌ Erro ao verificar senha: {e}")
            return False

    def _is_login_locked(self, email: str) -> bool:
        """Verifica se o login está bloqueado por muitas tentativas."""
        if email not in self._login_attempts:
            return False

        attempts = self._login_attempts[email]
        if attempts["count"] >= MAX_LOGIN_ATTEMPTS:
            lock_time = attempts["lock_time"]
            if datetime.now() < lock_time:
                return True
            else:
                # Resetar bloqueio após o tempo expirar
                del self._login_attempts[email]
                return False

        return False

    def _record_login_attempt(self, email: str, success: bool) -> None:
        """Registra uma tentativa de login."""
        if email not in self._login_attempts:
            self._login_attempts[email] = {"count": 0, "lock_time": None}

        attempts = self._login_attempts[email]

        if success:
            # Resetar contador em caso de sucesso
            attempts["count"] = 0
            attempts["lock_time"] = None
        else:
            # Incrementar contador em caso de falha
            attempts["count"] += 1

            # Bloquear se atingir o limite
            if attempts["count"] >= MAX_LOGIN_ATTEMPTS:
                attempts["lock_time"] = datetime.now() + timedelta(
                    minutes=LOGIN_LOCKOUT_MINUTES
                )
                logger.warning(
                    f"🔒 Login bloqueado para {email} por {LOGIN_LOCKOUT_MINUTES} minutos"
                )

    def authenticate_coordenador(self, credentials: CoordenadorLogin) -> Optional[int]:
        """
        Autentica um coordenador com base nas credenciais fornecidas.

        Args:
            credentials: Credenciais de login (email e senha)

        Returns:
            ID do coordenador autenticado ou None se falhar
        """
        email = credentials.email.lower().strip()

        # Verificar se está bloqueado
        if self._is_login_locked(email):
            remaining_time = self._login_attempts[email]["lock_time"] - datetime.now()
            minutes_left = int(remaining_time.total_seconds() / 60)
            logger.warning(
                f"🔒 Tentativa de login bloqueada para {email}. Restam {minutes_left} minutos."
            )
            raise ValueError(
                f"Login temporariamente bloqueado. Tente novamente em {minutes_left} minutos."
            )

        try:
            with db_manager.get_db_session() as session:
                coord_repo = get_coordenador_repository(session)
                auditoria_repo = get_auditoria_repository(session)

                # Buscar coordenador pelo email
                coordenador = coord_repo.get_by_email(email)

                if not coordenador:
                    self._record_login_attempt(email, False)
                    logger.warning(f"❌ Falha de login: Email não encontrado - {email}")
                    raise ValueError("Email ou senha incorretos")

                # Verificar senha
                if not self.verify_password(credentials.senha, coordenador.senha_hash):
                    self._record_login_attempt(email, False)
                    logger.warning(f"❌ Falha de login: Senha incorreta - {email}")
                    raise ValueError("Email ou senha incorretos")

                # Login bem-sucedido
                self._record_login_attempt(email, True)

                # Registrar auditoria
                if settings.enable_audit_logging:
                    auditoria_repo.create_audit_log(
                        coordenador_id=coordenador.id,
                        acao="LOGIN_SUCCESS",
                        detalhes=f"Login realizado via interface web",
                    )

                logger.info(f"✅ Login bem-sucedido: {coordenador.email}")
                return coordenador.id

        except ValueError:
            raise  # Re-raise ValueError para mensagens específicas
        except Exception as e:
            logger.error(f"❌ Erro durante autenticação: {e}")
            raise ValueError("Erro durante autenticação. Tente novamente.")

    def create_session(self, coordenador_id: int) -> None:
        """
        Cria uma sessão de usuário no Streamlit session state e persiste via token.
        """
        try:
            with db_manager.get_db_session() as session:
                coord_repo = get_coordenador_repository(session)
                coordenador = coord_repo.get_by_id(Coordenador, coordenador_id)

                if not coordenador:
                    raise ValueError(
                        f"Coordenador com ID {coordenador_id} não encontrado"
                    )

                # Generate a secure session token
                session_token = secrets.token_urlsafe(32)

                # Store token in database
                coordenador.session_token = session_token
                session.commit()

                # Store token in cookie for persistence
                try:
                    # Wait for cookies to be ready before saving
                    if not cookies.ready():
                        logger.warning(
                            "Cookies not ready during session creation, cannot persist session"
                        )
                        logger.warning(
                            "User will need to login again after page refresh"
                        )
                    else:
                        cookies["session_token"] = session_token
                        cookies.save()
                        logger.info("🍪 Session token saved to cookie successfully")
                except Exception as e:
                    logger.warning(f"Failed to save session token to cookie: {e}")
                    logger.warning("User will need to login again after page refresh")

                # Obter cidades permitidas para o coordenador
                allowed_cities = []
                if not coordenador.is_superadmin:
                    # Aqui precisaríamos implementar um método para obter as cidades do coordenador
                    # Por enquanto, vamos deixar como lista vazia para não-coordenadores superadmin
                    pass

                # Preencher session state - verificar se estamos em contexto Streamlit
                try:
                    st.session_state[SESSION_KEYS["logged_in"]] = True
                    st.session_state[SESSION_KEYS["user_id"]] = coordenador.id
                    st.session_state[SESSION_KEYS["user_email"]] = coordenador.email
                    st.session_state[SESSION_KEYS["user_name"]] = coordenador.nome
                    st.session_state[SESSION_KEYS["is_superadmin"]] = (
                        coordenador.is_superadmin
                    )
                    st.session_state[SESSION_KEYS["login_time"]] = datetime.now()
                    st.session_state[SESSION_KEYS["last_activity"]] = datetime.now()
                    st.session_state[SESSION_KEYS["allowed_cities"]] = allowed_cities

                    logger.info(f"✅ Sessão criada para: {coordenador.email}")
                except Exception as e:
                    # Estamos fora do contexto Streamlit ou outro erro de sessão
                    logger.info(
                        f"✅ Autenticação bem-sucedida para: {coordenador.email} (contexto não-Streamlit ou erro de sessão: {e})"
                    )
                    # Não lançar erro para não quebrar testes fora do contexto Streamlit

        except Exception as e:
            logger.error(f"❌ Erro ao criar sessão: {e}")
            # Quando estamos fora do contexto Streamlit, não lançar erro
            try:
                # Verificar se estamos em contexto Streamlit
                _ = st.session_state
                # Se chegamos aqui, estamos em contexto Streamlit, então lançar erro
                raise ValueError("Erro ao criar sessão de usuário")
            except:
                # Estamos fora do contexto Streamlit, apenas logar
                logger.info("⚠️ Sessão não criada (contexto não-Streamlit)")
                return

    def restore_session_from_token(self, token: str) -> bool:
        """
        Restaura sessão a partir de um token válido.
        """
        try:
            with db_manager.get_db_session() as session:
                coord_repo = get_coordenador_repository(session)
                coordenador = (
                    session.query(Coordenador)
                    .filter(Coordenador.session_token == token)
                    .first()
                )

                if not coordenador:
                    return False

                # Restore session state without generating a new token
                allowed_cities = []
                if not coordenador.is_superadmin:
                    # Implement cities logic if needed
                    pass

                # Preencher session state - verificar se estamos em contexto Streamlit
                try:
                    st.session_state[SESSION_KEYS["logged_in"]] = True
                    st.session_state[SESSION_KEYS["user_id"]] = coordenador.id
                    st.session_state[SESSION_KEYS["user_email"]] = coordenador.email
                    st.session_state[SESSION_KEYS["user_name"]] = coordenador.nome
                    st.session_state[SESSION_KEYS["is_superadmin"]] = (
                        coordenador.is_superadmin
                    )
                    st.session_state[SESSION_KEYS["login_time"]] = datetime.now()
                    st.session_state[SESSION_KEYS["last_activity"]] = datetime.now()
                    st.session_state[SESSION_KEYS["allowed_cities"]] = allowed_cities

                    return True
                except Exception as e:
                    return True
        except Exception as e:
            return False

    def destroy_session(self) -> None:
        """Destroi a sessão atual do usuário."""
        try:
            user_email = st.session_state.get(SESSION_KEYS["user_email"])

            # Clear token from database
            if user_email:
                try:
                    with db_manager.get_db_session() as session:
                        coord_repo = get_coordenador_repository(session)
                        coordenador = coord_repo.get_by_email(user_email)
                        if coordenador:
                            coordenador.session_token = None
                            session.commit()
                except Exception as e:
                    logger.warning(f"⚠️ Não foi possível limpar token: {e}")

            # Limpar session state
            for key in SESSION_KEYS.values():
                if key in st.session_state:
                    del st.session_state[key]

            # Clear query params
            if "session_token" in st.query_params:
                del st.query_params["session_token"]

            # Clear session token cookie
            try:
                if "session_token" in cookies:
                    del cookies["session_token"]
                    cookies.save()
                    logger.info("🍪 Session token cleared from cookie")
            except Exception as e:
                logger.warning(f"Failed to clear session token from cookie: {e}")

            # Registrar auditoria de logout se existir usuário
            if user_email:
                try:
                    with db_manager.get_db_session() as session:
                        coord_repo = get_coordenador_repository(session)
                        auditoria_repo = get_auditoria_repository(session)

                        coordenador = coord_repo.get_by_email(user_email)
                        if coordenador:
                            if settings.enable_audit_logging:
                                auditoria_repo.create_audit_log(
                                    coordenador_id=coordenador.id,
                                    acao="LOGOUT",
                                    detalhes="Logout realizado via interface web",
                                )
                except Exception as e:
                    logger.warning(
                        f"⚠️ Não foi possível registrar auditoria de logout: {e}"
                    )

            logger.info(f"✅ Sessão destruída para: {user_email}")

        except Exception as e:
            logger.error(f"❌ Erro ao destruir sessão: {e}")

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
                self.destroy_session()
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

    def require_authentication(self) -> None:
        """
        Verifica se o usuário está autenticado. Se não estiver, tenta restaurar via token.
        """
        # First, check if we have a valid session
        if self.is_session_valid():
            return

        # If no valid session, try to restore from token
        # Note: The pages should already handle waiting for cookies.ready()
        # before calling this method, but we'll check anyway
        try:
            if not cookies.ready():
                # Cookies not ready yet - stop and let page wait
                st.info("🔄 Carregando sessão... Por favor, aguarde.")
                st.stop()

            token = cookies.get("session_token")
            if token:
                logger.info(
                    f"🍪 Retrieved token from cookie: {token[:20] if token else 'None'}"
                )
                if self.restore_session_from_token(token):
                    logger.info(
                        "✅ Session restored from cookie token in require_authentication"
                    )
                    return  # Session restored
        except Exception as e:
            logger.warning(f"Failed to retrieve session token from cookie: {e}")

        # If neither session nor token worked, require login
        st.error("⚠️ Você precisa estar logado para acessar esta página.")
        if st.button("↩️ Ir para Login", type="primary", use_container_width=True):
            st.session_state["redirect_to_login"] = True
            st.switch_page("Home.py")
        st.stop()

    def require_superadmin(self) -> None:
        """
        Verifica se o usuário é superadmin. Se não estiver, exibe mensagem
        de erro e interrompe a execução da página.
        """
        self.require_authentication()

        if not st.session_state.get(SESSION_KEYS["is_superadmin"], False):
            st.error("⚠️ Acesso negado. Você não tem permissão de superadmin.")
            st.stop()

    def can_access_city(self, cidade_id: int) -> bool:
        """
        Verifica se o usuário tem permissão para acessar uma cidade específica.

        Args:
            cidade_id: ID da cidade a verificar

        Returns:
            True se tem permissão, False caso contrário
        """
        if not self.is_session_valid():
            return False

        # Superadmin tem acesso a todas as cidades
        if st.session_state.get(SESSION_KEYS["is_superadmin"], False):
            return True

        # Verificar se a cidade está na lista de cidades permitidas
        allowed_cities = st.session_state.get(SESSION_KEYS["allowed_cities"], [])
        return cidade_id in allowed_cities

    def update_user_activity(self) -> None:
        """Atualiza o timestamp da última atividade do usuário."""
        if self.is_authenticated():
            st.session_state[SESSION_KEYS["last_activity"]] = datetime.now()


# Instância global do gerenciador de autenticação
auth_manager = AuthManager()


# ============= FUNÇÕES DE CONVENIÊNCIA =============


def login_coordenador(email: str, senha: str) -> bool:
    """
    Função de conveniência para realizar login de coordenador.

    Args:
        email: Email do coordenador
        senha: Senha do coordenador

    Returns:
        True se login bem-sucedido, False caso contrário
    """
    try:
        # Validação customizada com mensagens amigáveis
        erro_validacao = validar_credenciais_login(email, senha)
        if erro_validacao:
            try:
                st.error(f"❌ {erro_validacao}")
            except:
                # Estamos fora do contexto Streamlit
                pass
            return False

        credentials = CoordenadorLogin(email=email, senha=senha)
        coordenador_id = auth_manager.authenticate_coordenador(credentials)

        if coordenador_id:
            auth_manager.create_session(coordenador_id)
            return True

        return False

    except Exception as e:
        logger.error(f"❌ Erro no login: {str(e)}")
        try:
            st.error(f"❌ Erro no login: {str(e)}")
        except:
            # Estamos fora do contexto Streamlit
            pass
        return False


def logout_coordenador() -> None:
    """Função de conveniência para realizar logout do coordenador atual."""
    auth_manager.destroy_session()
    st.rerun()


def is_user_logged_in() -> bool:
    """Verifica se o usuário está logado."""
    return auth_manager.is_session_valid()


def get_current_user_info() -> Optional[Dict[str, Any]]:
    """Retorna informações do usuário atual."""
    return auth_manager.get_current_user()


def require_login() -> None:
    """Exige que o usuário esteja logado para continuar."""
    auth_manager.require_authentication()


def require_superadmin() -> None:
    """Exige que o usuário seja superadmin para continuar."""
    auth_manager.require_superadmin()


def can_access_cidade(cidade_id: int) -> bool:
    """Verifica se o usuário pode acessar uma cidade específica."""
    return auth_manager.can_access_city(cidade_id)


def criar_coordenador(
    nome: str, email: str, senha: str, is_superadmin: bool = False
) -> bool:
    """
    Cria um novo coordenador no sistema.

    Args:
        nome: Nome do coordenador
        email: Email do coordenador
        senha: Senha do coordenador
        is_superadmin: Se é superadmin ou não

    Returns:
        True se criado com sucesso, False caso contrário
    """
    try:
        # Hash da senha
        senha_hash = auth_manager.hash_password(senha)

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

            logger.info(f"✅ Coordenador criado: {email}")
            return True

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao criar coordenador: {e}")
        raise ValueError("Erro ao criar coordenador")


def alterar_senha_coordenador(email: str, senha_atual: str, nova_senha: str) -> bool:
    """
    Altera a senha de um coordenador.

    Args:
        email: Email do coordenador
        senha_atual: Senha atual
        nova_senha: Nova senha

    Returns:
        True se alterada com sucesso, False caso contrário
    """
    try:
        with db_manager.get_db_session() as session:
            coord_repo = get_coordenador_repository(session)
            auditoria_repo = get_auditoria_repository(session)

            # Buscar coordenador
            coordenador = coord_repo.get_by_email(email)
            if not coordenador:
                raise ValueError("Coordenador não encontrado")

            # Verificar senha atual
            if not auth_manager.verify_password(senha_atual, coordenador.senha_hash):
                raise ValueError("Senha atual incorreta")

            # Atualizar senha
            nova_senha_hash = auth_manager.hash_password(nova_senha)
            coordenador.senha_hash = nova_senha_hash
            session.merge(coordenador)

            # Registrar auditoria
            current_user = get_current_user_info()
            if current_user and settings.enable_audit_logging:
                auditoria_repo.create_audit_log(
                    coordenador_id=current_user["id"],
                    acao="CHANGE_PASSWORD",
                    detalhes=f"Senha alterada para: {email}",
                )

            logger.info(f"✅ Senha alterada para: {email}")
            return True

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao alterar senha: {e}")
        raise ValueError("Erro ao alterar senha")
