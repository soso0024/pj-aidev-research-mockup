import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import heapq


def find_most_similar(target_embedding: list, code_embeddings: list, top_n: int = 3):
    """最も類似したコードを見つけます。

    Args:
        target_embedding: 検索対象の埋め込みベクトル
        code_embeddings: (コードID, 埋め込みベクトル)のタプルのリスト
        top_n: 返す類似コードの数

    Returns:
        [(コードID, 類似度)]の形式で上位n個の類似コードのリスト
    """
    if not code_embeddings:
        return []

    target_embedding = np.array(target_embedding).reshape(1, -1)
    similarities = []

    for code_id, embedding in code_embeddings:
        embedding = np.array(embedding).reshape(1, -1)
        similarity = cosine_similarity(target_embedding, embedding)[0][0]
        heapq.heappush(similarities, (-similarity, code_id))

    top_matches = []
    for _ in range(min(top_n, len(similarities))):
        if similarities:
            similarity, code_id = heapq.heappop(similarities)
            top_matches.append((code_id, -similarity))

    return top_matches
