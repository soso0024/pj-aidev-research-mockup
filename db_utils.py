import json
from typing import Dict, List, Any
from database.code_repository import insert_code, update_embedding
from database.test_repository import insert_test_case
from embedding.api_client import BedrockClient
from datasets import load_dataset
import re
import ast


def normalize_test_case(test_str: str) -> str:
    """テストケース文字列を正規化します。

    Args:
        test_str: 元のテストケース文字列

    Returns:
        str: 正規化されたテストケース文字列
    """
    # スペースを正規化
    test_str = re.sub(r'\s+', ' ', test_str.strip())
    
    # カンマのない配列表記を修正
    test_str = re.sub(r'\[(\d+)\s+(\d+)', r'[\1, \2', test_str)
    
    # 括弧のない関数呼び出しを修正
    test_str = re.sub(r'assert\s+(\w+)\s+([^=\s]+)', r'assert \1(\2)', test_str)
    
    return test_str


def extract_test_case(test_assertion: str) -> tuple[Any, Any]:
    """テストケースのアサーションから入力と期待される出力を抽出します。

    Args:
        test_assertion: アサーション文字列

    Returns:
        tuple[Any, Any]: (入力値, 期待される出力値)のタプル
    """
    try:
        # テストケース文字列を正規化
        test_assertion = normalize_test_case(test_assertion)
        
        # 基本的なアサーション形式をチェック
        basic_match = re.match(r'assert\s+([\w_]+)\((.*?)\)\s*==\s*(.*?)(?:,|\s*$)', test_assertion)
        if basic_match:
            func_name, input_str, output_str = basic_match.groups()
            try:
                # 文字列を Python の式として評価
                input_val = ast.literal_eval(input_str)
                output_val = ast.literal_eval(output_str)
                return input_val, output_val
            except (ValueError, SyntaxError):
                print(f"Failed to parse test case values: {test_assertion}")
                return None, None
        
        # 特殊なアサーション形式をチェック（例：assert not func(x)）
        special_match = re.match(r'assert\s+not\s+([\w_]+)\((.*?)\)', test_assertion)
        if special_match:
            func_name, input_str = special_match.groups()
            try:
                input_val = ast.literal_eval(input_str)
                return input_val, False
            except (ValueError, SyntaxError):
                print(f"Failed to parse special test case: {test_assertion}")
                return None, None
        
        # その他の形式のアサーション
        print(f"Unrecognized test case format: {test_assertion}")
        return None, None
        
    except Exception as e:
        print(f"Error extracting test case: {e}")
        return None, None


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


def process_test_cases(code_id: int, test_list: List[str]) -> bool:
    """テストケースを処理し、データベースに保存します。

    Args:
        code_id: 関連するコードのID
        test_list: テストケースのリスト

    Returns:
        bool: 全てのテストケースの保存が成功した場合はTrue
    """
    try:
        success = True
        for test_case in test_list:
            input_val, output_val = extract_test_case(test_case)
            if input_val is None or output_val is None:
                print(f"Failed to extract test case from: {test_case}")
                continue
                
            input_str = json.dumps(input_val)
            output_str = json.dumps(output_val)
            
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
            if key in ["code", "test_list"]:
                print(f"Sample {key}:", value[:200] + "..." if isinstance(value, str) else value[:2])

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
            test_list = sample["test_list"]

            code_id = process_code(code, bedrock_client)
            if code_id:
                stats["successful_solutions"] += 1
                if process_test_cases(code_id, test_list):
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
    print("=== データ読み込みと保存の開始 ===")
    stats = load_and_store_data()

    print("\n=== 処理結果 ===")
    print(f"総ソリューション数: {stats['total_solutions']}")
    print(f"成功したソリューション: {stats['successful_solutions']}")
    print(f"失敗したソリューション: {stats['failed_solutions']}")
    print(f"テストケース保存成功: {stats['successful_test_cases']}")
