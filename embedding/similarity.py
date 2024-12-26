import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(embedding1: list, embedding2: list) -> float:
    """2つの埋め込みベクトル間のコサイン類似度を計算します。"""
    embedding1 = np.array(embedding1).reshape(1, -1)
    embedding2 = np.array(embedding2).reshape(1, -1)
    return cosine_similarity(embedding1, embedding2)[0][0]


def find_most_similar(target_embedding: list, embeddings: list) -> tuple:
    """最も類似度の高いコードとその類似度を返します。

    Args:
        target_embedding: 比較対象の埋め込みベクトル
        embeddings: (code_id, embedding)のタプルのリスト

    Returns:
        (最も類似度の高いコードのID, 類似度)のタプル
    """
    best_match_id = None
    max_similarity = -1

    for code_id, db_embedding in embeddings:
        similarity = calculate_similarity(target_embedding, db_embedding)
        if similarity > max_similarity:
            max_similarity = similarity
            best_match_id = code_id

    return best_match_id, max_similarity
