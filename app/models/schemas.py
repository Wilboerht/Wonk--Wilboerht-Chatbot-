from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class FAQItem(BaseModel):
    id: Optional[int] = None
    question: str
    answer: str
    language: str = Field(default="auto", description="zh/en/auto")
    tags: Optional[List[str]] = None
    source: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class Candidate(BaseModel):
    question: str
    answer: str
    score: float
    id: Optional[int] = None

class QueryResponse(BaseModel):
    query: str
    answer: Optional[str]
    confidence: float
    source_id: Optional[int] = None
    candidates: List[Candidate] = Field(default_factory=list)
    trace_id: Optional[str] = None

class IngestRequest(BaseModel):
    items: List[FAQItem]
    rebuild_index: bool = True

# 聊天相关模型
class ChatSession(BaseModel):
    id: Optional[int] = None
    title: str
    user_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ChatMessage(BaseModel):
    id: Optional[int] = None
    session_id: int
    role: str  # 'user' 或 'assistant'
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None

class ChatResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    session_id: int
    message_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    error: Optional[str] = None

