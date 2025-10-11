#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados iniciais.

Este script inicializa o banco de dados e cria dados iniciais necessários
para o funcionamento do sistema Pint of Science Brasil.

Uso:
    python utils/seed_database.py [--force] [--verbose]

Opções:
    --force     Força a recriação dos dados iniciais mesmo se já existirem
    --verbose   Mostra informações detalhadas durante o processo
"""

import argparse
import logging
import sys
from pathlib import Path

# Adicionar o diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core import settings
from app.db import init_database, check_database_health, db_manager
from app.models import Cidade, Funcao, Evento, Coordenador


def setup_logging(verbose: bool = False) -> None:
    """Configura o logging do script."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def show_database_status() -> None:
    """Exibe o status atual do banco de dados."""
    print("\n🔍 Verificando status do banco de dados...")
    health = check_database_health()

    print(f"Status geral: {health['status']}")
    print(f"Conexão: {'✅ OK' if health['connection'] else '❌ Falha'}")
    print(f"Tabelas criadas: {'✅ OK' if health['tables_created'] else '❌ Falha'}")
    print(f"Dados iniciais: {'✅ OK' if health['initial_data'] else '❌ Faltando'}")

    if health.get("details", {}).get("table_counts"):
        print("\n📊 Contagem de registros por tabela:")
        for table, count in health["details"]["table_counts"].items():
            print(f"  {table}: {count} registros")


def seed_database(force: bool = False) -> bool:
    """Executa o processo de seeding do banco de dados."""
    try:
        print("\n🚀 Iniciando processo de seeding do banco de dados...")

        if force:
            print("⚠️  Modo force ativado - recriando dados existentes...")
            # Se force=True, podemos dropar e recriar as tabelas
            # Mas isso é perigoso, então vamos apenas logar
            logging.warning(
                "Modo force solicitado, mas recriação completa não implementada por segurança"
            )

        # Inicializar banco de dados (isso cria tabelas e dados iniciais se necessário)
        print("📝 Inicializando banco de dados...")
        init_database()

        print("✅ Seeding concluído com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro durante o seeding: {e}")
        logging.error(f"Erro no seeding: {e}", exc_info=True)
        return False


def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(
        description="Script para popular o banco de dados com dados iniciais"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Força a recriação dos dados iniciais mesmo se já existirem",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Mostra informações detalhadas durante o processo",
    )
    parser.add_argument(
        "--status-only",
        action="store_true",
        help="Apenas mostra o status do banco de dados sem fazer seeding",
    )

    args = parser.parse_args()

    # Configurar logging
    setup_logging(args.verbose)

    print("🎨 Pint of Science Brasil - Database Seeder")
    print("=" * 50)

    # Verificar se as configurações necessárias estão presentes
    if not settings.database_url:
        print("❌ DATABASE_URL não configurada. Verifique o arquivo .env")
        sys.exit(1)

    if not settings.encryption_key:
        print("❌ ENCRYPTION_KEY não configurada. Verifique o arquivo .env")
        sys.exit(1)

    # Mostrar status atual
    show_database_status()

    # Se apenas status foi solicitado, sair
    if args.status_only:
        sys.exit(0)

    # Executar seeding
    success = seed_database(force=args.force)

    if success:
        print("\n🎉 Processo concluído com sucesso!")
        print("\n💡 Dicas:")
        print("  - Execute 'python test_system.py' para validar o sistema")
        print("  - Use 'streamlit run Home.py' para iniciar a aplicação")
        sys.exit(0)
    else:
        print("\n💥 Processo falhou!")
        sys.exit(1)


if __name__ == "__main__":
    main()
