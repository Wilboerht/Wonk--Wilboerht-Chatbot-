from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logger import logger

app = FastAPI(title="Wonk Chatbot API", version="0.1.0")

# CORS 允许本机和简单前端
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入并注册路由
from app.api.query import router as query_router
from app.api.manage import router as manage_router
from app.api.config_api import router as config_router

app.include_router(query_router)
app.include_router(manage_router)
app.include_router(config_router)

@app.get("/")
def root():
    return {
        "name": "Wonk Chatbot API",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "query": "POST /api/query",
            "config": "/api/config",
            "ingest": "POST /api/ingest"
        }
    }

@app.get("/health")
def health():
    logger.info("Health check OK")
    return {"status": "ok"}

