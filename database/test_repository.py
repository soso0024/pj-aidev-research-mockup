from .connection import get_connection


def insert_test_case(
    code_id: int, input_val: str, expected_output: str, description: str
):
    """テストケースをデータベースに挿入します。
    
    同じコードに対して同じ入力と期待される出力の組み合わせが既に存在する場合は、
    重複を避けるために挿入を行いません。

    Args:
        code_id: テストケースが関連付けられるコードのID
        input_val: テストケースの入力値
        expected_output: テストケースの期待される出力
        description: テストケースの説明

    Returns:
        True: 挿入が成功した場合、または同じテストケースが既に存在する場合
        False: エラーが発生した場合
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 既存のテストケースをチェック
        cursor.execute(
            """
            SELECT id FROM test_cases 
            WHERE code_id = ? AND input = ? AND expected_output = ?
            """,
            (code_id, input_val, expected_output),
        )
        existing_test = cursor.fetchone()
        if existing_test:
            print(f"Test case already exists with ID: {existing_test[0]}")
            conn.close()
            return True

        # 新しいテストケースを挿入
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
    except Exception as e:
        print(f"Error inserting test case data: {e}")
        conn.rollback()
        conn.close()
        return False


def get_test_cases(code_id: int):
    """指定されたコードIDのテストケースを取得します。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT input, expected_output FROM test_cases WHERE code_id = ?", (code_id,)
    )
    test_cases = cursor.fetchall()
    conn.close()
    return test_cases