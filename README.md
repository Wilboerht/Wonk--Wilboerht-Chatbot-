# Wonk (Wilboerht Chatbot)

本项目是一个本地运行的FAQ聊天机器人，支持中英文双语，采用“BM25 + 语义向量检索”架构，优先离线，不依赖付费AI服务。

## 快速开始（功能优先，无UI）

1. 创建虚拟环境并安装依赖
2. 运行API服务：`uvicorn app.main:app --reload`
3. 导入示例数据：`python scripts/import_data.py data/samples/faq_sample.jsonl`
4. 查询接口：`POST /api/query`，传 `{ "query": "你的问题" }`

详见 docs/、scripts/ 与 app/ 代码。

## 降级与容错
- 若FTS5不可用，自动回退到SQLite LIKE 检索（性能与准确度较低）
- 若向量模型不可用/未下载，自动只用BM25检索
- 所有API返回包含错误码与可追踪ID，便于排障

## 许可
- 项目代码：MIT
- 模型与第三方库：遵循各自开源许可，请在商用前确认模型许可（建议 multilingual-e5-small / paraphrase-multilingual-MiniLM-L12-v2）

