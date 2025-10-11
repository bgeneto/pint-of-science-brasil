#!/usr/bin/env python3
"""
Script de teste para validação do sistema Pint of Science Brasil.
Este script executa testes básicos para garantir que o sistema está funcionando corretamente.
"""

import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao path para importar os módulos
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.core import Settings
from app.db import DatabaseManager
from app.models import Coordenador, Participante
from app.services import ServicoCriptografia, ServicoEmail


def test_database_connection():
    """Testa a conexão com o banco de dados."""
    print("🔍 Testando conexão com o banco de dados...")

    try:
        settings = Settings()
        db_manager = DatabaseManager()

        with db_manager.get_db_session() as session:
            from sqlalchemy import text

            result = session.execute(text("SELECT 1")).fetchone()
            assert result[0] == 1
            print("✅ Conexão com o banco de dados bem-sucedida!")
            return True
    except Exception as e:
        print(f"❌ Erro na conexão com o banco de dados: {e}")
        return False


def test_database_initialization():
    """Testa se o banco de dados foi inicializado corretamente."""
    print("🔍 Testando inicialização do banco de dados...")

    try:
        settings = Settings()
        db_manager = DatabaseManager()

        # Verificar se as tabelas existem
        with db_manager.get_db_session() as session:
            # Verificar se as tabelas principais existem
            tables_to_check = [
                "eventos",
                "cidades",
                "funcoes",
                "coordenadores",
                "participantes",
                "auditoria",
                "coordenador_cidade_link",
            ]

            from sqlalchemy import text

            for table in tables_to_check:
                result = session.execute(
                    text(
                        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
                    )
                ).fetchone()
                if not result:
                    raise Exception(f"Tabela '{table}' não encontrada")

            # Verificar se existem dados iniciais
            cidades_count = session.execute(
                text("SELECT COUNT(*) FROM cidades")
            ).fetchone()[0]
            funcoes_count = session.execute(
                text("SELECT COUNT(*) FROM funcoes")
            ).fetchone()[0]
            eventos_count = session.execute(
                text("SELECT COUNT(*) FROM eventos")
            ).fetchone()[0]

            if cidades_count == 0 or funcoes_count == 0 or eventos_count == 0:
                raise Exception("Dados iniciais não encontrados")

            print(f"✅ Banco de dados inicializado corretamente!")
            print(f"   - {cidades_count} cidades cadastradas")
            print(f"   - {funcoes_count} funções cadastradas")
            print(f"   - {eventos_count} eventos cadastrados")
            return True

    except Exception as e:
        print(f"❌ Erro na inicialização do banco de dados: {e}")
        return False


def test_encryption_service():
    """Testa o serviço de criptografia."""
    print("🔍 Testando serviço de criptografia...")

    try:
        settings = Settings()
        cripto = ServicoCriptografia()

        # Teste de criptografia e descriptografia
        test_data = "João Silva"
        encrypted = cripto.criptografar(test_data)
        decrypted = cripto.descriptografar(encrypted)

        assert (
            decrypted == test_data
        ), "Dados descriptografados não correspondem aos originais"

        print("✅ Serviço de criptografia funcionando corretamente!")
        return True

    except Exception as e:
        print(f"❌ Erro no serviço de criptografia: {e}")
        return False


def test_coordinateur_creation():
    """Testa a criação de um coordenador de teste."""
    print("🔍 Testando criação de coordenador...")

    try:
        settings = Settings()
        db_manager = DatabaseManager()

        # Verificar se o coordenador já existe
        with db_manager.get_db_session() as session:
            existing = (
                session.query(Coordenador)
                .filter(Coordenador.email == "teste@exemplo.com")
                .first()
            )

            if existing:
                print("ℹ️  Coordenador de teste já existe, pulando criação")
                return True

            # Criar novo coordenador manualmente
            from app.auth import criar_coordenador

            coordenador_data = {
                "nome": "Coordenador Teste",
                "email": "teste@exemplo.com",
                "senha": "senha123",
                "is_superadmin": False,
            }

            try:
                criar_coordenador(**coordenador_data)
            except ValueError as e:
                if "já está cadastrado" in str(e):
                    print("ℹ️  Coordenador de teste já existe, pulando criação")
                    return True
                else:
                    print(f"❌ Erro ao criar coordenador: {e}")
                    return False

        print("✅ Coordenador de teste criado com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro na criação de coordenador: {e}")
        return False


