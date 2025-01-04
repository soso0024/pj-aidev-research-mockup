import json
from database.code_repository import insert_code, update_embedding
from database.test_repository import insert_test_case
from embedding.api_client import BedrockClient


def load_and_store_data(solutions_path: str, input_output_path: str):
    """
    ソリューションとテストケースをデータベースに格納します。
    コードはBedrockを使用してベクトル化されます。
    """
    # BedrockClientのインスタンスを作成
    bedrock_client = BedrockClient()

    # solutions.jsonを読み込む
    with open(solutions_path, "r") as f:
        solutions = json.load(f)

    # input_output.jsonを読み込む
    with open(input_output_path, "r") as f:
        test_data = json.load(f)

    # 各ソリューションをデータベースに格納
    code_ids = []
    for solution in solutions:
        # コードを保存
        code_id = insert_code(solution)
        if code_id:
            try:
                # コードをベクトル化
                embedding = bedrock_client.get_embedding(solution)
                # 埋め込みベクトルを更新
                if update_embedding(code_id, embedding):
                    code_ids.append(code_id)
                else:
                    print(f"Failed to update embedding for code ID: {code_id}")
            except Exception as e:
                print(f"Error vectorizing code: {e}")
        else:
            print(f"Failed to insert code: {solution[:100]}...")

    # テストケースを格納
    inputs = test_data["inputs"]
    outputs = test_data["outputs"]

    # 各コードに対してテストケースを追加
    for code_id in code_ids:
        for test_input, test_output in zip(inputs, outputs):
            # 入力と出力をJSON文字列として格納
            input_str = json.dumps(test_input)
            output_str = json.dumps(test_output)

            success = insert_test_case(code_id, input_str, output_str)
            if not success:
                print(f"Failed to insert test case for code {code_id}")


if __name__ == "__main__":
    solutions_path = "APPS/train/4998/solutions.json"
    input_output_path = "APPS/train/4998/input_output.json"
    load_and_store_data(solutions_path, input_output_path)
