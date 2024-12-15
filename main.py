import db_utils
import embedding_utils


def main():
    # データベース作成
    db_utils.create_database()
    print("Database created/connected.")

    # コードデータの挿入（例）
    code1 = """def add(a, b):\n    return a + b"""
    code_id_1 = db_utils.insert_code_data(
        code=code1,
        language="Python",
        description="Addition function",
    )
    if code_id_1:
        print(f"Code ID: {code_id_1}")
        embedding = embedding_utils.get_code_embedding(code1)
        if db_utils.update_code_embedding(code_id_1, embedding):
            print(f"Updated embedding for code ID: {code_id_1}")

        if db_utils.insert_test_case(
            code_id=code_id_1,
            input_val="1, 2",
            expected_output="3",
            description="Test case 1",
        ):
            print("Inserted Test Case 1 for add function")
        if db_utils.insert_test_case(
            code_id=code_id_1,
            input_val="5, -3",
            expected_output="2",
            description="Test case 2",
        ):
            print("Inserted Test Case 2 for add function")

    code2 = """def subtract(a, b):\n    return a - b"""
    code_id_2 = db_utils.insert_code_data(
        code=code2,
        language="Python",
        description="Subtraction function",
    )
    if code_id_2:
        print(f"Code ID: {code_id_2}")
        embedding = embedding_utils.get_code_embedding(code2)
        if db_utils.update_code_embedding(code_id_2, embedding):
            print(f"Updated embedding for code ID: {code_id_2}")

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
