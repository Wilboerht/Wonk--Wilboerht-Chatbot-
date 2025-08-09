import os
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.logger import logger

# HTTP Bearer token scheme
security = HTTPBearer()

def get_admin_token() -> str:
    """获取管理员token，优先从环境变量读取"""
    token = os.getenv('WONK_ADMIN_TOKEN')
    if not token:
        # 如果没有设置环境变量，使用默认token（仅开发环境）
        default_token = "wonk-admin-2025"
        logger.warning(f"WONK_ADMIN_TOKEN not set, using default token: {default_token}")
        return default_token
    return token

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """验证管理员token"""
    expected_token = get_admin_token()
    
    if credentials.credentials != expected_token:
        logger.warning(f"Invalid admin token attempt: {credentials.credentials[:10]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid admin token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info("Admin token verified successfully")
    return True

def require_admin_auth():
    """管理员鉴权依赖，用于保护管理接口"""
    return Depends(verify_admin_token)
