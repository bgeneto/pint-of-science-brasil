#!/usr/bin/env python3
"""
Migração: Adicionar campo hash_validacao à tabela participantes

Este script adiciona a coluna hash_validacao e gera hashes para todos os
participantes validados existentes.

Executar uma vez após atualizar o código.
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import db_manager, get_participante_repository
from app.services import servico_criptografia
from app.models import Participante


def adicionar_coluna_hash_validacao():
    """Adiciona a coluna hash_validacao se não existir."""
    print("=" * 70)
    print("Migração: Adicionar campo hash_validacao")
    print("=" * 70)
    print()

    try:
        with db_manager.get_db_session() as session:
            # Verificar se a coluna já existe
            from sqlalchemy import inspect

            inspector = inspect(session.bind)
            columns = [c["name"] for c in inspector.get_columns("participantes")]

            if "hash_validacao" in columns:
                print("✅ Coluna 'hash_validacao' já existe no banco de dados.")
            else:
                print("➕ Adicionando coluna 'hash_validacao'...")
                # SQLite: ALTER TABLE é limitado, mas funciona para ADD COLUMN
                session.execute(
                    """
                    ALTER TABLE participantes
                    ADD COLUMN hash_validacao VARCHAR(64) UNIQUE
                """
                )
                session.commit()
                print("✅ Coluna 'hash_validacao' adicionada com sucesso!")

            print()
            print("=" * 70)
            print("Gerando hashes para participantes validados")
            print("=" * 70)
            print()

            # Buscar participantes validados sem hash
            participantes = (
                session.query(Participante)
                .filter(
                    Participante.validado == True, Participante.hash_validacao == None
                )
                .all()
            )

            if not participantes:
                print("✅ Todos os participantes validados já possuem hash.")
                print()
                return

            print(f"📋 Encontrados {len(participantes)} participantes sem hash.")
            print()

            sucesso = 0
            erros = 0

            for i, p in enumerate(participantes, 1):
                try:
                    # Descriptografar dados
                    email = servico_criptografia.descriptografar(p.email_encrypted)
                    nome = servico_criptografia.descriptografar(
                        p.nome_completo_encrypted
                    )

                    # Gerar hash
                    hash_val = servico_criptografia.gerar_hash_validacao_certificado(
                        p.id, p.evento_id, email, nome
                    )

                    # Atualizar no banco
                    p.hash_validacao = hash_val
                    sucesso += 1

                    print(
                        f"  [{i}/{len(participantes)}] ✅ Hash gerado para participante ID {p.id}"
                    )

                except Exception as e:
                    erros += 1
                    print(
                        f"  [{i}/{len(participantes)}] ❌ Erro no participante ID {p.id}: {e}"
                    )

            # Commit das alterações
            session.commit()

            print()
            print("=" * 70)
            print(f"✅ Migração concluída!")
            print(f"   - Sucessos: {sucesso}")
            print(f"   - Erros: {erros}")
            print("=" * 70)
            print()

            if erros > 0:
                print(
                    "⚠️  ATENÇÃO: Alguns participantes não receberam hash. Verifique os erros acima."
                )
            else:
                print(
                    "🎉 Todos os participantes validados agora possuem hash de validação!"
                )

    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    adicionar_coluna_hash_validacao()
