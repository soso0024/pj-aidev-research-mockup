import db_utils
import embedding_utils
import sqlite3


def main():
    # データベース作成
    db_utils.create_database()
    print("Database created/connected.")

    # コードデータの挿入（例）
    code_id_1 = db_utils.insert_code_data(
        code="""def add(a, b):\n    return a + b""",
        language="Python",
        description="Addition function",
    )
    if code_id_1:
        print(f"Inserted code with ID: {code_id_1}")
        embedding = embedding_utils.get_code_embedding(
            code="""def add(a, b):\n    return a + b"""
        )
        db_utils.update_code_embedding(code_id_1, embedding)

        if db_utils.insert_test_case(
            code_id=code_id_1,
            input_val="1, 2",
            expected_output="3",
            description="Test case 1",
        ):
            print("Inserted Test Case 1")
        if db_utils.insert_test_case(
            code_id=code_id_1,
            input_val="5, -3",
            expected_output="2",
            description="Test case 2",
        ):
            print("Inserted Test Case 2")
    code_id_2 = db_utils.insert_code_data(
        code="""def subtract(a, b):\n    return a - b""",
        language="Python",
        description="Subtraction function",
    )
    if code_id_2:
        print(f"Inserted code with ID: {code_id_2}")
        embedding = embedding_utils.get_code_embedding(
            code="""def subtract(a, b):\n    return a - b"""
        )
        db_utils.update_code_embedding(code_id_2, embedding)
    # AI生成コードの例
    ai_code = """def multiply(x, y):\n    return x * y"""
    ai_embedding = embedding_utils.get_code_embedding(ai_code)

    # 類似コードの検索とテストケースの選択
    code_embeddings = db_utils.get_code_embeddings()
    best_match_id = None
    max_similarity = -1
    if code_embeddings:

        for code_id, db_embedding in code_embeddings:
            similarity = embedding_utils.calculate_cosine_similarity(
                ai_embedding, db_embedding
            )
            if similarity > max_similarity:
                max_similarity = similarity
                best_match_id = code_id
        if best_match_id:
            test_cases = db_utils.get_test_cases(best_match_id)
            if test_cases:
                print(
                    f"Most similar code found with ID: {best_match_id}, similarity: {max_similarity}"
                )
                print("Selected Test Cases:")
                for input_val, expected_output in test_cases:
                    print(f"Input: {input_val}, Expected Output: {expected_output}")
        else:
            print("No code data found")
    else:
        print("No code data found")


if __name__ == "__main__":
    main()
