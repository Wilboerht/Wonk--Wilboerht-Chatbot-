import os
from typing import List, Tuple, Optional
from math import sqrt
from app.utils.logger import logger
from app.core.data_manager import search_bm25, get_all_faqs

# 语义检索依赖按需导入
_USE_SEMANTIC = os.getenv("WONK_USE_SEMANTIC", "true").lower() == "true"
# fastembed 推荐中文小模型；英文仍由BM25兜底（也可改为 bge-small-en-v1.5）
_FE_MODEL = os.getenv("WONK_FE_MODEL", "BAAI/bge-small-zh-v1.5")
_ST_MODEL = os.getenv("WONK_ST_MODEL", "intfloat/multilingual-e5-small")


def _l2_norm(vec: List[float]) -> float:
    return sqrt(sum(v * v for v in vec)) or 1.0


def _cosine(a: List[float], b: List[float]) -> float:
    num = sum(x * y for x, y in zip(a, b))
    den = _l2_norm(a) * _l2_norm(b)
    return float(num / den)


class SemanticRetriever:
    def __init__(self, fe_model_name: str = _FE_MODEL, st_model_name: str = _ST_MODEL):
        self.fe_model_name = fe_model_name
        self.st_model_name = st_model_name
        self.backend = None  # 'fastembed' | 'st' | None
        self.model = None
        self.embeddings: List[List[float]] = []
        self.id_map: List[int] = []
        self.available = False
        self._lazy_init()

    def _lazy_init(self):
        # 优先 fastembed（无需 torch/编译依赖）
        try:
            from fastembed import TextEmbedding
            # models = TextEmbedding.list_supported_models()
            self.model = TextEmbedding(self.fe_model_name)
            self.backend = 'fastembed'
            self.available = True
            logger.info(f"Semantic retriever ready (fastembed): {self.fe_model_name}")
            return
        except Exception as fe:
            logger.warning(f"fastembed unavailable: {fe}")
        # 回退到 sentence-transformers（可能需要 torch）
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.st_model_name)
            self.backend = 'st'
            self.available = True
            logger.info(f"Semantic retriever ready (st): {self.st_model_name}")
        except Exception as st:
            self.model = None
            self.backend = None
            self.available = False
            logger.warning(f"Semantic retrieval disabled: {st}")

    def _encode(self, texts: List[str]) -> List[List[float]]:
        if self.backend == 'fastembed':
            # fastembed 返回生成器，逐条获取
            embs: List[List[float]] = []
            for e in self.model.embed(texts):
                embs.append(list(e))
            return embs
        elif self.backend == 'st':
            embs = self.model.encode(texts, convert_to_numpy=False, show_progress_bar=False)
            # ensure python lists
            return [list(map(float, vec)) for vec in embs]
        else:
            return []

    def build_from_db(self):
        if not self.available:
            return
        try:
            rows = get_all_faqs()
            if not rows:
                self.embeddings = []
                self.id_map = []
                return
            texts = [r["question"] + " \n" + r["answer"] for r in rows]
            ids = [r["id"] for r in rows]
            embs = self._encode(texts)
            self.embeddings = embs
            self.id_map = ids
            logger.info(f"Built vector cache from DB: {len(ids)} items, backend={self.backend}")
        except Exception as e:
            logger.warning(f"Build vector cache failed: {e}")
            self.embeddings = []
            self.id_map = []

    def query(self, text: str, top_k: int = 10) -> List[Tuple[int, float]]:
        if not self.available:
            return []
        if not self.embeddings:
            self.build_from_db()
            if not self.embeddings:
                return []
        q = self._encode([text])[0]
        # 计算余弦相似度，返回 top_k
        sims = []
        for idx, emb in enumerate(self.embeddings):
            sims.append((self.id_map[idx], _cosine(q, emb)))
        sims.sort(key=lambda x: x[1], reverse=True)
        return sims[:top_k]


def fuse_scores(bm25_results, semantic_scores: dict, alpha: float = 0.5) -> List[Tuple[int, float]]:
    # 归一化 BM25 分数（越小越好）→ 转为相似度
    if not bm25_results and not semantic_scores:
        return []
    bm25_ids = [r["id"] for r in bm25_results]
    bm25_vals = [r["score"] for r in bm25_results]
    bm25_sim = {}
    if bm25_vals:
        m = max(bm25_vals)
        n = min(bm25_vals)
        if m == n:
            bm25_sim = {rid: 0.3 for rid in bm25_ids}
        else:
            denom = (m - n)
            bm25_sim = {rid: (1.0 - (val - n) / denom) * 0.9 for rid, val in zip(bm25_ids, bm25_vals)}
    # 合并
    all_ids = set(bm25_ids) | set(semantic_scores.keys())
    fused = []
    for rid in all_ids:
        b = bm25_sim.get(rid, 0.0)
        s = semantic_scores.get(rid, 0.0)
        fused.append((rid, alpha * s + (1 - alpha) * b))
    fused.sort(key=lambda x: x[1], reverse=True)
    return fused


def _fuzzy_fallback(query: str, top_k: int = 5) -> List[Tuple[int, float]]:
    try:
        from rapidfuzz import fuzz
    except Exception:
        return []
    rows = get_all_faqs()
    if not rows:
        return []
    scored: List[Tuple[int, float]] = []
    for r in rows:
        q = r["question"] or ""
        a = r["answer"] or ""
        # 对问题与答案分别打分，取最大值，提高鲁棒性
        s = max(fuzz.token_set_ratio(query, q), fuzz.token_set_ratio(query, a)) / 100.0
        scored.append((int(r["id"]), float(s)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def retrieve(query: str, top_k: int = 5, alpha: float = 0.5,
             semantic_retriever: Optional[SemanticRetriever] = None):
    bm25_rows = search_bm25(query, top_k=top_k)
    # 仅当可用时使用语义检索
    semantic_scores = {}
    if _USE_SEMANTIC and semantic_retriever and semantic_retriever.available:
        sem = semantic_retriever.query(query, top_k=top_k)
        semantic_scores = {rid: score for rid, score in sem}
    fused = fuse_scores(bm25_rows, semantic_scores, alpha=alpha)
    if not fused:
        # 最后兜底：模糊匹配
        fuzzy = _fuzzy_fallback(query, top_k=top_k)
        fused = fuzzy
    return bm25_rows, fused

