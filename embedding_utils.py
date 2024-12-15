import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import boto3
import json

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="ap-northeast-1" # Tokyo region
)

def get_code_embedding(code: str):
    """コードの埋め込みベクトルを取得 (Bedrock APIを使用)"""
    model_id = "amazon.titan-embed-text-v1"
    body = json.dumps({"inputText": code})
    accept = "application/json"
    content_type = "application/json"

    response = bedrock_runtime.invoke_model(
        body=body, modelId=model_id, accept=accept, contentType=content_type
    )
    response_body = json.loads(response.get("body").read())
    embedding = response_body.get("embedding")
    return embedding


def calculate_cosine_similarity(embedding1: list, embedding2: list):
    """コサイン類似度を計算"""
    embedding1 = np.array(embedding1).reshape(1, -1)
    embedding2 = np.array(embedding2).reshape(1, -1)
    similarity = cosine_similarity(embedding1, embedding2)[0][0]
    return similarity
