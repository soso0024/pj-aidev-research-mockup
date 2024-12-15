import sqlite3
import json

DATABASE_NAME = "code_comparison.db"


def create_database():
    """SQLiteデータベースを作成し、テーブルを定義"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            language TEXT NOT NULL,
            embedding TEXT,
            description TEXT
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS test_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_id INTEGER,
            input TEXT NOT NULL,
            expected_output TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (code_id) REFERENCES codes(id)
        )
    """
    )

    conn.commit()
    conn.close()


def insert_code_data(code: str, language: str, description: str):
    """コードデータをDBに挿入"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO codes (code, language, embedding, description)
            VALUES (?, ?, ?, ?)
        """,
            (code, language, None, description),
        )  # 埋め込みは後で更新するためNone
        conn.commit()
        code_id = cursor.lastrowid
        conn.close()
        return code_id
    except sqlite3.Error as e:
        print(f"Error inserting code data: {e}")
        conn.rollback()
        conn.close()
        return None


def update_code_embedding(code_id: int, embedding: list):
    """コードの埋め込みベクトルを更新"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    embedding_json = json.dumps(embedding)
    try:
        cursor.execute(
            """
            UPDATE codes SET embedding = ? WHERE id = ?
        """,
            (embedding_json, code_id),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Error updating code embedding: {e}")
        conn.rollback()
        conn.close()
        return False


def insert_test_case(
    code_id: int, input_val: str, expected_output: str, description: str
):
    """テストケースデータをDBに挿入"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO test_cases (code_id, input, expected_output, description)
            VALUES (?, ?, ?, ?)
        """,
            (code_id, input_val, expected_output, description),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Error inserting test case data: {e}")
        conn.rollback()
        conn.close()
        return False


def get_code_embeddings():
    """DBからコードIDと埋め込みベクトルを取得"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, embedding FROM codes WHERE embedding IS NOT NULL"
    )  # embeddingがnullでないデータのみ取得
    code_embeddings = []
    for code_id, embedding_json in cursor:
        embedding = json.loads(embedding_json)
        code_embeddings.append((code_id, embedding))
    conn.close()
    return code_embeddings


def get_test_cases(code_id: int):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT input, expected_output FROM test_cases WHERE code_id = ?", (code_id,)
    )
    test_cases = cursor.fetchall()
    conn.close()
    return test_cases
