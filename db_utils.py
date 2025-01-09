import json
from typing import Dict, List, Any
from database.code_repository import insert_code, update_embedding
from database.test_repository import insert_test_case
from embedding.api_client import BedrockClient


def load_json_file(file_path: str) -> Any:
    """JSONファイルを読み込みます。

    Args:
        file_path: JSONファイルのパス

    Returns:
        Any: 読み込まれたJSONデータ
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return None


def process_code(code: str, bedrock_client: BedrockClient) -> int:
    """コードを処理し、データベースに保存します。

    Args:
        code: 保存するコード
        bedrock_client: BedrockClientのインスタンス

    Returns:
        int: 保存されたコードのID、失敗した場合は0
    """
    try:
        code_id = insert_code(code)
        if not code_id:
            return 0

        embedding = bedrock_client.get_embedding(code)
        if not embedding or not update_embedding(code_id, embedding):
            print(f"Failed to update embedding for code ID: {code_id}")
            return 0

        return code_id
    except Exception as e:
        print(f"Error processing code: {e}")
        return 0


def process_test_cases(code_id: int, inputs: List[Any], outputs: List[Any]) -> bool:
    """テストケースを処理し、データベースに保存します。

    Args:
        code_id: 関連するコードのID
        inputs: テストケースの入力値のリスト
        outputs: テストケースの期待される出力のリスト

    Returns:
        bool: 全てのテストケースの保存が成功した場合はTrue
    """
    try:
        success = True
        for test_input, test_output in zip(inputs, outputs):
            input_str = json.dumps(test_input)
            output_str = json.dumps(test_output)
            if not insert_test_case(code_id, input_str, output_str):
                print(f"Failed to insert test case for code {code_id}")
                success = False
        return success
    except Exception as e:
        print(f"Error processing test cases: {e}")
        return False


def load_and_store_data(solutions_path: str, input_output_path: str) -> Dict[str, int]:
    """ソリューションとテストケースをデータベースに格納します。

    Args:
        solutions_path: ソリューションJSONファイルのパス
        input_output_path: 入出力JSONファイルのパス

    Returns:
        Dict[str, int]: 処理結果の統計情報
    """
    stats = {
        "total_solutions": 0,
        "successful_solutions": 0,
        "failed_solutions": 0,
        "successful_test_cases": 0,
    }

    # JSONファイルの読み込み
    solutions = load_json_file(solutions_path)
    test_data = load_json_file(input_output_path)
    if not solutions or not test_data:
        return stats

    # BedrockClientのインスタンスを作成
    bedrock_client = BedrockClient()

    # 統計情報の初期化
    stats["total_solutions"] = len(solutions)

    # 各ソリューションの処理
    for solution in solutions:
        code_id = process_code(solution, bedrock_client)
        if code_id:
            stats["successful_solutions"] += 1
            if process_test_cases(code_id, test_data["inputs"], test_data["outputs"]):
                stats["successful_test_cases"] += 1
        else:
            stats["failed_solutions"] += 1

    return stats


if __name__ == "__main__":
    solutions_path = "APPS/train/4998/solutions.json"
    input_output_path = "APPS/train/4998/input_output.json"

    print("=== データ読み込みと保存の開始 ===")
    stats = load_and_store_data(solutions_path, input_output_path)

    print("\n=== 処理結果 ===")
    print(f"総ソリューション数: {stats['total_solutions']}")
    print(f"成功したソリューション: {stats['successful_solutions']}")
    print(f"失敗したソリューション: {stats['failed_solutions']}")
    print(f"テストケース保存成功: {stats['successful_test_cases']}")
