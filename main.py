import db_utils
import embedding_utils


def insert_code_with_tests(code_data):
    """
    コードとそれに関連するテストケースを挿入する関数

    Args:
        code_data: コードとテストケースの情報を含む辞書
            {
                'code': str,          # コードスニペット
                'language': str,      # プログラミング言語
                'description': str,   # コードの説明
                'test_cases': list    # テストケースのリスト
            }
    """
    code_id = db_utils.insert_code_data(
        code=code_data['code'],
        language=code_data['language'],
        description=code_data['description'],
    )
    
    if code_id:
        print(f"Code ID: {code_id}")
        embedding = embedding_utils.get_code_embedding(code_data['code'])
        if db_utils.update_code_embedding(code_id, embedding):
            print(f"Updated embedding for code ID: {code_id}")

        for test_case in code_data['test_cases']:
            if db_utils.insert_test_case(
                code_id=code_id,
                input_val=test_case['input'],
                expected_output=test_case['expected_output'],
                description=test_case['description'],
            ):
                print(f"Inserted {test_case['description']} for {code_data['description']}")


def main():
    # データベース作成
    db_utils.create_database()
    print("Database created/connected.")

    # コードとテストケースのデータ定義
    code_samples = [
        {
            'code': """def add(a, b):\n    return a + b""",
            'language': "Python",
            'description': "Addition function",
            'test_cases': [
                {
                    'input': "1, 2",
                    'expected_output': "3",
                    'description': "Test case 1"
                },
                {
                    'input': "5, -3",
                    'expected_output': "2",
                    'description': "Test case 2"
                }
            ]
        },
        {
            'code': """def subtract(a, b):\n    return a - b""",
            'language': "Python",
            'description': "Subtraction function",
            'test_cases': [
                {
                    'input': "5, 3",
                    'expected_output': "2",
                    'description': "Test case 1"
                },
                {
                    'input': "10, 7",
                    'expected_output': "3",
                    'description': "Test case 2"
                }
            ]
        }
    ]

    # 各コードサンプルを処理
    for code_data in code_samples:
        insert_code_with_tests(code_data)

    print("\n=== 類似コードの検索 ===")
    # AI生成コードの例
    ai_code = """def multiply(x, y):\n    return x * y"""
    print(f"AI生成コード:\n{ai_code}")
    ai_embedding = embedding_utils.get_code_embedding(ai_code)

    # 類似コードの検索とテストケースの選択
    code_embeddings = db_utils.get_code_embeddings()
    print(f"\n取得したembedding数: {len(code_embeddings)}")

    best_match_id = None
    max_similarity = -1

    if code_embeddings:
        print("\n各コードとの類似度:")
        for code_id, db_embedding in code_embeddings:
            similarity = embedding_utils.calculate_cosine_similarity(
                ai_embedding, db_embedding
            )
            print(f"Code ID {code_id}: {similarity:.4f}")
            if similarity > max_similarity:
                max_similarity = similarity
                best_match_id = code_id

        if best_match_id:
            print(f"\n最も類似したコード ID: {best_match_id}")
            print(f"類似度: {max_similarity:.4f}")

            test_cases = db_utils.get_test_cases(best_match_id)
            if test_cases:
                print("\n選択されたテストケース:")
                for input_val, expected_output in test_cases:
                    print(f"Input: {input_val}, Expected Output: {expected_output}")
            else:
                print(f"\nコード ID {best_match_id} のテストケースが見つかりません")
        else:
            print("\n類似コードが見つかりません")
    else:
        print("\nコードデータが見つかりません")


if __name__ == "__main__":
    main()
