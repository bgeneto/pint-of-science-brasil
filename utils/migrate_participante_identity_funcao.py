#!/usr/bin/env python3
"""
Migração: usar email_hash + evento_id + funcao_id como identidade de inscrição.

Esta migração é idempotente para SQLite. Ela:
- preenche email_hash ausente a partir do email criptografado;
- bloqueia a migração se já existirem duplicidades de email/evento/função;
- remove restrições legadas de unicidade global em email_hash;
- garante índices para email_hash, hash_validacao e email/evento/função.
"""

from __future__ import annotations

import hashlib
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable

from cryptography.fernet import Fernet

from app.core import settings


EMAIL_INDEX_NAME = "ix_participantes_email_hash"
HASH_VALIDACAO_INDEX_NAME = "ix_participantes_hash_validacao"
IDENTITY_INDEX_NAME = "uq_participantes_email_evento_funcao"


def _database_path(database_path: str | Path | None = None) -> Path:
    if database_path is not None:
        return Path(database_path)
    return settings.db_path


def _generate_email_hash(email: str) -> str:
    return hashlib.sha256(email.lower().strip().encode("utf-8")).hexdigest()


def _index_rows(cursor: sqlite3.Cursor) -> list[dict]:
    rows = cursor.execute("PRAGMA index_list('participantes')").fetchall()
    return [
        {
            "seq": row[0],
            "name": row[1],
            "unique": bool(row[2]),
            "origin": row[3],
            "partial": bool(row[4]),
        }
        for row in rows
    ]


def _index_columns(cursor: sqlite3.Cursor, index_name: str) -> list[str]:
    rows = cursor.execute(f"PRAGMA index_info('{index_name}')").fetchall()
    return [row[2] for row in rows]


def _has_unique_index(
    cursor: sqlite3.Cursor, columns: Iterable[str], *, exact_order: bool = True
) -> bool:
    expected = list(columns)
    for index in _index_rows(cursor):
        if not index["unique"]:
            continue
        actual = _index_columns(cursor, index["name"])
        if exact_order and actual == expected:
            return True
        if not exact_order and set(actual) == set(expected):
            return True
    return False


def _email_hash_is_not_null(cursor: sqlite3.Cursor) -> bool:
    rows = cursor.execute("PRAGMA table_info('participantes')").fetchall()
    for row in rows:
        if row[1] == "email_hash":
            return bool(row[3])
    raise RuntimeError("Coluna participantes.email_hash não encontrada.")


def _has_auto_unique_email_hash(cursor: sqlite3.Cursor) -> bool:
    for index in _index_rows(cursor):
        if not index["unique"] or index["origin"] != "u":
            continue
        if _index_columns(cursor, index["name"]) == ["email_hash"]:
            return True
    return False


def _drop_explicit_unique_email_hash_indexes(cursor: sqlite3.Cursor) -> int:
    dropped = 0
    for index in _index_rows(cursor):
        if (
            index["unique"]
            and index["origin"] == "c"
            and _index_columns(cursor, index["name"]) == ["email_hash"]
        ):
            cursor.execute(f'DROP INDEX "{index["name"]}"')
            dropped += 1
    return dropped


def _backfill_email_hashes(conn: sqlite3.Connection) -> int:
    fernet = Fernet(settings.encryption_key.encode())
    cursor = conn.cursor()
    rows = cursor.execute(
        """
        SELECT id, email_encrypted
        FROM participantes
        WHERE email_hash IS NULL OR TRIM(email_hash) = ''
        """
    ).fetchall()

    for participante_id, email_encrypted in rows:
        email = fernet.decrypt(email_encrypted).decode("utf-8")
        cursor.execute(
            "UPDATE participantes SET email_hash = ? WHERE id = ?",
            (_generate_email_hash(email), participante_id),
        )

    return len(rows)


def _duplicate_identity_groups(cursor: sqlite3.Cursor) -> list[tuple]:
    return cursor.execute(
        """
        SELECT email_hash, evento_id, funcao_id, COUNT(*) AS total, GROUP_CONCAT(id)
        FROM participantes
        GROUP BY email_hash, evento_id, funcao_id
        HAVING COUNT(*) > 1
        """
    ).fetchall()


