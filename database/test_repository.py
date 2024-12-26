from .connection import get_connection


def insert_test_case(
    code_id: int, input_val: str, expected_output: str, description: str
):
    """テストケースをデータベースに挿入します。"""
    conn = get_connection()
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