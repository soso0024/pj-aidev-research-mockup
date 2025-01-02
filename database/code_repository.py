import json
from .connection import get_connection


def insert_code(code: str):
    """コードをデータベースに挿入します。"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 既存のコードをチェック
        cursor.execute("SELECT id FROM codes WHERE code = ?", (code,))
        existing_code = cursor.fetchone()
        if existing_code:
            print(f"Code already exists with ID: {existing_code[0]}")
            conn.close()
            return existing_code[0]

        # 新しいコードを挿入
        cursor.execute(
            """
            INSERT INTO codes (code, embedding)
            VALUES (?, ?)
        """,
            (code, None),
        )
        conn.commit()
        code_id = cursor.lastrowid
        conn.close()
        return code_id
    except Exception as e:
        print(f"Error inserting code data: {e}")
        conn.rollback()
        conn.close()
        return None


def update_embedding(code_id: int, embedding: list):
    """コードの埋め込みベクトルを更新します。"""
    conn = get_connection()
    cursor = conn.cursor()
    embedding_json = json.dumps(embedding)
    try:
        cursor.execute(
            "UPDATE codes SET embedding = ? WHERE id = ?",
            (embedding_json, code_id),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating code embedding: {e}")
        conn.rollback()
        conn.close()
        return False


def get_embeddings():
    """全てのコード埋め込みベクトルを取得します。"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, embedding FROM codes WHERE embedding IS NOT NULL")
    code_embeddings = []
    for code_id, embedding_json in cursor:
        try:
            embedding = json.loads(embedding_json)
            code_embeddings.append((code_id, embedding))
        except json.JSONDecodeError as e:
            print(f"Error decoding embedding for code ID {code_id}: {e}")
            continue

    conn.close()
    return code_embeddings
