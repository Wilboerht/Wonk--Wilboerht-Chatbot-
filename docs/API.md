# API 文档（MVP）

## 健康检查
GET /health
- 200 {"status":"ok"}

## 查询
POST /api/query
Body:
{
  "query": "string",
  "top_k": 5
}
Response 200:
{
  "query": "...",
  "answer": "..." | null,
  "confidence": 0.0-1.0,
  "source_id": 1 | null,
  "candidates": [{"id":1,"question":"...","answer":"...","score":0.9}],
  "trace_id": "uuid"
}

## 导入FAQ
POST /api/ingest
Body:
{
  "items": [{"question":"...","answer":"...","language":"zh|en|auto","tags":["..."],"source":"..."}],
  "rebuild_index": true
}

## 列表FAQ
GET /api/faqs?limit=100&offset=0

## 重建索引
POST /api/rebuild_index

