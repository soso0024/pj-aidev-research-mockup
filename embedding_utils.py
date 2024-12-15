import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def get_code_embedding(code: str):
    """コードの埋め込みベクトルを取得 (モックアップ)"""
    # 本番環境ではBedrockのAPI呼び出しに置き換える
    embedding_size = 1536  # 例
    fake_embedding = list(np.random.rand(embedding_size))
    return fake_embedding


def calculate_cosine_similarity(embedding1: list, embedding2: list):
    """コサイン類似度を計算"""
    embedding1 = np.array(embedding1).reshape(1, -1)
    embedding2 = np.array(embedding2).reshape(1, -1)
    similarity = cosine_similarity(embedding1, embedding2)[0][0]
    return similarity
