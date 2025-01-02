from database import connection, code_repository, test_repository
from embedding.api_client import BedrockClient
from embedding.gemini_client import GeminiClient
from embedding.similarity import find_most_similar
from sample_codes import code_samples


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
    code_id = code_repository.insert_code(code=code_data["code"])

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
            ):
                print(f"Inserted test case for code ID {code_id}")


def run_test_case(code: str, input_val: str, expected_output: str):
    """テストケースを実行し、結果を返します。

    Args:
        code: 実行するコード
        input_val: テストケースの入力値
        expected_output: 期待される出力

    Returns:
        (bool, str): テストの成功/失敗と実際の出力
    """
    try:
        # コードをグローバル名前空間で実行
        namespace = {}
        exec(code, namespace)
        
        # 関数名を取得（最初の関数定義を使用）
        func_name = None
        for name, obj in namespace.items():
            if callable(obj) and name != '__builtins__':
                func_name = name
                break
        
        if not func_name:
            return False, "No function found in code"
        
        # 入力値を引数リストに変換
        args = []
        if ',' in input_val:
            # カンマで区切られた複数の引数を分割
            arg_strings = [arg.strip() for arg in input_val.split(',')]
            for arg in arg_strings:
                try:
                    # 各引数を評価して適切な型に変換
                    args.append(eval(arg))
                except:
                    # 評価できない場合は文字列として扱う
                    args.append(arg)
        else:
            # 単一の引数の場合
            try:
                args.append(eval(input_val))
            except:
                args.append(input_val)
            
        # 期待される出力を評価
        try:
            expected_output = eval(expected_output)
        except:
            pass  # 文字列として扱う
            
        # 関数を実行（複数の引数に対応）
        actual_output = namespace[func_name](*args)
        
        # 結果を比較
        success = actual_output == expected_output
        return success, str(actual_output)
    except Exception as e:
        return False, f"Error: {str(e)}"

def find_similar_code(code: str):
    """類似コードを検索し、関連するテストケースを取得して実行します。

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
            print("\nテスト実行結果:")
            total_tests = len(test_cases)
            passed_tests = 0
            for input_val, expected_output in test_cases:
                success, actual_output = run_test_case(code, input_val, expected_output)
                if success:
                    passed_tests += 1
                print(f"Input: {input_val}")
                print(f"Expected Output: {expected_output}")
                print(f"Actual Output: {actual_output}")
                print(f"Result: {'✓ Pass' if success else '✗ Fail'}\n")
            
            # テストケースの通過率を表示
            pass_rate = (passed_tests / total_tests) * 100
            print(f"テスト結果サマリー: {passed_tests}/{total_tests} テストケース通過 ({pass_rate:.1f}%)")
        else:
            print(f"\nコード ID {best_match_id} のテストケースが見つかりません")
    else:
        print("\n類似コードが見つかりません")


def main():
    # データベース初期化
    connection.create_database()
    print("Database created/connected.")

    # サンプルコードの登録
    for code_data in code_samples:
        insert_code_with_tests(code_data)

    # 類似コード検索のデモ
    print("\n=== 類似コードの検索 ===")

    # Geminiを使用してコードを生成
    gemini = GeminiClient()
    prompt = input("類似コードを検索するためのプロンプトを入力してください: ")
    ai_code = gemini.generate_code(prompt)

    if ai_code:
        print(f"AI生成コード:\n{ai_code}")
        find_similar_code(ai_code)
    else:
        print("コードの生成に失敗しました")


if __name__ == "__main__":
    main()
