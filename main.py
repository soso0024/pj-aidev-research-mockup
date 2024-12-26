from database import connection, code_repository, test_repository
from embedding.api_client import BedrockClient
from embedding.similarity import find_most_similar


def insert_code_with_tests(code_data: dict):
    """コードとそれに関連するテストケースを挿入します。

    Args:
        code_data: {
            'code': str,          # コードスニペット
            'language': str,      # プログラミング言語
            'description': str,   # コードの説明
            'test_cases': list    # テストケースのリスト
        }
    """
    code_id = code_repository.insert_code(
        code=code_data["code"],
        language=code_data["language"],
        description=code_data["description"],
    )

    if code_id:
        print(f"Code ID: {code_id}")
        bedrock = BedrockClient()
        embedding = bedrock.get_embedding(code_data["code"])

        if code_repository.update_embedding(code_id, embedding):
            print(f"Updated embedding for code ID: {code_id}")

        for test_case in code_data["test_cases"]:
            if test_repository.insert_test_case(
                code_id=code_id,
                input_val=test_case["input"],
                expected_output=test_case["expected_output"],
                description=test_case["description"],
            ):
                print(
                    f"Inserted {test_case['description']} for {code_data['description']}"
                )


def find_similar_code(code: str):
    """類似コードを検索し、関連するテストケースを取得します。

    Args:
        code: 検索対象のコード
    """
    bedrock = BedrockClient()
    code_embedding = bedrock.get_embedding(code)
    code_embeddings = code_repository.get_embeddings()

    if not code_embeddings:
        print("\nコードデータが見つかりません")
        return

    best_match_id, similarity = find_most_similar(code_embedding, code_embeddings)

    if best_match_id:
        print(f"\n最も類似したコード ID: {best_match_id}")
        print(f"類似度: {similarity:.4f}")

        test_cases = test_repository.get_test_cases(best_match_id)
        if test_cases:
            print("\n選択されたテストケース:")
            for input_val, expected_output in test_cases:
                print(f"Input: {input_val}, Expected Output: {expected_output}")
        else:
            print(f"\nコード ID {best_match_id} のテストケースが見つかりません")
    else:
        print("\n類似コードが見つかりません")


def main():
    # データベース初期化
    connection.create_database()
    print("Database created/connected.")

    # サンプルコードの定義
    code_samples = [
        {
            "code": """def add(a, b):\n    return a + b""",
            "language": "Python",
            "description": "Addition function",
            "test_cases": [
                {"input": "1, 2", "expected_output": "3", "description": "Test case 1"},
                {
                    "input": "5, -3",
                    "expected_output": "2",
                    "description": "Test case 2",
                },
            ],
        },
        {
            "code": """def subtract(a, b):\n    return a - b""",
            "language": "Python",
            "description": "Subtraction function",
            "test_cases": [
                {"input": "5, 3", "expected_output": "2", "description": "Test case 1"},
                {
                    "input": "10, 7",
                    "expected_output": "3",
                    "description": "Test case 2",
                },
            ],
        },
    ]

    # サンプルコードの登録
    for code_data in code_samples:
        insert_code_with_tests(code_data)

    # 類似コード検索のデモ
    print("\n=== 類似コードの検索 ===")
    ai_code = """def multiply(x, y):\n    return x * y"""
    print(f"AI生成コード:\n{ai_code}")
    find_similar_code(ai_code)


if __name__ == "__main__":
    main()
