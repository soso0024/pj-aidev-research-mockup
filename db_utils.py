import json
import re
from typing import Dict, List, Any, Optional, Tuple
from database.code_repository import insert_code, update_embedding
from database.test_repository import insert_test_case
from embedding.api_client import BedrockClient
from datasets import load_dataset
from database.connection import create_database
import ast


import cmath


def convert_complex_number(num: complex) -> Dict[str, float]:
    """複素数をJSON シリアライズ可能な形式に変換します。

    Args:
        num: 変換する複素数

    Returns:
        Dict[str, float]: 実部と虚部を含む辞書
    """
    return {"real": num.real, "imag": num.imag}


def convert_to_json_serializable(obj: Any) -> Any:
    """オブジェクトをJSON シリアライズ可能な形式に変換します。

    Args:
        obj: 変換する対象のオブジェクト

    Returns:
        Any: JSON シリアライズ可能な形式に変換されたオブジェクト
    """
    if isinstance(obj, (set, frozenset)):
        return list(obj)
    elif isinstance(obj, complex):
        return convert_complex_number(obj)
    elif isinstance(obj, tuple):
        return list(obj)
    elif isinstance(obj, dict):
        return {str(k): convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(x) for x in obj]
    elif isinstance(obj, float) and (cmath.isinf(obj) or cmath.isnan(obj)):
        return str(obj)
    return obj


def safe_json_dumps(obj: Any) -> str:
    """オブジェクトを安全にJSONシリアライズします。

    Args:
        obj: シリアライズする対象のオブジェクト

    Returns:
        str: JSONシリアライズされた文字列
    """
    try:
        return json.dumps(convert_to_json_serializable(obj))
    except TypeError as e:
        print(f"Error serializing object: {e}")
        return json.dumps(str(obj))


def extract_test_data_from_test_field(test_str: str) -> List[Tuple[Any, Any]]:
    """テストフィールドからテストデータを抽出します。

    Args:
        test_str: テストコードを含む文字列

    Returns:
        List[Tuple[Any, Any]]: (入力値, 期待される出力値)のタプルのリスト
    """
    try:
        # inputsとresultsの部分を抽出
        inputs_match = re.search(
            r"inputs\s*=\s*(\[.*?\])\s*results", test_str, re.DOTALL
        )
        results_match = re.search(r"results\s*=\s*(\[.*?\])\s*for", test_str, re.DOTALL)

        if not inputs_match or not results_match:
            return []

        # 文字列を評価可能な形式に整形
        inputs_str = inputs_match.group(1).replace("\n", "").replace(" ", "")
        results_str = results_match.group(1).replace("\n", "").replace(" ", "")

        # 文字列をPythonオブジェクトに変換
        inputs = ast.literal_eval(inputs_str)
        results = ast.literal_eval(results_str)

        # 入力と出力のペアを作成し、JSON シリアライズ可能な形式に変換
        test_cases = []
        for input_val, expected in zip(inputs, results):
            input_val = convert_to_json_serializable(input_val)
            expected = convert_to_json_serializable(expected)
            test_cases.append((input_val, expected))

        return test_cases
    except Exception as e:
        print(f"Error extracting test data: {e}")
        return []


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


def process_test_cases(code_id: int, test_data: List[Tuple[Any, Any]]) -> bool:
    """テストケースを処理し、データベースに保存します。

    Args:
        code_id: 関連するコードのID
        test_data: (入力値, 期待される出力値)のタプルのリスト

    Returns:
        bool: 全てのテストケースの保存が成功した場合はTrue
    """
    try:
        success = True
        for input_val, output_val in test_data:
            input_str = safe_json_dumps(input_val)
            output_str = safe_json_dumps(output_val)

            if not insert_test_case(code_id, input_str, output_str):
                print(f"Failed to insert test case for code {code_id}")
                success = False

        return success
    except Exception as e:
        print(f"Error processing test cases: {e}")
        return False


def load_and_store_data() -> Dict[str, int]:
    """HuggingFaceのデータセットからデータを読み込み、データベースに格納します。

    Returns:
        Dict[str, int]: 処理結果の統計情報
    """
    stats = {
        "total_solutions": 0,
        "successful_solutions": 0,
        "failed_solutions": 0,
        "successful_test_cases": 0,
    }

    try:
        # データベースの初期化
        print("Initializing database...")
        create_database()

        # データセットの読み込み
        print("Loading dataset...")
        dataset = load_dataset("evalplus/mbppplus")
        print(f"Dataset structure: {dataset}")

        if not dataset or "test" not in dataset:
            print("Failed to load dataset or 'test' split not found")
            return stats

        # データセットの最初の要素を表示（デバッグ用）
        first_example = dataset["test"][0]
        print("\nFirst example structure:")
        for key, value in first_example.items():
            print(f"{key}: {type(value)}")
            if key in ["code", "test"]:
                print(
                    f"Sample {key}:",
                    value[:200] + "..." if isinstance(value, str) else value[:2],
                )

        # BedrockClientのインスタンスを作成
        bedrock_client = BedrockClient()

        # 統計情報の初期化
        test_dataset = dataset["test"]
        stats["total_solutions"] = len(test_dataset)
        print(f"\nProcessing {stats['total_solutions']} examples...")

        # 各サンプルの処理
        for i, sample in enumerate(test_dataset):
            if i % 10 == 0:  # より頻繁に進捗を表示
                print(f"Processing example {i}/{stats['total_solutions']}")

            code = sample["code"]
            test_data = extract_test_data_from_test_field(sample["test"])

            if not test_data:
                print(f"Failed to extract test data for example {i}")
                stats["failed_solutions"] += 1
                continue

            code_id = process_code(code, bedrock_client)
            if code_id:
                stats["successful_solutions"] += 1
                if process_test_cases(code_id, test_data):
                    stats["successful_test_cases"] += 1
            else:
                stats["failed_solutions"] += 1

        return stats
    except Exception as e:
        print(f"Error loading dataset: {e}")
        import traceback

        traceback.print_exc()
        return stats


if __name__ == "__main__":
    print("=== データベース作成とデータ読み込み・保存の開始 ===")

    # データベースの作成
    create_database()
    print("データベースが作成されました。")

    # データの読み込みと保存
    stats = load_and_store_data()

    print("\n=== 処理結果 ===")
    print(f"総ソリューション数: {stats['total_solutions']}")
    print(f"成功したソリューション: {stats['successful_solutions']}")
    print(f"失敗したソリューション: {stats['failed_solutions']}")
    print(f"テストケース保存成功: {stats['successful_test_cases']}")

    print("\nデータベースファイルが作成され、データが保存されました。")