def _recreate_participantes_table(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    backup_name = f"participantes_backup_identity_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    cursor.execute("PRAGMA foreign_keys=OFF")
    cursor.execute(f'ALTER TABLE participantes RENAME TO "{backup_name}"')
    cursor.execute(
        """
        CREATE TABLE participantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo_encrypted BLOB NOT NULL,
            email_encrypted BLOB NOT NULL,
            email_hash VARCHAR(64) NOT NULL,
            titulo_apresentacao TEXT,
            evento_id INTEGER NOT NULL,
            cidade_id INTEGER NOT NULL,
            funcao_id INTEGER NOT NULL,
            datas_participacao TEXT NOT NULL,
            validado BOOLEAN NOT NULL,
            hash_validacao VARCHAR(64),
            data_inscricao TEXT NOT NULL,
            FOREIGN KEY(evento_id) REFERENCES eventos (id),
            FOREIGN KEY(cidade_id) REFERENCES cidades (id),
            FOREIGN KEY(funcao_id) REFERENCES funcoes (id)
        )
        """
    )

    columns = [
        "id",
        "nome_completo_encrypted",
        "email_encrypted",
        "email_hash",
        "titulo_apresentacao",
        "evento_id",
        "cidade_id",
        "funcao_id",
        "datas_participacao",
        "validado",
        "hash_validacao",
        "data_inscricao",
    ]
    column_list = ", ".join(columns)
    cursor.execute(
        f"""
        INSERT INTO participantes ({column_list})
        SELECT {column_list}
        FROM "{backup_name}"
        """
    )
    cursor.execute(f'DROP TABLE "{backup_name}"')
    cursor.execute("PRAGMA foreign_keys=ON")


def _ensure_indexes(cursor: sqlite3.Cursor) -> None:
    cursor.execute(
        f"CREATE INDEX IF NOT EXISTS {EMAIL_INDEX_NAME} ON participantes(email_hash)"
    )

    if not _has_unique_index(cursor, ["hash_validacao"]):
        cursor.execute(
            f"CREATE UNIQUE INDEX IF NOT EXISTS {HASH_VALIDACAO_INDEX_NAME} "
            "ON participantes(hash_validacao)"
        )

    if not _has_unique_index(cursor, ["email_hash", "evento_id", "funcao_id"]):
        cursor.execute(
            f"CREATE UNIQUE INDEX IF NOT EXISTS {IDENTITY_INDEX_NAME} "
            "ON participantes(email_hash, evento_id, funcao_id)"
        )


def migrate_participante_identity_funcao(
    database_path: str | Path | None = None,
) -> dict[str, int | bool]:
    db_path = _database_path(database_path)
    if not db_path.exists():
        raise FileNotFoundError(f"Banco de dados não encontrado: {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.execute("BEGIN")

        backfilled = _backfill_email_hashes(conn)
        duplicates = _duplicate_identity_groups(cursor)
        if duplicates:
            detalhes = "; ".join(
                f"email_hash={row[0]} evento_id={row[1]} funcao_id={row[2]} ids={row[4]}"
                for row in duplicates
            )
            raise RuntimeError(
                "Existem inscrições duplicadas para email/evento/função. "
                f"Resolva manualmente antes de migrar: {detalhes}"
            )

        dropped_unique_email_indexes = _drop_explicit_unique_email_hash_indexes(cursor)
        needs_rebuild = (
            not _email_hash_is_not_null(cursor) or _has_auto_unique_email_hash(cursor)
        )

        if needs_rebuild:
            _recreate_participantes_table(conn)
            cursor = conn.cursor()

        _ensure_indexes(cursor)
        conn.commit()

        return {
            "backfilled_email_hashes": backfilled,
            "dropped_unique_email_indexes": dropped_unique_email_indexes,
            "rebuilt_table": needs_rebuild,
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        try:
            conn.execute("PRAGMA foreign_keys=ON")
        except sqlite3.Error:
            pass
        conn.close()


def main() -> int:
    database_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    try:
        result = migrate_participante_identity_funcao(database_path)
    except Exception as exc:
        print(f"❌ Migração falhou: {exc}")
        return 1

    print("✅ Migração concluída com sucesso.")
    print(f"   email_hash preenchidos: {result['backfilled_email_hashes']}")
    print(f"   índices únicos legados removidos: {result['dropped_unique_email_indexes']}")
    print(f"   tabela recriada: {'sim' if result['rebuilt_table'] else 'não'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
