#!/usr/bin/env python3
"""
Migration script to drop the 'carga_horaria_calculada' column from participantes table.

This column is no longer needed since carga horária is calculated on-the-fly
from the JSON configuration file.
"""

import sqlite3
import os
from pathlib import Path


def migrate_drop_carga_horaria_column():
    """Remove the carga_horaria_calculada column from participantes table."""

    # Database path
    db_path = Path("data/pint_of_science.db")

    if not db_path.exists():
        print("❌ Database file not found!")
        return False

    try:
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        print("🔍 Checking current table structure...")

        # Check if column exists
        cursor.execute("PRAGMA table_info(participantes)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if "carga_horaria_calculada" not in column_names:
            print(
                "ℹ️ Column 'carga_horaria_calculada' not found in participantes table. Migration may already be applied."
            )
            conn.close()
            return True

        print("📊 Current columns:", column_names)

        # Create new table without the column
        print(
            "🔄 Creating new table structure without carga_horaria_calculada column..."
        )

        # Get all columns except carga_horaria_calculada
        columns_to_keep = [
            col for col in column_names if col != "carga_horaria_calculada"
        ]
        columns_str = ", ".join(columns_to_keep)

        # Create backup table
        cursor.execute("ALTER TABLE participantes RENAME TO participantes_backup")

        # Create new table without the column
        create_table_sql = f"""
        CREATE TABLE participantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo_encrypted BLOB NOT NULL,
            email_encrypted BLOB NOT NULL,
            email_hash TEXT NOT NULL UNIQUE,
            titulo_apresentacao TEXT,
            evento_id INTEGER NOT NULL,
            cidade_id INTEGER NOT NULL,
            funcao_id INTEGER NOT NULL,
            datas_participacao TEXT NOT NULL,
            validado BOOLEAN NOT NULL DEFAULT 0,
            data_inscricao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            hash_validacao TEXT,
            FOREIGN KEY (evento_id) REFERENCES eventos (id),
            FOREIGN KEY (cidade_id) REFERENCES cidades (id),
            FOREIGN KEY (funcao_id) REFERENCES funcoes (id)
        )
        """

        cursor.execute(create_table_sql)

        # Copy data from backup table
        print("📋 Copying data to new table structure...")
        cursor.execute(
            f"""
            INSERT INTO participantes ({columns_str})
            SELECT {columns_str} FROM participantes_backup
        """
        )

        # Drop backup table
        cursor.execute("DROP TABLE participantes_backup")

        # Create indexes
        print("🔗 Recreating indexes...")
        cursor.execute(
            "CREATE INDEX idx_participantes_email_hash ON participantes(email_hash)"
        )
        cursor.execute(
            "CREATE INDEX idx_participantes_evento_id ON participantes(evento_id)"
        )
        cursor.execute(
            "CREATE INDEX idx_participantes_cidade_id ON participantes(cidade_id)"
        )
        cursor.execute(
            "CREATE INDEX idx_participantes_funcao_id ON participantes(funcao_id)"
        )
        cursor.execute(
            "CREATE INDEX idx_participantes_validado ON participantes(validado)"
        )

        # Commit changes
        conn.commit()

        print("✅ Migration completed successfully!")
        print(
            "🗑️ Column 'carga_horaria_calculada' has been removed from participantes table"
        )

        # Verify the change
        cursor.execute("PRAGMA table_info(participantes)")
        new_columns = cursor.fetchall()
        new_column_names = [col[1] for col in new_columns]
        print("📊 New columns:", new_column_names)

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if "conn" in locals():
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    print("🚀 Starting migration: Drop carga_horaria_calculada column")
    print("=" * 60)

    success = migrate_drop_carga_horaria_column()

    if success:
        print("\n✅ Migration completed successfully!")
        print("ℹ️ You can now remove carga_horaria_calculada from your models and code.")
    else:
        print("\n❌ Migration failed!")
        exit(1)
