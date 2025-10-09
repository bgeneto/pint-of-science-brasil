"""
Modelos de Dados - Pydantic e SQLAlchemy

Este módulo contém todos os modelos de dados do sistema, incluindo:
- Modelos Pydantic para validação de dados
- Modelos SQLAlchemy para ORM (Object-Relational Mapping)
"""

from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    Text,
    ForeignKey,
    LargeBinary,
    create_engine,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session, sessionmaker
from sqlalchemy.pool import StaticPool
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


# Base para modelos SQLAlchemy
Base = declarative_base()


# ============= MODELOS SQLALCHEMY =============


class Evento(Base):
    """Modelo SQLAlchemy para a tabela eventos."""

    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ano = Column(Integer, nullable=False, unique=True)
    datas_evento = Column(JSON, nullable=False)  # Store list of date objects
    data_criacao = Column(
        Text, nullable=False, default=lambda: datetime.now().isoformat()
    )

    # Relacionamentos
    participantes = relationship("Participante", back_populates="evento")

    def __repr__(self):
        return f"<Evento(id={self.id}, ano={self.ano})>"


class Cidade(Base):
    """Modelo SQLAlchemy para a tabela cidades."""

    __tablename__ = "cidades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(Text, nullable=False)
    estado = Column(Text, nullable=False)  # Sigla com 2 caracteres

    # Relacionamentos
    participantes = relationship("Participante", back_populates="cidade")
    coordenadores = relationship("CoordenadorCidadeLink", back_populates="cidade")

    def __repr__(self):
        return f"<Cidade(id={self.id}, nome={self.nome}, estado={self.estado})>"


class Funcao(Base):
    """Modelo SQLAlchemy para a tabela funcoes."""

    __tablename__ = "funcoes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_funcao = Column(Text, nullable=False, unique=True)

    # Relacionamentos
    participantes = relationship("Participante", back_populates="funcao")

    def __repr__(self):
        return f"<Funcao(id={self.id}, nome_funcao={self.nome_funcao})>"


class Coordenador(Base):
    """Modelo SQLAlchemy para a tabela coordenadores."""

    __tablename__ = "coordenadores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    senha_hash = Column(Text, nullable=False)
    is_superadmin = Column(Boolean, nullable=False, default=False)
    session_token = Column(
        Text, nullable=True, unique=True
    )  # New field for session persistence

    # Relacionamentos
    cidades = relationship("CoordenadorCidadeLink", back_populates="coordenador")
    auditorias = relationship("Auditoria", back_populates="coordenador")

    def __repr__(self):
        return f"<Coordenador(id={self.id}, email={self.email}, superadmin={self.is_superadmin})>"


class CoordenadorCidadeLink(Base):
    """Modelo SQLAlchemy para a tabela de relacionamento N:N entre coordenadores e cidades."""

    __tablename__ = "coordenador_cidade_link"

    coordenador_id = Column(Integer, ForeignKey("coordenadores.id"), primary_key=True)
    cidade_id = Column(Integer, ForeignKey("cidades.id"), primary_key=True)

    # Relacionamentos
    coordenador = relationship("Coordenador", back_populates="cidades")
    cidade = relationship("Cidade", back_populates="coordenadores")

    def __repr__(self):
        return f"<CoordenadorCidadeLink(coordenador_id={self.coordenador_id}, cidade_id={self.cidade_id})>"


class Participante(Base):
    """Modelo SQLAlchemy para a tabela participantes."""

    __tablename__ = "participantes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_completo_encrypted = Column(LargeBinary, nullable=False)
    email_encrypted = Column(LargeBinary, nullable=False)
    titulo_apresentacao = Column(Text, nullable=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    cidade_id = Column(Integer, ForeignKey("cidades.id"), nullable=False)
    funcao_id = Column(Integer, ForeignKey("funcoes.id"), nullable=False)
    datas_participacao = Column(Text, nullable=False)
    carga_horaria_calculada = Column(Integer, nullable=False)
    validado = Column(Boolean, nullable=False, default=False)
    data_inscricao = Column(
        Text, nullable=False, default=lambda: datetime.now().isoformat()
    )

    # Relacionamentos
    evento = relationship("Evento", back_populates="participantes")
    cidade = relationship("Cidade", back_populates="participantes")
    funcao = relationship("Funcao", back_populates="participantes")

    def __repr__(self):
        return f"<Participante(id={self.id}, validado={self.validado})>"


class Auditoria(Base):
    """Modelo SQLAlchemy para a tabela auditoria."""

    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Text, nullable=False, default=lambda: datetime.now().isoformat())
    coordenador_id = Column(Integer, ForeignKey("coordenadores.id"), nullable=False)
    acao = Column(Text, nullable=False)
    detalhes = Column(Text, nullable=True)

    # Relacionamentos
    coordenador = relationship("Coordenador", back_populates="auditorias")

    def __repr__(self):
        return f"<Auditoria(id={self.id}, acao={self.acao}, coordenador_id={self.coordenador_id})>"


