from typing import List, Tuple, Optional
from .context import db_context


def insert_test_case(code_id: int, input_val: str, expected_output: str) -> bool:
    """テストケースをデータベースに挿入します。
    
    同じコードに対して同じ入力と期待される出力の組み合わせが既に存在する場合は、
    重複を避けるために挿入を行いません。

    Args:
        code_id: テストケースが関連付けられるコードのID
        input_val: テストケースの入力値
        expected_output: テストケースの期待される出力

    Returns:
        bool: 挿入が成功した場合、または同じテストケースが既に存在する場合はTrue
    """
    try:
        with db_context() as (_, cursor):
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
                return True

            # 新しいテストケースを挿入
            cursor.execute(
                """
                INSERT INTO test_cases (code_id, input, expected_output)
                VALUES (?, ?, ?)
                """,
                (code_id, input_val, expected_output),
            )
            return True
    except Exception as e:
        print(f"Error inserting test case data: {e}")
        return False


def get_test_cases(code_id: int) -> List[Tuple[str, str]]:
    """指定されたコードIDのテストケースを取得します。

    Args:
        code_id: テストケースを取得するコードのID

    Returns:
        List[Tuple[str, str]]: (入力, 期待される出力)のタプルのリスト
    """
    try:
        with db_context() as (_, cursor):
            cursor.execute(
                "SELECT input, expected_output FROM test_cases WHERE code_id = ?",
                (code_id,)
            )
            return cursor.fetchall()
    except Exception as e:
        print(f"Error getting test cases: {e}")
        return []


def get_test_case_count(code_id: int) -> int:
    """指定されたコードIDのテストケース数を取得します。

    Args:
        code_id: テストケース数を取得するコードのID

    Returns:
        int: テストケースの数
    """
    try:
        with db_context() as (_, cursor):
            cursor.execute(
                "SELECT COUNT(*) FROM test_cases WHERE code_id = ?",
                (code_id,)
            )
            return cursor.fetchone()[0]
    except Exception as e:
        print(f"Error getting test case count: {e}")
        return 0
