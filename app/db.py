"""
Sistema de Gerenciamento de Banco de Dados

Este módulo é responsável por gerenciar todas as operações de banco de dados,
incluindo conexão, inicialização, migrações e repositórios de dados.
"""

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional, Generator, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .core import settings
from .models import (
    Base,
    get_all_table_models,
    create_database_engine,
    get_session_factory,
    Evento,
    Cidade,
    Funcao,
    Coordenador,
    Participante,
    Auditoria,
    CoordenadorCidadeLink,
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gerenciador central do banco de dados."""

    def __init__(self):
        self.engine = None
        self.session_factory = None
        self._initialized = False

    def initialize(self) -> None:
        """Inicializa o banco de dados e cria as tabelas."""
        if self._initialized:
            return

        try:
            # Criar engine
            self.engine = create_database_engine(settings.database_url)

            # Criar tabelas
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Banco de dados inicializado com sucesso!")

            # Criar session factory
            self.session_factory = get_session_factory(self.engine)
            self._initialized = True

        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
            raise

    def get_session(self) -> Session:
        """Retorna uma sessão do banco de dados."""
        if not self._initialized:
            self.initialize()
        return self.session_factory()

    @contextmanager
    def get_db_session(self) -> Generator[Session, None, None]:
        """Context manager para sessão de banco de dados com commit/rollback automático."""
        if not self._initialized:
            self.initialize()

        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Erro na transação do banco de dados: {e}")
            raise
        finally:
            session.close()

    def check_connection(self) -> bool:
        """Verifica se a conexão com o banco de dados está ativa."""
        try:
            if not self._initialized:
                self.initialize()

            with self.get_db_session() as session:
                from sqlalchemy import text

                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"❌ Erro na conexão com o banco de dados: {e}")
            return False

    def get_database_info(self) -> dict:
        """Retorna informações sobre o banco de dados."""
        if not self._initialized:
            self.initialize()

        info = {
            "database_url": settings.database_url,
            "database_path": str(settings.db_path) if settings.db_path else None,
            "database_exists": settings.db_path.exists() if settings.db_path else True,
            "tables_count": len(get_all_table_models()),
            "tables": [model.__tablename__ for model in get_all_table_models()],
        }

        return info


# Instância global do gerenciador de banco de dados
db_manager = DatabaseManager()


# ============= REPOSITÓRIOS =============


class BaseRepository:
    """Classe base para repositórios de dados."""

    def __init__(self, session: Session):
        self.session = session

    def add(self, model_instance: Any) -> Any:
        """Adiciona uma instância ao banco de dados."""
        self.session.add(model_instance)
        self.session.flush()
        return model_instance

    def get_by_id(self, model_class: type, id: int) -> Optional[Any]:
        """Busca uma instância por ID."""
        return self.session.query(model_class).filter(model_class.id == id).first()

    def get_all(self, model_class: type) -> list[Any]:
        """Retorna todas as instâncias de um modelo."""
        return self.session.query(model_class).all()

    def update(self, model_instance: Any) -> Any:
        """Atualiza uma instância no banco de dados."""
        self.session.merge(model_instance)
        self.session.flush()
        return model_instance

    def delete(self, model_instance: Any) -> bool:
        """Remove uma instância do banco de dados."""
        try:
            self.session.delete(model_instance)
            self.session.flush()
            return True
        except Exception:
            return False


class EventoRepository(BaseRepository):
    """Repositório para operações com Eventos."""

    def get_by_ano(self, ano: int) -> Optional[Evento]:
        """Busca um evento pelo ano."""
        return self.session.query(Evento).filter(Evento.ano == ano).first()

    def get_current_event(self) -> Optional[Evento]:
        """Retorna o evento mais recente (ano maior)."""
        return self.session.query(Evento).order_by(Evento.ano.desc()).first()

    def create_evento(self, ano: int, datas_evento) -> Evento:
        """Cria um novo evento."""
        evento = Evento(ano=ano, datas_evento=datas_evento)
        return self.add(evento)


class CidadeRepository(BaseRepository):
    """Repositório para operações com Cidades."""

    def get_by_nome_estado(self, nome: str, estado: str) -> Optional[Cidade]:
        """Busca uma cidade por nome e estado."""
        return (
            self.session.query(Cidade)
            .filter(Cidade.nome == nome, Cidade.estado == estado.upper())
            .first()
        )

    def get_by_nome(self, nome: str) -> Optional[Cidade]:
        """Busca uma cidade pelo nome."""
        return self.session.query(Cidade).filter(Cidade.nome == nome.strip()).first()

    def get_all_ordered(self) -> list[Cidade]:
        """Retorna todas as cidades ordenadas por nome e estado."""
        return self.session.query(Cidade).order_by(Cidade.estado, Cidade.nome).all()

    def create_cidade(self, nome: str, estado: str) -> Cidade:
        """Cria uma nova cidade."""
        cidade = Cidade(nome=nome.strip(), estado=estado.upper())
        return self.add(cidade)


class FuncaoRepository(BaseRepository):
    """Repositório para operações com Funções."""

    def get_by_name(self, nome_funcao: str) -> Optional[Funcao]:
        """Busca uma função pelo nome."""
        return (
            self.session.query(Funcao).filter(Funcao.nome_funcao == nome_funcao).first()
        )

    def get_all_ordered(self) -> list[Funcao]:
        """Retorna todas as funções ordenadas por nome."""
        return self.session.query(Funcao).order_by(Funcao.nome_funcao).all()

    def create_funcao(self, nome_funcao: str) -> Funcao:
        """Cria uma nova função."""
        funcao = Funcao(nome_funcao=nome_funcao.strip())
        return self.add(funcao)


class CoordenadorRepository(BaseRepository):
    """Repositório para operações com Coordenadores."""

    def get_by_email(self, email: str) -> Optional[Coordenador]:
        """Busca um coordenador pelo email."""
        return (
            self.session.query(Coordenador).filter(Coordenador.email == email).first()
        )

    def get_superadmins(self) -> list[Coordenador]:
        """Retorna todos os superadmins."""
        return (
            self.session.query(Coordenador)
            .filter(Coordenador.is_superadmin == True)
            .all()
        )

    def get_first_superadmin(self) -> Optional[Coordenador]:
        """Retorna o primeiro superadmin cadastrado (usado para assinatura do certificado)."""
        return (
            self.session.query(Coordenador)
            .filter(Coordenador.is_superadmin == True)
            .order_by(Coordenador.id.asc())
            .first()
        )

    def get_cidade_coordenadores(self, cidade_id: int) -> list[Coordenador]:
        """Retorna coordenadores de uma cidade específica."""
        return (
            self.session.query(Coordenador)
            .join(CoordenadorCidadeLink)
            .filter(CoordenadorCidadeLink.cidade_id == cidade_id)
            .all()
        )

    def create_coordenador(
        self, nome: str, email: str, senha_hash: str, is_superadmin: bool = False
    ) -> Coordenador:
        """Cria um novo coordenador."""
        coordenador = Coordenador(
            nome=nome.strip(),
            email=email.lower().strip(),
            senha_hash=senha_hash,
            is_superadmin=is_superadmin,
        )
        return self.add(coordenador)

    def link_coordenador_cidade(self, coordenador_id: int, cidade_id: int) -> bool:
        """Associa um coordenador a uma cidade."""
        try:
            link = CoordenadorCidadeLink(
                coordenador_id=coordenador_id, cidade_id=cidade_id
            )
            self.session.add(link)
            self.session.flush()
            return True
        except Exception:
            return False

    def unlink_coordenador_cidade(self, coordenador_id: int, cidade_id: int) -> bool:
        """Remove associação entre coordenador e cidade."""
        try:
            link = (
                self.session.query(CoordenadorCidadeLink)
                .filter(
                    CoordenadorCidadeLink.coordenador_id == coordenador_id,
                    CoordenadorCidadeLink.cidade_id == cidade_id,
                )
                .first()
            )
            if link:
                self.session.delete(link)
                self.session.flush()
                return True
            return False
        except Exception:
            return False


class ParticipanteRepository(BaseRepository):
    """Repositório para operações com Participantes."""

    def get_by_email_hash(
        self, email_hash: str, evento_id: int
    ) -> Optional[Participante]:
        """Busca um participante pelo hash do email e evento."""
        return (
            self.session.query(Participante)
            .filter(
                Participante.email_hash == email_hash,
                Participante.evento_id == evento_id,
            )
            .first()
        )

    def get_by_encrypted_email(
        self, email_encrypted: bytes, evento_id: int
    ) -> Optional[Participante]:
        """Busca um participante pelo email criptografado e evento (deprecated - use get_by_email_hash)."""
        return (
            self.session.query(Participante)
            .filter(
                Participante.email_encrypted == email_encrypted,
                Participante.evento_id == evento_id,
            )
            .first()
        )

    def get_by_evento_cidade(
        self, evento_id: int, cidade_id: Optional[int] = None
    ) -> list[Participante]:
        """Retorna participantes de um evento (opcionalmente filtrado por cidade)."""
        query = self.session.query(Participante).filter(
            Participante.evento_id == evento_id
        )
        if cidade_id:
            query = query.filter(Participante.cidade_id == cidade_id)
        return query.order_by(Participante.data_inscricao.desc()).all()

    def get_validated_participants(
        self, evento_id: int, cidade_id: Optional[int] = None
    ) -> list[Participante]:
        """Retorna participantes validados de um evento."""
        query = self.session.query(Participante).filter(
            Participante.evento_id == evento_id, Participante.validado == True
        )
        if cidade_id:
            query = query.filter(Participante.cidade_id == cidade_id)
        return query.order_by(Participante.data_inscricao.desc()).all()

    def create_participante(self, **kwargs) -> Participante:
        """Cria um novo participante."""
        participante = Participante(**kwargs)
        return self.add(participante)

    def validate_participant(self, participante_id: int) -> bool:
        """Marca um participante como validado."""
        try:
            participante = self.get_by_id(Participante, participante_id)
            if participante:
                participante.validado = True
                self.update(participante)
                return True
            return False
        except Exception:
            return False

    def invalidate_participant(self, participante_id: int) -> bool:
        """Remove a validação de um participante."""
        try:
            participante = self.get_by_id(Participante, participante_id)
            if participante:
                participante.validado = False
                self.update(participante)
                return True
            return False
        except Exception:
            return False


class AuditoriaRepository(BaseRepository):
    """Repositório para operações com Auditoria."""

    def create_audit_log(
        self, coordenador_id: int, acao: str, detalhes: Optional[str] = None
    ) -> Auditoria:
        """Cria um registro de auditoria."""
        auditoria = Auditoria(
            coordenador_id=coordenador_id, acao=acao, detalhes=detalhes
        )
        return self.add(auditoria)

    def get_by_coordenador(
        self, coordenador_id: int, limit: int = 100
    ) -> list[Auditoria]:
        """Retorna registros de auditoria de um coordenador."""
        return (
            self.session.query(Auditoria)
            .filter(Auditoria.coordenador_id == coordenador_id)
            .order_by(Auditoria.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_recent_logs(self, limit: int = 50) -> list[Auditoria]:
        """Retorna os registros mais recentes de auditoria."""
        return (
            self.session.query(Auditoria)
            .order_by(Auditoria.timestamp.desc())
            .limit(limit)
            .all()
        )


# ============= FUNÇÕES DE FÁBRICA =============


def get_evento_repository(session: Session) -> EventoRepository:
    """Retorna uma instância do repositório de eventos."""
    return EventoRepository(session)


def get_cidade_repository(session: Session) -> CidadeRepository:
    """Retorna uma instância do repositório de cidades."""
    return CidadeRepository(session)


def get_funcao_repository(session: Session) -> FuncaoRepository:
    """Retorna uma instância do repositório de funções."""
    return FuncaoRepository(session)


def get_coordenador_repository(session: Session) -> CoordenadorRepository:
    """Retorna uma instância do repositório de coordenadores."""
    return CoordenadorRepository(session)


def get_participante_repository(session: Session) -> ParticipanteRepository:
    """Retorna uma instância do repositório de participantes."""
    return ParticipanteRepository(session)


def get_auditoria_repository(session: Session) -> AuditoriaRepository:
    """Retorna uma instância do repositório de auditoria."""
    return AuditoriaRepository(session)


# ============= FUNÇÕES DE CONVENIÊNCIA =============


def get_db() -> Generator[Session, None, None]:
    """Função para obter sessão do banco de dados (compatível com injeção de dependência)."""
    with db_manager.get_db_session() as session:
        yield session


def init_database() -> None:
    """Inicializa o banco de dados e cria dados iniciais se necessário."""
    db_manager.initialize()

    # Sempre tentar criar dados iniciais (a função é idempotente)
    with db_manager.get_db_session() as session:
        logger.info("📝 Verificando/criando dados iniciais...")
        _create_initial_data(session)
        logger.info("✅ Dados iniciais verificados/criados com sucesso.")


def _create_initial_data(session: Session) -> None:
    """Cria dados iniciais para o sistema."""
    try:
        # Cidades de exemplo (Pint of Science comumente acontece nestas cidades)
        cidades_data = [
            ("São Paulo", "SP"),
            ("Rio de Janeiro", "RJ"),
            ("Belo Horizonte", "MG"),
            ("Porto Alegre", "RS"),
            ("Recife", "PE"),
            ("Salvador", "BA"),
            ("Brasília", "DF"),
            ("Campinas", "SP"),
            ("Fortaleza", "CE"),
            ("Curitiba", "PR"),
        ]

        cidade_repo = get_cidade_repository(session)
        cidades_criadas = 0
        for nome, estado in cidades_data:
            # Verificar se a cidade já existe
            if not cidade_repo.get_by_nome_estado(nome, estado):
                cidade_repo.create_cidade(nome, estado)
                cidades_criadas += 1

        if cidades_criadas > 0:
            logger.info(f"✅ Criadas {cidades_criadas} cidades")

        # Funções de exemplo
        funcoes_data = [
            "Apoio ao Público",
            "Apoio Logístico",
            "Assessor(a) de Bar",
            "Comissão Audiovisual",
            "Comissão Científica",
            "Comissão de Divulgação",
            "Comissão de Infraestrutura e Logística",
            "Comissão Financeira",
            "Comissão Organizadora",
            "Coordenador(a) Acadêmico(a)",
            "Coordenador(a) Adjunto(a)",
            "Coordenador(a) de Bar",
            "Coordenador(a) de Comunicação",
            "Coordenador(a) de Mídias",
            "Coordenador(a) Local",
            "Coordenador(a) Regional",
            "Designer Gráfico",
            "Equipe de Apoio",
            "Equipe de Arte e Design",
            "Equipe Executora",
            "Fotógrafo(a)",
            "Mediador(a)",
            "Palestrante",
            "Técnico Audiovisual",
            "Vice-Coordenador(a) Acadêmico(a)",
            "Vice-Coordenador(a) Adjunto(a)",
            "Vice-Coordenador(a) de Bar",
            "Vice-Coordenador(a) de Comunicação",
            "Vice-Coordenador(a) de Mídias",
            "Vice-Coordenador(a) Geral",
            "Vice-Coordenador(a) Local",
            "Vice-Coordenador(a) Regional",
            "Voluntário(a)",
        ]

        funcao_repo = get_funcao_repository(session)
        funcoes_criadas = 0
        for nome_funcao in funcoes_data:
            # Verificar se a função já existe
            if not funcao_repo.get_by_name(nome_funcao):
                funcao_repo.create_funcao(nome_funcao)
                funcoes_criadas += 1

        if funcoes_criadas > 0:
            logger.info(f"✅ Criadas {funcoes_criadas} funções")

        # Evento atual (2025) - using ISO 8601 format for dates
        evento_repo = get_evento_repository(session)

        # Verificar se o evento 2025 já existe
        evento_2025 = evento_repo.get_by_ano(2025)
        if not evento_2025:
            # Convert date objects to ISO 8601 strings for JSON serialization
            datas_evento_iso = [
                "2025-05-19",  # ISO 8601: YYYY-MM-DD
                "2025-05-20",
                "2025-05-21",
            ]

            evento_2025 = evento_repo.create_evento(
                ano=2025,
                datas_evento=datas_evento_iso,  # Pass the list directly
            )
            logger.info(f"✅ Evento {evento_2025.ano} criado")
        else:
            logger.info(f"✅ Evento {evento_2025.ano} já existe")

        # Seed initial superadmin if configured and none exists
        from app.core import settings
        from app.auth import criar_coordenador

        if (
            settings.initial_superadmin_email
            and settings.initial_superadmin_password
            and settings.initial_superadmin_name
        ):

            coord_repo = get_coordenador_repository(session)
            existing_superadmins = coord_repo.get_superadmins()

            if not existing_superadmins:
                # Create initial superadmin using the auth function (handles password hashing)
                success = criar_coordenador(
                    nome=settings.initial_superadmin_name,
                    email=settings.initial_superadmin_email,
                    senha=settings.initial_superadmin_password,
                    is_superadmin=True,
                )

                if success:
                    logger.info(
                        f"✅ Superadmin inicial criado: {settings.initial_superadmin_email}"
                    )
                else:
                    logger.error(
                        f"❌ Falha ao criar superadmin inicial: {settings.initial_superadmin_email}"
                    )

        logger.info(
            f"✅ Dados iniciais criados com sucesso! Evento {evento_2025.ano} configurado."
        )

    except Exception as e:
        logger.error(f"❌ Erro ao criar dados iniciais: {e}")
        raise


def check_database_health() -> dict:
    """Verifica a saúde do banco de dados."""
    health_info = {
        "status": "healthy",
        "connection": False,
        "tables_created": False,
        "initial_data": False,
        "details": {},
    }

    try:
        # Verificar conexão
        health_info["connection"] = db_manager.check_connection()
        if not health_info["connection"]:
            health_info["status"] = "unhealthy"
            return health_info

        # Verificar tabelas
        with db_manager.get_db_session() as session:
            # Contar registros em cada tabela
            table_counts = {}
            for model in get_all_table_models():
                count = session.query(model).count()
                table_counts[model.__tablename__] = count

            health_info["details"]["table_counts"] = table_counts
            health_info["tables_created"] = all(
                count >= 0 for count in table_counts.values()
            )

            # Verificar dados iniciais
            health_info["initial_data"] = (
                table_counts.get("cidades", 0) > 0
                and table_counts.get("funcoes", 0) > 0
                and table_counts.get("eventos", 0) > 0
            )

            if not health_info["tables_created"]:
                health_info["status"] = "unhealthy"
            elif not health_info["initial_data"]:
                health_info["status"] = "warning"

    except Exception as e:
        health_info["status"] = "error"
        health_info["details"]["error"] = str(e)
        logger.error(f"❌ Erro ao verificar saúde do banco de dados: {e}")

    return health_info
