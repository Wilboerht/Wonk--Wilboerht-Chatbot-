from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import QueryRequest, QueryResponse, Candidate
from app.core.retriever import retrieve, SemanticRetriever
from app.core.data_manager import init_db, get_all_faqs, count_faqs
from app.core.matcher import apply_threshold
from app.utils.logger import logger
from app.utils.config import get_conf
import uuid

router = APIRouter(prefix="/api", tags=["query"])

_sem = SemanticRetriever()
init_db()
_last_count = None

@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    trace_id = str(uuid.uuid4())
    try:
        global _last_count
        cur = count_faqs()
        if _last_count is None or cur != _last_count:
            # 语义缓存失效，触发重建（在 SemanticRetriever 内部会自动处理）
            if _sem and _sem.available:
                _sem.embeddings = []
            _last_count = cur
        alpha = float(get_conf('retrieval.fuse_alpha', 0.5))
        high = float(get_conf('retrieval.confidence_threshold.high', 0.8))
        low = float(get_conf('retrieval.confidence_threshold.low', 0.5))
        bm25_rows, fused = retrieve(req.query, top_k=req.top_k, alpha=alpha, semantic_retriever=_sem)
        # 若语义返回了ID但不在bm25_rows内，补一遍完整行
        bm25_map = {r["id"]: r for r in bm25_rows}
        db_map = None
        candidates: List[Candidate] = []
        for rid, score in fused[:req.top_k]:
            row = bm25_map.get(rid)
            if row is None:
                if db_map is None:
                    db_map = {r["id"]: r for r in get_all_faqs()}
                row = db_map.get(rid)
                if row is None:
                    continue
            candidates.append(Candidate(id=row["id"], question=row["question"], answer=row["answer"], score=float(score)))
        if candidates:
            best = candidates[0]
            best_score, level = apply_threshold([(c.id, c.score) for c in candidates], high=high, low=low)
            return QueryResponse(query=req.query, answer=best.answer, confidence=best.score, source_id=best.id, candidates=candidates, trace_id=trace_id)
        else:
            return QueryResponse(query=req.query, answer=None, confidence=0.0, source_id=None, candidates=[], trace_id=trace_id)
    except Exception as e:
        logger.exception(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail={"message": "internal_error", "trace_id": trace_id})

