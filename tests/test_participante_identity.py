import sqlite3
import sys
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from sqlalchemy.exc import IntegrityError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.core import settings
from app.db import db_manager, get_participante_repository
from app.models import Cidade, Evento, Funcao, Participante, ParticipanteCreate
from app.services import (
    baixar_certificado,
    gerador_certificado,
    inscrever_participante,
    servico_criptografia,
    servico_email,
)
from utils.migrate_participante_identity_funcao import (
    migrate_participante_identity_funcao,
)


@pytest.fixture()
def temp_database(monkeypatch, tmp_path):
    db_path = tmp_path / "pint_test.db"
    monkeypatch.setattr(settings, "database_url", f"sqlite:///{db_path}")
    monkeypatch.setattr(servico_email, "_configured", False)

    db_manager.engine = None
    db_manager.session_factory = None
    db_manager._initialized = False
    db_manager.initialize()

    with db_manager.get_db_session() as session:
        cidade = Cidade(nome="São Paulo", estado="SP")
        funcao_palestrante = Funcao(nome_funcao="Palestrante")
        funcao_voluntario = Funcao(nome_funcao="Voluntário(a)")
        funcao_organizador = Funcao(nome_funcao="Organizador")
        evento_2025 = Evento(ano=2025, datas_evento=["2025-05-19"])
        evento_2026 = Evento(ano=2026, datas_evento=["2026-05-18"])
        session.add_all(
            [
                cidade,
                funcao_palestrante,
                funcao_voluntario,
                funcao_organizador,
                evento_2025,
                evento_2026,
            ]
        )
        session.flush()
        context = {
            "cidade_id": cidade.id,
            "palestrante_id": funcao_palestrante.id,
            "voluntario_id": funcao_voluntario.id,
            "organizador_id": funcao_organizador.id,
            "evento_2025_id": evento_2025.id,
            "evento_2026_id": evento_2026.id,
        }

    yield context

    if db_manager.engine:
        db_manager.engine.dispose()
    db_manager.engine = None
    db_manager.session_factory = None
    db_manager._initialized = False


def _dados_inscricao(
    context,
    *,
    email="multi@example.com",
    evento_id=None,
    funcao_id=None,
    data="2025-05-19",
):
    return ParticipanteCreate(
        nome_completo="Participante Teste",
        email=email,
        titulo_apresentacao="Ciência no Bar",
        evento_id=evento_id or context["evento_2025_id"],
        cidade_id=context["cidade_id"],
        funcao_id=funcao_id or context["palestrante_id"],
        datas_participacao=data,
    )


def test_same_email_same_event_different_funcao_allowed(temp_database):
    sucesso, _, participante_1 = inscrever_participante(
        _dados_inscricao(
            temp_database,
            funcao_id=temp_database["palestrante_id"],
        )
    )
    assert sucesso is True
    assert participante_1 is not None

    sucesso, _, participante_2 = inscrever_participante(
        _dados_inscricao(
            temp_database,
            funcao_id=temp_database["voluntario_id"],
        )
    )
    assert sucesso is True
    assert participante_2 is not None
    assert participante_2 != participante_1


def test_same_email_event_and_funcao_rejected_by_validation_and_db(temp_database):
    dados = _dados_inscricao(
        temp_database,
        funcao_id=temp_database["palestrante_id"],
    )
    sucesso, _, _ = inscrever_participante(dados)
    assert sucesso is True

    sucesso, mensagem, participante_id = inscrever_participante(dados)
    assert sucesso is False
    assert participante_id is None
    assert "email já está inscrito neste evento com esta função" in mensagem

    session = db_manager.get_session()
    try:
        participante_repo = get_participante_repository(session)
        email_hash = servico_criptografia.gerar_hash_email("db-unique@example.com")
        encrypted_email = servico_criptografia.criptografar_email(
            "db-unique@example.com"
        )
        encrypted_name = servico_criptografia.criptografar_nome("DB Unique")
        kwargs = dict(
            nome_completo_encrypted=encrypted_name,
            email_encrypted=encrypted_email,
            email_hash=email_hash,
            titulo_apresentacao=None,
            evento_id=temp_database["evento_2025_id"],
            cidade_id=temp_database["cidade_id"],
            funcao_id=temp_database["palestrante_id"],
            datas_participacao="2025-05-19",
            validado=False,
        )
        participante_repo.create_participante(**kwargs)
        session.commit()

        with pytest.raises(IntegrityError):
            participante_repo.create_participante(**kwargs)
            session.commit()
    finally:
        session.rollback()
        session.close()


def test_same_email_different_event_same_funcao_allowed(temp_database):
    sucesso, _, participante_1 = inscrever_participante(
        _dados_inscricao(
            temp_database,
            funcao_id=temp_database["palestrante_id"],
        )
    )
    assert sucesso is True

    sucesso, _, participante_2 = inscrever_participante(
        _dados_inscricao(
            temp_database,
            evento_id=temp_database["evento_2026_id"],
            funcao_id=temp_database["palestrante_id"],
            data="2026-05-18",
        )
    )
    assert sucesso is True
    assert participante_2 != participante_1


