#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados iniciais.

Este script inicializa o banco de dados e cria dados iniciais necessários
para o funcionamento do sistema Pint of Science Brasil.

Uso:
    python utils/seed_database.py [--force] [--verbose] [--seed-speakers]

Opções:
    --force         Força a recriação dos dados iniciais mesmo se já existirem
    --verbose       Mostra informações detalhadas durante o processo
    --status-only   Apenas mostra o status do banco de dados sem fazer seeding
    --seed-speakers Carrega dados de palestrantes do arquivo CSV
"""

import argparse
import csv
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
import re

# Adicionar o diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core import settings
from app.db import init_database, check_database_health, db_manager
from app.models import Cidade, Funcao, Evento, Coordenador, Participante
from app.services import ServicoCriptografia


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
    print(f"Dados iniciais: {'✅ OK' if health['initial_data'] else '❌ Falha'}")

    if health.get("details", {}).get("table_counts"):
        print("\n📊 Contagem de registros por tabela:")
        for table, count in health["details"]["table_counts"].items():
            print(f"  {table}: {count} registros")


def load_municipios_data() -> Dict[str, str]:
    """
    Carrega os dados de municípios do arquivo CSV.

    Returns:
        Dict[str, str]: Mapeamento de nome da cidade para UF (estado)
    """
    municipios_file = (
        project_root / "utils" / "Lista_Municipios_com_IBGE_Brasil_Versao_CSV.csv"
    )
    municipios_map = {}

    try:
        with open(municipios_file, "r", encoding="utf-8") as f:
            # Detectar delimitador automaticamente
            sample = f.read(1024)
            f.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter

            reader = csv.DictReader(f, delimiter=delimiter)

            for row in reader:
                # Extrair colunas relevantes
                uf = row.get("UF", "").strip()
                municipio = row.get("Município", "").strip()

                if uf and municipio:
                    # Normalizar nome da cidade para busca
                    municipio_key = municipio.lower().strip()
                    municipios_map[municipio_key] = uf

        logging.info(f"✅ Carregados {len(municipios_map)} municípios do arquivo CSV")
        return municipios_map

    except Exception as e:
        logging.error(f"❌ Erro ao carregar dados de municípios: {e}")
        return {}


def parse_portuguese_date(date_str: str) -> Optional[str]:
    """
    Converte uma data em português para formato ISO 8601 (YYYY-MM-DD).

    Args:
        date_str: Data em formato português (ex: "19 de maio de 2025")

    Returns:
        str: Data em formato ISO 8601 ou None se inválida
    """
    try:
        # Mapeamento de meses em português para números
        meses = {
            "janeiro": "01",
            "fevereiro": "02",
            "março": "03",
            "abril": "04",
            "maio": "05",
            "junho": "06",
            "julho": "07",
            "agosto": "08",
            "setembro": "09",
            "outubro": "10",
            "novembro": "11",
            "dezembro": "12",
        }

        # Limpar e normalizar a string
        date_str = date_str.lower().strip()

        # Padrões comuns de data em português
        patterns = [
            # "19 de maio de 2025"
            r"^(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})$",
            # "19 de Maio de 2025" (com maiúscula)
            r"^(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})$",
        ]

        for pattern in patterns:
            match = re.match(pattern, date_str)
            if match:
                dia, mes_nome, ano = match.groups()
                mes_num = meses.get(mes_nome.lower())
                if mes_num:
                    # Formatar como YYYY-MM-DD
                    return f"{ano}-{mes_num}-{int(dia):02d}"

        # Tentar outros formatos comuns
        # Formatos numéricos: DD/MM/YYYY, DD/MM/YY, MM/DD/YYYY, etc.
        numeric_patterns = [
            (
                r"^(\d{1,2})/(\d{1,2})/(\d{4})$",
                "detect",
            ),  # Ambiguous DD/MM/YYYY or MM/DD/YYYY
            (
                r"^(\d{1,2})/(\d{1,2})/(\d{2})$",
                "detect",
            ),  # Ambiguous DD/MM/YY or MM/DD/YY
            (
                r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$",
                lambda d, m, y: f"{y}-{m:02d}-{d:02d}",
            ),  # DD.MM.YYYY
            (
                r"^(\d{1,2})\.(\d{1,2})\.(\d{2})$",
                lambda d, m, y: f"20{y}-{m:02d}-{d:02d}",
            ),  # DD.MM.YY
        ]

        for pattern, formatter in numeric_patterns:
            match = re.match(pattern, date_str)
            if match:
                parts = match.groups()
                try:
                    a, b, y = map(int, parts)

                    # Detect format for ambiguous slash-separated dates
                    if formatter == "detect":
                        # If second number > 12, it's likely MM/DD/YYYY (month can't be > 12)
                        if b > 12:
                            m, d = a, b  # MM/DD/YYYY -> month=a, day=b
                        else:
                            d, m = a, b  # DD/MM/YYYY -> day=a, month=b

                        # Convert 2-digit year to 4-digit
                        if y < 100:
                            y = 2000 + y

                        if 1 <= d <= 31 and 1 <= m <= 12 and y >= 2024:
                            return f"{y}-{m:02d}-{d:02d}"
                    else:
                        # For dot-separated dates, assume DD.MM format
                        d, m, y = a, b, y
                        if 1 <= d <= 31 and 1 <= m <= 12 and y >= 2024:
                            return formatter(d, m, y)
                except ValueError:
                    continue

        # Formatos especiais
        if " a " in date_str and " de " in date_str:
            # Formatos como "19 a 21 de maio de 2025" - pegar apenas a primeira data
            parts = date_str.split(" a ")
            if len(parts) >= 1:
                first_date = parts[0].strip()
                return parse_portuguese_date(first_date)

        logging.warning(f"❌ Formato de data não reconhecido: {date_str}")
        return None

    except Exception as e:
        logging.error(f"❌ Erro ao parsear data '{date_str}': {e}")
        return None


def get_cidade_from_name(
    cidade_nome: str, municipios_map: Dict[str, str], session
) -> Optional[Cidade]:
    """
    Busca ou cria uma cidade no banco de dados.

    Args:
        cidade_nome: Nome da cidade
        municipios_map: Mapeamento de cidades para UFs
        session: Sessão do banco de dados

    Returns:
        Cidade: Instância da cidade ou None se não encontrada
    """
    from app.db import get_cidade_repository

    cidade_repo = get_cidade_repository(session)

    # Primeiro tentar buscar cidade existente
    cidade = cidade_repo.get_by_nome(cidade_nome)
    if cidade:
        return cidade

    # Também tentar buscar pela versão limpa do nome (sem estado)
    separators = ["/", " - ", "-"]
    for separator in separators:
        if separator in cidade_nome:
            parts = cidade_nome.split(separator, 1)
            if len(parts) == 2:
                cidade_base = parts[0].strip()
                if cidade_base != cidade_nome:  # Só buscar se for diferente
                    cidade = cidade_repo.get_by_nome(cidade_base)
                    if cidade:
                        return cidade
            break

    # Se não existe, tentar encontrar a UF no mapeamento
    cidade_key = cidade_nome.lower().strip()
    uf = municipios_map.get(cidade_key)

    if uf:
        # Criar nova cidade
        cidade = cidade_repo.create_cidade(cidade_nome, uf)
        logging.info(f"✅ Cidade criada: {cidade_nome} - {uf}")
        return cidade
    else:
        # Tentar extrair apenas o nome da cidade (remover estado)
        # Formatos comuns: "Cidade/UF", "Cidade - UF", "Cidade-UF"
        cidade_base = None
        uf_extraida = None

        # Primeiro, tentar diferentes separadores
        separators = ["/", " - ", "-"]
        for separator in separators:
            if separator in cidade_nome:
                parts = cidade_nome.split(separator, 1)
                if len(parts) == 2:
                    cidade_base = parts[0].strip()
                    uf_part = parts[1].strip()

                    # Processar a parte da UF para extrair apenas o código do estado
                    # Pode ter duplicações como "MG-MG" ou "PR-PR"
                    uf_parts = [p.strip() for p in uf_part.split("-") if p.strip()]
                    if uf_parts:
                        # Pegar a última parte não vazia como UF
                        uf_extraida = uf_parts[-1].upper()
                        # Se há mais de uma parte e as duas últimas são iguais,
                        # significa duplicação, então usar apenas a última
                        if len(uf_parts) >= 2 and uf_parts[-1] == uf_parts[-2]:
                            uf_extraida = uf_parts[-1].upper()
                    break

        # Se conseguiu extrair cidade e UF, tentar buscar novamente
        if cidade_base and uf_extraida:
            cidade_key_base = cidade_base.lower().strip()
            uf_mapeada = municipios_map.get(cidade_key_base)

            if uf_mapeada:
                # Verificar se a UF extraída corresponde à mapeada
                if uf_extraida.upper() == uf_mapeada.upper():
                    # Criar nova cidade com o NOME LIMPO (sem estado)
                    cidade = cidade_repo.create_cidade(cidade_base, uf_mapeada)
                    logging.info(f"✅ Cidade criada: {cidade_base} - {uf_mapeada}")
                    return cidade
                else:
                    logging.warning(
                        f"❌ UF conflitante para cidade {cidade_nome}: extraída='{uf_extraida}', mapeada='{uf_mapeada}'"
                    )

        logging.warning(f"❌ UF não encontrada para cidade: {cidade_nome}")
        return None


def seed_speakers_from_csv(verbose: bool = False) -> bool:
    """
    Carrega dados de palestrantes do arquivo CSV.

    Args:
        verbose: Se deve mostrar informações detalhadas

    Returns:
        bool: True se bem-sucedido
    """
    speakers_file = project_root / "utils" / "2025_data_palestrantes.csv"

    if not speakers_file.exists():
        logging.error(f"❌ Arquivo de palestrantes não encontrado: {speakers_file}")
        return False

    try:
        # Carregar dados de municípios
        municipios_map = load_municipios_data()
        if not municipios_map:
            logging.error("❌ Não foi possível carregar dados de municípios")
            return False

        # Inicializar serviços
        crypto_service = ServicoCriptografia()

        with db_manager.get_db_session() as session:
            from app.db import (
                get_evento_repository,
                get_participante_repository,
                get_funcao_repository,
            )

            evento_repo = get_evento_repository(session)
            participante_repo = get_participante_repository(session)
            funcao_repo = get_funcao_repository(session)

            # Buscar evento 2025
            evento_2025 = evento_repo.get_by_ano(2025)
            if not evento_2025:
                logging.error("❌ Evento 2025 não encontrado no banco de dados")
                return False

            # Datas válidas do evento
            datas_validas = set(evento_2025.datas_evento)
            logging.info(f"📅 Datas válidas do evento 2025: {sorted(datas_validas)}")

            # Buscar função "Palestrante"
            funcao_palestrante = funcao_repo.get_by_name("Palestrante")
            if not funcao_palestrante:
                logging.error(
                    "❌ Função 'Palestrante' não encontrada no banco de dados"
                )
                return False

            # Processar arquivo CSV
            palestrantes_processados = 0
            palestrantes_criados = 0
            erros = 0

            with open(speakers_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(
                    reader, start=2
                ):  # Começar em 2 (linha do header + 1)
                    try:
                        # Extrair dados da linha
                        nome = row.get("Nome", "").strip()
                        funcao_csv = row.get("Função", "").strip()
                        titulo = row.get("Título", "").strip()
                        cidade_nome = row.get("Cidade", "").strip()
                        data_str = row.get("Data", "").strip()
                        email = row.get("E-mail", "").strip()

                        # Validações básicas
                        if not all(
                            [nome, funcao_csv, titulo, cidade_nome, data_str, email]
                        ):
                            logging.warning(
                                f"⚠️ Linha {row_num}: Dados incompletos, pulando..."
                            )
                            erros += 1
                            continue

                        # Verificar se é palestrante ou apresentador
                        funcao_lower = funcao_csv.lower()
                        if funcao_lower not in [
                            "palestrante",
                            "palestrantes",
                            "apresentador",
                            "apresentadora",
                        ]:
                            if verbose:
                                logging.info(
                                    f"ℹ️ Linha {row_num}: Função '{funcao_csv}' não é palestrante ou apresentador, pulando..."
                                )
                            continue

                        # Parsear data
                        data_iso = parse_portuguese_date(data_str)
                        if not data_iso:
                            logging.warning(
                                f"⚠️ Linha {row_num}: Data inválida '{data_str}', pulando..."
                            )
                            erros += 1
                            continue

                        # Verificar se data é válida para o evento
                        if data_iso not in datas_validas:
                            logging.warning(
                                f"⚠️ Linha {row_num}: Data '{data_iso}' não é válida para o evento 2025, pulando..."
                            )
                            erros += 1
                            continue

                        # Buscar cidade
                        cidade = get_cidade_from_name(
                            cidade_nome, municipios_map, session
                        )
                        if not cidade:
                            logging.warning(
                                f"⚠️ Linha {row_num}: Cidade '{cidade_nome}' não encontrada, pulando..."
                            )
                            erros += 1
                            continue

                        # Verificar se participante já existe (pelo hash do email)
                        email_hash = crypto_service.gerar_hash_email(email)
                        participante_existente = participante_repo.get_by_email_hash(
                            email_hash, evento_2025.id
                        )

                        if participante_existente:
                            if verbose:
                                logging.info(
                                    f"ℹ️ Linha {row_num}: Palestrante '{nome}' já existe, pulando..."
                                )
                            palestrantes_processados += 1
                            continue

                        # Criptografar dados sensíveis
                        nome_criptografado = crypto_service.criptografar_nome(nome)
                        email_criptografado = crypto_service.criptografar_email(email)

                        # Calcular carga horária (assumindo 1 hora por palestra)
                        carga_horaria = 1

                        # Criar participante
                        participante = participante_repo.create_participante(
                            nome_completo_encrypted=nome_criptografado,
                            email_encrypted=email_criptografado,
                            email_hash=email_hash,
                            titulo_apresentacao=titulo,
                            evento_id=evento_2025.id,
                            cidade_id=cidade.id,
                            funcao_id=funcao_palestrante.id,
                            datas_participacao=data_iso,  # Apenas uma data
                            carga_horaria_calculada=carga_horaria,
                            validado=False,  # Palestrantes precisam ser validados manualmente
                            data_inscricao=datetime.now().isoformat(),
                        )

                        palestrantes_criados += 1
                        palestrantes_processados += 1

                        if verbose:
                            logging.info(
                                f"✅ Linha {row_num}: Palestrante '{nome}' criado com ID {participante.id}"
                            )

                    except Exception as e:
                        logging.error(f"❌ Erro na linha {row_num}: {e}")
                        erros += 1
                        continue

            logging.info("📊 Resumo do processamento:")
            logging.info(f"  Palestrantes processados: {palestrantes_processados}")
            logging.info(f"  Palestrantes criados: {palestrantes_criados}")
            logging.info(f"  Erros: {erros}")

            return True

    except Exception as e:
        logging.error(f"❌ Erro geral ao processar arquivo de palestrantes: {e}")
        return False


def seed_database(
    force: bool = False, seed_speakers: bool = False, verbose: bool = False
) -> bool:
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

        # Seed speakers if requested
        if seed_speakers:
            print("\n🎤 Carregando dados de palestrantes...")
            if not seed_speakers_from_csv(verbose):
                print("❌ Falha ao carregar dados de palestrantes")
                return False
            print("✅ Dados de palestrantes carregados com sucesso!")

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
    parser.add_argument(
        "--seed-speakers",
        action="store_true",
        help="Carrega dados de palestrantes do arquivo CSV",
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
    success = seed_database(
        force=args.force, seed_speakers=args.seed_speakers, verbose=args.verbose
    )

    if success:
        print("\n🎉 Processo concluído com sucesso!")
        if args.seed_speakers:
            print(
                "\n💡 Palestrantes foram carregados. Eles precisam ser validados manualmente no sistema."
            )
        print("\n💡 Dicas:")
        print("  - Execute 'python test_system.py' para validar o sistema")
        print("  - Use 'streamlit run Home.py' para iniciar a aplicação")
        sys.exit(0)
    else:
        print("\n💥 Processo falhou!")
        sys.exit(1)


if __name__ == "__main__":
    main()