# ============= MODELOS PYDANTIC =============


# Eventos
class EventoBase(BaseModel):
    ano: int = Field(..., gt=2000, lt=2100)
    datas_evento: List[str] = Field(..., min_length=1)

    model_config = ConfigDict(from_attributes=True)


class EventoCreate(EventoBase):
    pass


class EventoRead(EventoBase):
    id: int
    data_criacao: str

    model_config = ConfigDict(from_attributes=True)


# Cidades
class CidadeBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    estado: str = Field(..., min_length=2, max_length=2)

    @field_validator("estado")
    @classmethod
    def validate_estado(cls, v):
        if not v.isalpha() or len(v) != 2:
            raise ValueError("Estado deve ser uma sigla de 2 letras")
        return v.upper()

    model_config = ConfigDict(from_attributes=True)


class CidadeCreate(CidadeBase):
    pass


class CidadeRead(CidadeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Funções
class FuncaoBase(BaseModel):
    nome_funcao: str = Field(..., min_length=1, max_length=100)

    model_config = ConfigDict(from_attributes=True)


class FuncaoCreate(FuncaoBase):
    pass


class FuncaoRead(FuncaoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Coordenadores
class CoordenadorBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    is_superadmin: bool = False

    model_config = ConfigDict(from_attributes=True)


class CoordenadorCreate(CoordenadorBase):
    senha: str = Field(..., min_length=8)

    @field_validator("senha")
    @classmethod
    def validate_senha(cls, v):
        if len(v) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")
        return v


class CoordenadorLogin(BaseModel):
    email: EmailStr
    senha: str


class CoordenadorRead(CoordenadorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CoordenadorCreateDB(CoordenadorBase):
    senha_hash: str

    model_config = ConfigDict(from_attributes=True)


# Participantes
class ParticipanteBase(BaseModel):
    nome_completo: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    titulo_apresentacao: Optional[str] = Field(None, max_length=200)
    evento_id: int = Field(..., gt=0)
    cidade_id: int = Field(..., gt=0)
    funcao_id: int = Field(..., gt=0)
    datas_participacao: str = Field(..., min_length=1, max_length=200)
    carga_horaria_calculada: int = Field(..., ge=0)

    @field_validator("nome_completo")
    @classmethod
    def validate_nome(cls, v):
        if not v.strip():
            raise ValueError("Nome não pode estar vazio")
        return v.strip()

    model_config = ConfigDict(from_attributes=True)


class ParticipanteCreate(ParticipanteBase):
    pass


class ParticipanteRead(BaseModel):
    id: int
    nome_completo: str  # Descriptografado
    email: str  # Descriptografado
    titulo_apresentacao: Optional[str]
    evento_id: int
    cidade_id: int
    funcao_id: int
    datas_participacao: str
    carga_horaria_calculada: int
    validado: bool
    data_inscricao: str

    model_config = ConfigDict(from_attributes=True)


# Auditoria
class AuditoriaBase(BaseModel):
    acao: str = Field(..., min_length=1, max_length=100)
    detalhes: Optional[str] = Field(None, max_length=500)

    model_config = ConfigDict(from_attributes=True)


class AuditoriaCreate(AuditoriaBase):
    coordenador_id: int = Field(..., gt=0)


class AuditoriaRead(AuditoriaBase):
    id: int
    timestamp: str
    coordenador_id: int

    model_config = ConfigDict(from_attributes=True)


# ============= FUNÇÕES ÚTEIS =============


def get_all_table_models() -> List[type]:
    """Retorna todos os modelos de tabela SQLAlchemy."""
    return [
        Evento,
        Cidade,
        Funcao,
        Coordenador,
        CoordenadorCidadeLink,
        Participante,
        Auditoria,
    ]


def create_database_engine(database_url: str):
    """Cria e retorna uma engine de banco de dados."""
    if database_url.startswith("sqlite://"):
        return create_engine(
            database_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False, "timeout": 20},
            echo=False,
        )
    else:
        return create_engine(database_url, echo=False)


def get_session_factory(engine):
    """Cria uma factory de sessões do banco de dados."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
