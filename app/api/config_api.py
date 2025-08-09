from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.utils.config import load_config, set_conf, get_conf
from app.utils.logger import logger
from app.utils.auth import require_admin_auth

router = APIRouter(prefix="/api", tags=["config"]) 

class UpdateConfigRequest(BaseModel):
    fuse_alpha: float | None = None
    high: float | None = None
    low: float | None = None

@router.get('/config')
def get_config(_: bool = require_admin_auth()):
    try:
        data = load_config()
        return {
            'retrieval': {
                'fuse_alpha': get_conf('retrieval.fuse_alpha', 0.5),
                'confidence_threshold': {
                    'high': get_conf('retrieval.confidence_threshold.high', 0.8),
                    'low': get_conf('retrieval.confidence_threshold.low', 0.5)
                }
            }
        }
    except Exception as e:
        logger.exception(f"get_config failed: {e}")
        raise HTTPException(status_code=500, detail='get_config_failed')

@router.put('/config')
def update_config(req: UpdateConfigRequest, _: bool = require_admin_auth()):
    try:
        if req.fuse_alpha is not None:
            set_conf('retrieval.fuse_alpha', float(req.fuse_alpha))
        if req.high is not None:
            set_conf('retrieval.confidence_threshold.high', float(req.high))
        if req.low is not None:
            set_conf('retrieval.confidence_threshold.low', float(req.low))
        return get_config()
    except Exception as e:
        logger.exception(f"update_config failed: {e}")
        raise HTTPException(status_code=500, detail='update_config_failed')

