#!/usr/bin/env python3
"""
Migration script to add hash_validacao column to participantes table.

This script safely adds the hash_validacao column if it doesn't exist.
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core import settings


def add_hash_validacao_column():
    """Add hash_validacao column to participantes table if it doesn't exist."""

    db_path = settings.database_url.replace("sqlite:///", "")

    print(f"🔍 Conectando ao banco de dados: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(participantes)")
        columns = [row[1] for row in cursor.fetchall()]

        if "hash_validacao" in columns:
            print("✅ Coluna hash_validacao já existe na tabela participantes")
            return

        # Add the column
        print("➕ Adicionando coluna hash_validacao...")
        cursor.execute(
            """
            ALTER TABLE participantes
            ADD COLUMN hash_validacao TEXT
        """
        )

        # Create index
        print("📑 Criando índice para hash_validacao...")
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_participantes_hash_validacao
            ON participantes(hash_validacao)
        """
        )

        conn.commit()
        print("✅ Coluna hash_validacao adicionada com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao adicionar coluna: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    add_hash_validacao_column()