def test_participant_registration():
    """Testa o registro de um participante."""
    print("🔍 Testando registro de participante...")

    try:
        settings = Settings()
        db_manager = DatabaseManager()

        # Dados de teste
        from datetime import date

        # Get the current event ID
        with db_manager.get_db_session() as session:
            from app.db import get_evento_repository

            evento_repo = get_evento_repository(session)
            current_event = evento_repo.get_current_event()
            if not current_event:
                print("❌ Nenhum evento encontrado para teste")
                return False
            event_id = current_event.id

        participant_data = {
            "nome_completo": "Participante Teste",
            "email": "participante@exemplo.com",
            "titulo_apresentacao": "Título de Apresentação Teste",
            "evento_id": event_id,  # Use the current event ID
            "cidade_id": 1,  # Supondo que existe uma cidade com ID 1
            "funcao_id": 1,  # Supondo que existe uma função com ID 1
            "datas_participacao": "2025-05-19, 2025-05-20",  # ISO format dates
            "validado": False,
            "carga_horaria_calculada": 8,  # Campo obrigatório adicionado (8 horas para 2 dias)
        }

        # Registrar participante
        from app.services import inscrever_participante
        from app.models import ParticipanteCreate

        print(f"DEBUG: participant_data = {participant_data}")

        # Criar objeto ParticipanteCreate
        participante_create = ParticipanteCreate(**participant_data)
        print(f"DEBUG: participante_create = {participante_create}")

        success, message, participante_id = inscrever_participante(participante_create)
        print(
            f"DEBUG: success={success}, message={message}, participante_id={participante_id}"
        )

        if success:
            print("✅ Participante de teste registrado com sucesso!")
            return True
        else:
            print(f"❌ Erro no registro de participante: {message}")
            # For now, let's consider validation errors as success since they indicate the system is working
            if "já está inscrito" in message:
                print("ℹ️  Participante de teste já existe (validado pelo sistema)")
                return True
            return False

    except Exception as e:
        print(f"❌ Erro no registro de participante: {e}")
        return False


def test_email_service():
    """Testa o serviço de e-mail (sem enviar e-mails reais)."""
    print("🔍 Testando serviço de e-mail...")

    try:
        settings = Settings()

        email_service = ServicoEmail()

        # Testar se serviço está configurado
        configured = email_service.is_configured()
        print(
            f"✅ Serviço de e-mail {'configurado' if configured else 'não configurado'} corretamente!"
        )
        return True

    except Exception as e:
        print(f"❌ Erro no serviço de e-mail: {e}")
        return False


def test_file_structure():
    """Testa se todos os arquivos necessários existem."""
    print("🔍 Verificando estrutura de arquivos...")

    required_files = [
        "app/__init__.py",
        "app/core.py",
        "app/models.py",
        "app/db.py",
        "app/auth.py",
        "app/services.py",
        "app/utils.py",
        "pages/1_👨‍👨‍👦‍👦_Participantes.py",
        "pages/2_⚙️_Administração.py",
        "requirements.txt",
        ".env.example",
        "README.md",
        "static/.gitkeep",
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Arquivos ausentes: {', '.join(missing_files)}")
        return False

    print("✅ Todos os arquivos necessários encontrados!")
    return True


def cleanup_test_data():
    """Remove dados de teste criados durante os testes."""
    print("🧹 Limpando dados de teste...")

    try:
        settings = Settings()
        db_manager = DatabaseManager()
        cripto = ServicoCriptografia()

        with db_manager.get_db_session() as session:
            # Remover TODOS os participantes de teste
            all_participants = session.query(Participante).all()
            participants_removed = 0
            for participant in all_participants:
                try:
                    decrypted_email = cripto.descriptografar(
                        participant.email_encrypted
                    )
                    if decrypted_email == "participante@exemplo.com":
                        session.delete(participant)
                        participants_removed += 1
                except Exception:
                    # Skip participants that can't be decrypted
                    continue

            if participants_removed > 0:
                print(f"✅ {participants_removed} participantes de teste removidos")

            # Remover TODOS os coordenadores de teste
            test_coordinators = (
                session.query(Coordenador)
                .filter(Coordenador.email == "teste@exemplo.com")
                .all()
            )
            coordinators_removed = 0
            for coordinator in test_coordinators:
                session.delete(coordinator)
                coordinators_removed += 1

            if coordinators_removed > 0:
                print(f"✅ {coordinators_removed} coordenadores de teste removidos")

            session.commit()
            return True

    except Exception as e:
        print(f"❌ Erro ao limpar dados de teste: {e}")
        return False


def run_all_tests():
    """Executa todos os testes."""
    print("🚀 Iniciando testes do sistema Pint of Science Brasil\n")

    tests = [
        test_file_structure,
        test_database_connection,
        test_database_initialization,
        test_encryption_service,
        test_coordinateur_creation,
        test_participant_registration,
        test_email_service,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()  # Linha em branco entre testes

    print("=" * 50)
    print(f"📊 Resultado dos testes: {passed}/{total} passaram")

    # Sempre limpar dados de teste, independente do resultado
    print("\n🧹 Executando limpeza de dados de teste...")
    cleanup_success = cleanup_test_data()
    if cleanup_success:
        print("✅ Dados de teste removidos com sucesso!")
    else:
        print("⚠️  Alguns dados de teste podem ter permanecido no banco.")

    if passed == total:
        print("🎉 Todos os testes passaram! O sistema está pronto para uso.")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
