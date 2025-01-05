import json
from typing import List, Optional, Tuple
from .context import db_context


def insert_code(code: str) -> Optional[int]:
    """コードをデータベースに挿入します。"""
    try:
        with db_context() as (_, cursor):
            # 既存のコードをチェック
            cursor.execute("SELECT id FROM codes WHERE code = ?", (code,))
            existing_code = cursor.fetchone()
            if existing_code:
                print(f"Code already exists with ID: {existing_code[0]}")
                return existing_code[0]

            # 新しいコードを挿入
            cursor.execute(
                """
                INSERT INTO codes (code, embedding)
                VALUES (?, ?)
            """,
                (code, None),
            )
            return cursor.lastrowid
    except Exception as e:
        print(f"Error inserting code data: {e}")
        return None


def update_embedding(code_id: int, embedding: list) -> bool:
    """コードの埋め込みベクトルを更新します。"""
    try:
        with db_context() as (_, cursor):
            embedding_json = json.dumps(embedding)
            cursor.execute(
                "UPDATE codes SET embedding = ? WHERE id = ?",
                (embedding_json, code_id),
            )
            return True
    except Exception as e:
        print(f"Error updating code embedding: {e}")
        return False


def get_embeddings() -> List[Tuple[int, list]]:
    """全てのコード埋め込みベクトルを取得します。"""
    try:
        with db_context() as (_, cursor):
            cursor.execute("SELECT id, embedding FROM codes WHERE embedding IS NOT NULL")
            code_embeddings = []
            for code_id, embedding_json in cursor:
                try:
                    embedding = json.loads(embedding_json)
                    code_embeddings.append((code_id, embedding))
                except json.JSONDecodeError as e:
                    print(f"Error decoding embedding for code ID {code_id}: {e}")
                    continue
            return code_embeddings
    except Exception as e:
        print(f"Error getting embeddings: {e}")
        return []


def get_code_by_id(code_id: int) -> Optional[str]:
    """指定されたIDのコードを取得します。"""
    try:
        with db_context() as (_, cursor):
            cursor.execute("SELECT code FROM codes WHERE id = ?", (code_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except Exception as e:
        print(f"Error getting code by ID: {e}")
        return None