def test_certificate_download_uses_email_event_and_funcao(monkeypatch, temp_database):
    email = "certificados@example.com"
    sucesso, _, palestrante_id = inscrever_participante(
        _dados_inscricao(
            temp_database,
            email=email,
            funcao_id=temp_database["palestrante_id"],
        )
    )
    assert sucesso is True

    sucesso, _, voluntario_id = inscrever_participante(
        _dados_inscricao(
            temp_database,
            email=email,
            funcao_id=temp_database["voluntario_id"],
        )
    )
    assert sucesso is True

    with db_manager.get_db_session() as session:
        session.get(Participante, palestrante_id).validado = True

    monkeypatch.setattr(
        gerador_certificado,
        "gerar_certificado_pdf",
        lambda participante, evento, cidade, funcao: b"%PDF-identity-test",
    )

    sucesso, pdf_bytes, _ = baixar_certificado(
        email,
        temp_database["evento_2025_id"],
        temp_database["palestrante_id"],
    )
    assert sucesso is True
    assert pdf_bytes == b"%PDF-identity-test"

    sucesso, pdf_bytes, mensagem = baixar_certificado(
        email,
        temp_database["evento_2025_id"],
        temp_database["organizador_id"],
    )
    assert sucesso is False
    assert pdf_bytes is None
    assert "não inscrito neste evento com esta função" in mensagem

    sucesso, pdf_bytes, mensagem = baixar_certificado(
        email,
        temp_database["evento_2025_id"],
        temp_database["voluntario_id"],
    )
    assert sucesso is False
    assert pdf_bytes is None
    assert "ainda não foi validada" in mensagem

    assert voluntario_id is not None


def test_repository_detects_admin_edit_identity_collision(temp_database):
    sucesso, _, participante_1 = inscrever_participante(
        _dados_inscricao(
            temp_database,
            email="original@example.com",
            funcao_id=temp_database["palestrante_id"],
        )
    )
    assert sucesso is True

    sucesso, _, participante_2 = inscrever_participante(
        _dados_inscricao(
            temp_database,
            email="edit-target@example.com",
            funcao_id=temp_database["palestrante_id"],
        )
    )
    assert sucesso is True

    with db_manager.get_db_session() as session:
        participante_repo = get_participante_repository(session)
        email_hash = servico_criptografia.gerar_hash_email("original@example.com")
        collision = participante_repo.get_by_email_evento_funcao(
            email_hash,
            temp_database["evento_2025_id"],
            temp_database["palestrante_id"],
            exclude_participante_id=participante_2,
        )
        collision_id = collision.id if collision else None

    assert collision_id == participante_1


def _legacy_schema(connection: sqlite3.Connection, *, unique_email: bool) -> None:
    unique_clause = " UNIQUE" if unique_email else ""
    connection.execute(
        f"""
        CREATE TABLE participantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo_encrypted BLOB NOT NULL,
            email_encrypted BLOB NOT NULL,
            email_hash TEXT NOT NULL{unique_clause},
            titulo_apresentacao TEXT,
            evento_id INTEGER NOT NULL,
            cidade_id INTEGER NOT NULL,
            funcao_id INTEGER NOT NULL,
            datas_participacao TEXT NOT NULL,
            validado BOOLEAN NOT NULL DEFAULT 0,
            data_inscricao TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            hash_validacao TEXT
        )
        """
    )


def _insert_legacy_participant(
    connection: sqlite3.Connection,
    *,
    email: str,
    evento_id: int,
    funcao_id: int,
) -> None:
    fernet = Fernet(settings.encryption_key.encode())
    email_hash = servico_criptografia.gerar_hash_email(email)
    connection.execute(
        """
        INSERT INTO participantes (
            nome_completo_encrypted,
            email_encrypted,
            email_hash,
            titulo_apresentacao,
            evento_id,
            cidade_id,
            funcao_id,
            datas_participacao,
            validado,
            data_inscricao
        )
        VALUES (?, ?, ?, NULL, ?, 1, ?, '2025-05-19', 0, '2025-01-01T00:00:00')
        """,
        (
            fernet.encrypt(b"Participante Legado"),
            fernet.encrypt(email.encode("utf-8")),
            email_hash,
            evento_id,
            funcao_id,
        ),
    )


def test_identity_migration_rebuilds_legacy_unique_email_schema(tmp_path):
    db_path = tmp_path / "legacy_unique.db"
    connection = sqlite3.connect(db_path)
    try:
        _legacy_schema(connection, unique_email=True)
        _insert_legacy_participant(
            connection, email="one@example.com", evento_id=1, funcao_id=1
        )
        _insert_legacy_participant(
            connection, email="two@example.com", evento_id=1, funcao_id=1
        )
        connection.commit()
    finally:
        connection.close()

    result = migrate_participante_identity_funcao(db_path)
    assert result["rebuilt_table"] is True

    second_result = migrate_participante_identity_funcao(db_path)
    assert second_result["rebuilt_table"] is False

    connection = sqlite3.connect(db_path)
    try:
        table_info = connection.execute("PRAGMA table_info('participantes')").fetchall()
        email_hash_column = next(row for row in table_info if row[1] == "email_hash")
        assert email_hash_column[3] == 1

        indexes = connection.execute("PRAGMA index_list('participantes')").fetchall()
        index_columns = {
            row[1]: [
                info[2]
                for info in connection.execute(f"PRAGMA index_info('{row[1]}')").fetchall()
            ]
            for row in indexes
        }
        assert ["email_hash", "evento_id", "funcao_id"] in index_columns.values()
        assert not any(
            row[2] and index_columns[row[1]] == ["email_hash"] for row in indexes
        )
    finally:
        connection.close()


def test_identity_migration_reports_duplicate_composite_identity(tmp_path):
    db_path = tmp_path / "legacy_duplicate.db"
    connection = sqlite3.connect(db_path)
    try:
        _legacy_schema(connection, unique_email=False)
        _insert_legacy_participant(
            connection, email="duplicate@example.com", evento_id=1, funcao_id=1
        )
        _insert_legacy_participant(
            connection, email="duplicate@example.com", evento_id=1, funcao_id=1
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="email/evento/função"):
        migrate_participante_identity_funcao(db_path)
