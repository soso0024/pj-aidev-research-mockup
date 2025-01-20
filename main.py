from typing import Dict, List, Optional, Tuple
from database import connection
from database.code_repository import (
    insert_code,
    update_embedding,
    get_code_by_id,
    get_embeddings,
)
from database.test_repository import insert_test_case, get_test_cases
from embedding.api_client import BedrockClient
from embedding.gemini_client import GeminiClient
from embedding.similarity import find_most_similar

# from sample_codes import code_samples


class CodeProcessor:
    def __init__(self):
        self.bedrock_client = BedrockClient()
        self.gemini_client = GeminiClient()

    def process_sample_code(self, code_data: Dict) -> Optional[int]:
        """サンプルコードとそのテストケースを処理します。"""
        code_id = insert_code(code=code_data["code"])
        if not code_id:
            return None

        try:
            embedding = self.bedrock_client.get_embedding(code_data["code"])
            if update_embedding(code_id, embedding):
                print(f"Updated embedding for code ID: {code_id}")

                for test_case in code_data["test_cases"]:
                    if insert_test_case(
                        code_id=code_id,
                        input_val=test_case["input"],
                        expected_output=test_case["expected_output"],
                    ):
                        print(f"Inserted test case for code ID {code_id}")
                return code_id
        except Exception as e:
            print(f"Error processing sample code: {e}")
        return None


class TestRunner:
    @staticmethod
    def run_test_case(
        code: str, input_val: str, expected_output: str
    ) -> Tuple[bool, str]:
        """テストケースを実行します。"""
        try:
            # コードをグローバル名前空間で実行
            namespace = {}
            exec(code, namespace)

            # 関数名を取得（最初の関数定義を使用）
            func_name = next(
                (
                    name
                    for name, obj in namespace.items()
                    if callable(obj) and name != "__builtins__"
                ),
                None,
            )
            if not func_name:
                return False, "No function found in code"

            # 入力値を引数リストに変換
            args = []
            if "," in input_val:
                # カンマで区切られた複数の引数を分割
                for arg in (arg.strip() for arg in input_val.split(",")):
                    try:
                        args.append(eval(arg))
                    except:
                        args.append(arg)
            else:
                try:
                    args.append(eval(input_val))
                except:
                    args.append(input_val)

            # 期待される出力を評価
            try:
                expected = eval(expected_output)
            except:
                expected = expected_output

            # 関数を実行
            actual = namespace[func_name](*args)
            success = actual == expected
            return success, str(actual)

        except Exception as e:
            return False, f"Error: {str(e)}"


class TestResultFormatter:
    @staticmethod
    def format_test_results(
        test_results: List[Tuple[str, str, bool, str]], limit: int = 3
    ) -> str:
        """テスト結果を整形します。"""
        total_tests = len(test_results)
        passed_tests = sum(1 for _, _, success, _ in test_results if success)
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        output = ["\n=== テスト実行結果 (3つのサンプル) ==="]
        for i, (input_val, expected, success, actual) in enumerate(
            test_results[:limit], 1
        ):
            output.extend(
                [
                    f"\nテストケース {i}:",
                    f"入力値: {input_val}",
                    f"期待される出力: {expected}",
                    f"実際の出力: {actual}",
                    f"結果: {'✓ Pass' if success else '✗ Fail'}",
                ]
            )

        output.extend(
            [
                f"\n=== テスト結果サマリー ===",
                f"テスト成功: {passed_tests}/{total_tests}",
                f"成功率: {pass_rate:.1f}%",
            ]
        )

        return "\n".join(output)


def find_and_test_similar_code(code: str, test_runner: TestRunner) -> None:
    """類似コードを検索し、テストを実行します。"""
    bedrock = BedrockClient()
    code_embedding = bedrock.get_embedding(code)
    code_embeddings = get_embeddings()

    if not code_embeddings:
        print("\nコードデータが見つかりません")
        return

    best_match_id, similarity = find_most_similar(code_embedding, code_embeddings)
    if not best_match_id:
        print("\n類似コードが見つかりません")
        return

    print(f"\n最も類似したコード ID: {best_match_id}")
    print(f"類似度: {similarity:.4f}")

    similar_code = get_code_by_id(best_match_id)
    if not similar_code:
        print(f"\nコード ID {best_match_id} の取得に失敗しました")
        return

    test_cases = get_test_cases(best_match_id)
    if not test_cases:
        print(f"\nコード ID {best_match_id} のテストケースが見つかりません")
        return

    # 3つのテストケースのみ表示
    print("\n=== 利用可能なテストケース (3つのサンプル) ===")
    for i, (input_val, expected_output) in enumerate(test_cases[:3], 1):
        print(f"\nテストケース {i}:")
        print(f"入力値: {input_val}")
        print(f"期待される出力: {expected_output}")

    # テストケース実行の確認
    user_input = input("\nすべてのテストケースを実行しますか？ (y/n): ").lower()

    if user_input == "y":
        # すべてのテストケースの実行
        print("\n~~~ テスト実行開始 ~~~")
        test_results = []
        for input_val, expected_output in test_cases:
            success, actual = test_runner.run_test_case(
                code, input_val, expected_output
            )
            test_results.append((input_val, expected_output, success, actual))

        # 結果サマリーの表示（3つのサンプルのみ）
        print(TestResultFormatter.format_test_results(test_results))
    else:
        print("\nテストケースの実行をスキップしました")


def main():
    processor = CodeProcessor()

    # サンプルコードの登録
    # for code_data in code_samples:
    #     processor.process_sample_code(code_data)

    # 類似コード検索のデモ
    print("\n=== 類似コードの検索 ===")
    try:
        with open("question.txt", "r", encoding="utf-8") as f:
            prompt = f.read().strip()
        print(f"プロンプト: {prompt}")

        ai_code = processor.gemini_client.generate_code(prompt)
    except FileNotFoundError:
        print("エラー: question.txtファイルが見つかりません")
        return
    except Exception as e:
        print(f"エラー: プロンプトの読み込み中にエラーが発生しました - {str(e)}")
        return
    if ai_code:
        print(f"\nAI生成コード:\n{ai_code}")
        find_and_test_similar_code(ai_code, TestRunner())
    else:
        print("コードの生成に失敗しました")


if __name__ == "__main__":
    main()
