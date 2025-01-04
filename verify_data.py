from database.connection import get_connection


def verify_data():
    conn = get_connection()
    cursor = conn.cursor()

    # コードの数を確認
    cursor.execute("SELECT COUNT(*) FROM codes")
    code_count = cursor.fetchone()[0]
    print(f"コードの総数: {code_count}")

    # テストケースの数を確認
    cursor.execute("SELECT COUNT(*) FROM test_cases")
    test_count = cursor.fetchone()[0]
    print(f"テストケースの総数: {test_count}")

    # サンプルのコードとテストケースを表示
    cursor.execute("SELECT id, substr(code, 1, 100) FROM codes LIMIT 1")
    sample_code = cursor.fetchone()
    if sample_code:
        print(f"\nサンプルコード (ID: {sample_code[0]}):")
        print(sample_code[1] + "...")

        cursor.execute(
            "SELECT input, expected_output FROM test_cases WHERE code_id = ? LIMIT 1",
            (sample_code[0],),
        )
        sample_test = cursor.fetchone()
        if sample_test:
            print(f"\nコード{sample_code[0]}のサンプルテストケース:")
            print(f"入力: {sample_test[0]}")
            print(f"期待される出力: {sample_test[1]}")

    conn.close()


if __name__ == "__main__":
    verify_data()
