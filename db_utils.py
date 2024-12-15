import sqlite3
import json

DATABASE_NAME = "code_comparison.db"


def create_database():
    """
    SQLiteデータベースを作成し、テーブルを定義します。

    この関数は、'code_comparison.db'という名前のデータベースファイルを作成します（既に存在する場合は接続します）。
    そして、'codes'と'test_cases'という2つのテーブルを作成します。

    'codes'テーブルは以下のカラムを持ちます：
    - id: 整数型の主キーで、自動的に増加します。
    - code: テキスト型で、コードスニペットを格納します。一意である必要があります。
    - language: テキスト型で、コードのプログラミング言語を格納します。
    - embedding: テキスト型で、コードの埋め込みベクトルをJSON形式で格納します。
    - description: テキスト型で、コードの説明を格納します。

    'test_cases'テーブルは以下のカラムを持ちます：
    - id: 整数型の主キーで、自動的に増加します。
    - code_id: 整数型で、'codes'テーブルの'id'を参照する外部キーです。
    - input: テキスト型で、テストケースの入力を格納します。
    - expected_output: テキスト型で、テストケースの期待される出力を格納します。
    - description: テキスト型で、テストケースの説明を格納します。

    テーブルが既に存在する場合、この関数は新しいテーブルを作成しません。
    """
    conn = sqlite3.connect(DATABASE_NAME)
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


def insert_code_data(code: str, language: str, description: str):
    """
    コードデータをデータベースに挿入します。

    この関数は、与えられたコード、言語、説明を'codes'テーブルに挿入します。
    コードが既に存在する場合は、既存のコードのIDを返します。
    挿入が成功した場合は、新しいコードのIDを返します。
    エラーが発生した場合は、エラーメッセージを表示し、Noneを返します。

    Args:
        code: 挿入するコードスニペット。
        language: コードのプログラミング言語。
        description: コードの説明。

    Returns:
        挿入されたコードのID（成功した場合）、既存のコードのID（重複の場合）、またはNone（エラーの場合）。
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        # 既存のコードをチェック
        cursor.execute("SELECT id FROM codes WHERE code = ?", (code,))
        existing_code = cursor.fetchone()
        if existing_code:
            print(f"Code already exists with ID: {existing_code[0]}")
            conn.close()
            return existing_code[0]  # 既存のコードIDを返す

        # 新しいコードを挿入
        cursor.execute(
            """
            INSERT INTO codes (code, language, embedding, description)
            VALUES (?, ?, ?, ?)
        """,
            (code, language, None, description),
        )
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
    """
    コードの埋め込みベクトルを更新します。

    この関数は、指定されたコードIDに対応する'codes'テーブルのレコードの埋め込みベクトルを更新します。
    埋め込みベクトルは、リストとして渡され、JSON形式の文字列に変換されてデータベースに保存されます。
    更新が成功した場合はTrueを、エラーが発生した場合はFalseを返します。

    Args:
        code_id: 更新するコードのID。
        embedding: 更新する埋め込みベクトル（リスト形式）。

    Returns:
        True（成功した場合）、False（失敗した場合）。
    """
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
    """
    テストケースデータをデータベースに挿入します。

    この関数は、指定されたコードID、入力値、期待される出力、説明を'test_cases'テーブルに挿入します。
    挿入が成功した場合はTrueを、エラーが発生した場合はFalseを返します。

    Args:
        code_id: テストケースが関連付けられるコードのID。
        input_val: テストケースの入力値。
        expected_output: テストケースの期待される出力。
        description: テストケースの説明。

    Returns:
        True（成功した場合）、False（失敗した場合）。
    """
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
    """
    データベースからコードIDと埋め込みベクトルを取得します。

    この関数は、'codes'テーブルから、埋め込みベクトルがNULLでないレコードのコードIDと埋め込みベクトルを取得します。
    埋め込みベクトルはJSON形式の文字列としてデータベースに保存されているため、この関数ではPythonのリスト形式に変換して返します。
    結果は、(コードID, 埋め込みベクトル)のタプルのリストとして返されます。

    Returns:
        (コードID, 埋め込みベクトル)のタプルのリスト。
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # まず全てのコードデータを取得して確認
    cursor.execute("SELECT id, code, embedding FROM codes")
    all_codes = cursor.fetchall()
    print("\nデータベース内の全コード:")
    for code_id, code, embedding in all_codes:
        print(
            f"ID: {code_id}, Code: {code[:30]}..., Embedding: {'あり' if embedding else 'なし'}"
        )

    # embeddingがnullでないデータのみ取得
    cursor.execute("SELECT id, embedding FROM codes WHERE embedding IS NOT NULL")
    code_embeddings = []
    for code_id, embedding_json in cursor:
        try:
            embedding = json.loads(embedding_json)
            code_embeddings.append((code_id, embedding))
            print(f"Loaded embedding for code ID: {code_id}")
        except json.JSONDecodeError as e:
            print(f"Error decoding embedding for code ID {code_id}: {e}")
            continue

    print(f"\n有効なembeddingの数: {len(code_embeddings)}")
    conn.close()
    return code_embeddings


def get_test_cases(code_id: int):
    """
    指定されたコードIDに関連付けられたテストケースを取得します。

    この関数は、'test_cases'テーブルから、指定されたコードIDに関連付けられたテストケースの入力と期待される出力を取得します。
    結果は、(入力, 期待される出力)のタプルのリストとして返されます。

    Args:
        code_id: テストケースを取得するコードのID。

    Returns:
        (入力, 期待される出力)のタプルのリスト。
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT input, expected_output FROM test_cases WHERE code_id = ?", (code_id,)
    )
    test_cases = cursor.fetchall()
    conn.close()
    return test_cases
