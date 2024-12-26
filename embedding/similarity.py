import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def find_most_similar(target_embedding: list, code_embeddings: list):
    """最も類似したコードを見つけます。

    Args:
        target_embedding: 検索対象の埋め込みベクトル
        code_embeddings: (コードID, 埋め込みベクトル)のタプルのリスト

    Returns:
        (最も類似したコードのID, 類似度)のタプル
    """
    if not code_embeddings:
        return None, 0

    best_match_id = None
    best_similarity = -1

    target_embedding = np.array(target_embedding).reshape(1, -1)

    for code_id, embedding in code_embeddings:
        embedding = np.array(embedding).reshape(1, -1)
        similarity = cosine_similarity(target_embedding, embedding)[0][0]

        if similarity > best_similarity:
            best_similarity = similarity
            best_match_id = code_id

    return best_match_id, best_similarity