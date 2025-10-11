#!/usr/bin/env python3
"""
Script para regenerar todos os hashes de validação de certificados.

Use este script quando:
- A CERTIFICATE_SECRET_KEY foi alterada
- Houve mudança na lógica de geração de hash
- Deseja recalcular todos os hashes existentes

ATENÇÃO: Isso invalidará todos os certificados PDF já emitidos!
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import db_manager
from app.models import Participante
from app.services import servico_criptografia


def regenerar_todos_hashes(confirmar: bool = False):
    """
    Regenera os hashes de validação para todos os participantes.

    Args:
        confirmar: Se True, executa a regeneração. Se False, apenas simula.
    """

    print("🔄 Script de Regeneração de Hashes de Validação")
    print("=" * 60)

    if not confirmar:
        print("⚠️  MODO SIMULAÇÃO - Nenhuma alteração será feita no banco")
        print()

    try:
        with db_manager.get_db_session() as session:
            # Buscar todos os participantes
            participantes = session.query(Participante).all()

            print(f"📊 Total de participantes encontrados: {len(participantes)}")
            print()

            if not participantes:
                print("ℹ️  Nenhum participante encontrado no banco de dados.")
                return

            # Contar quantos já têm hash
            com_hash = sum(1 for p in participantes if p.hash_validacao)
            sem_hash = len(participantes) - com_hash

            print(f"✅ Participantes com hash: {com_hash}")
            print(f"❌ Participantes sem hash: {sem_hash}")
            print()

            if not confirmar:
                print("Para executar a regeneração, execute:")
                print(f"  python {sys.argv[0]} --confirm")
                print()
                print(
                    "⚠️  ATENÇÃO: Isso invalidará todos os certificados PDF já emitidos!"
                )
                return

            # Confirmar com o usuário
            print("⚠️  ATENÇÃO!")
            print("Esta ação irá:")
            print("  1. Regenerar todos os hashes de validação")
            print("  2. INVALIDAR todos os certificados PDF já emitidos")
            print("  3. Requerer nova geração de certificados para todos")
            print()

            resposta = input(
                "Tem certeza que deseja continuar? Digite 'SIM' para confirmar: "
            )

            if resposta.strip().upper() != "SIM":
                print()
                print("❌ Operação cancelada pelo usuário.")
                return

            print()
            print("🔄 Iniciando regeneração de hashes...")
            print()

            sucesso = 0
            erros = 0

            for i, participante in enumerate(participantes, 1):
                try:
                    # Descriptografar dados
                    nome = servico_criptografia.descriptografar(
                        participante.nome_completo_encrypted
                    )
                    email = servico_criptografia.descriptografar(
                        participante.email_encrypted
                    )

                    # Gerar novo hash
                    novo_hash = servico_criptografia.gerar_hash_validacao_certificado(
                        participante.id, participante.evento_id, email, nome
                    )

                    # Verificar se mudou
                    hash_anterior = participante.hash_validacao
                    mudou = hash_anterior != novo_hash

                    # Atualizar no banco
                    participante.hash_validacao = novo_hash

                    status = "🔄 ATUALIZADO" if mudou else "✓ Mantido"
                    print(
                        f"[{i:3d}/{len(participantes)}] {status} - ID {participante.id}: {nome[:40]}"
                    )

                    sucesso += 1

                except Exception as e:
                    print(
                        f"[{i:3d}/{len(participantes)}] ❌ ERRO - ID {participante.id}: {str(e)}"
                    )
                    erros += 1

            # Commit é feito automaticamente pelo context manager

            print()
            print("=" * 60)
            print("📊 Resultado da Regeneração:")
            print(f"  ✅ Sucesso: {sucesso}")
            print(f"  ❌ Erros: {erros}")
            print(f"  📁 Total processado: {len(participantes)}")
            print()

            if erros == 0:
                print("🎉 Todos os hashes foram regenerados com sucesso!")
            else:
                print(f"⚠️  {erros} erro(s) encontrado(s). Verifique os logs acima.")

    except Exception as e:
        print(f"❌ Erro fatal durante a regeneração: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Regenera hashes de validação de certificados"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirma a execução (sem esta flag, apenas simula)",
    )

    args = parser.parse_args()

    regenerar_todos_hashes(confirmar=args.confirm)
