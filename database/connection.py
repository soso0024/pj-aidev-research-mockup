import sqlite3

DATABASE_NAME = "code_comparison.db"


def get_connection():
    """データベース接続を取得します。"""
    return sqlite3.connect(DATABASE_NAME)


def create_database():
    """データベースとテーブルを初期化します。"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
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
