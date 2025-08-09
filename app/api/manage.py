from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.schemas import FAQItem, IngestRequest
from app.core.data_manager import init_db, insert_faqs, list_faqs, delete_faq, update_faq, rebuild_fts
from app.utils.logger import logger
from app.utils.auth import require_admin_auth

router = APIRouter(prefix="/api", tags=["manage"])

init_db()

@router.post("/ingest")
def ingest(req: IngestRequest, _: bool = require_admin_auth()):
    try:
        rows = [(
            item.question,
            item.answer,
            item.language or "auto",
            ",".join(item.tags) if item.tags else None,
            item.source,
        ) for item in req.items]
        count = insert_faqs(rows)
        if req.rebuild_index:
            rebuild_fts()
        return {"inserted": count}
    except Exception as e:
        logger.exception(f"Ingest failed: {e}")
        raise HTTPException(status_code=500, detail="ingest_failed")

@router.get("/faqs")
def faqs(limit: int = 100, offset: int = 0):
    try:
        rows = list_faqs(limit, offset)
        return [{k: r[k] for k in r.keys()} for r in rows]
    except Exception as e:
        logger.exception(f"List faqs failed: {e}")
        raise HTTPException(status_code=500, detail="list_failed")

@router.post("/rebuild_index")
def rebuild(_: bool = require_admin_auth()):
    try:
        rebuild_fts()
        return {"status": "ok"}
    except Exception as e:
        logger.exception(f"Rebuild index failed: {e}")
        raise HTTPException(status_code=500, detail="rebuild_failed")

