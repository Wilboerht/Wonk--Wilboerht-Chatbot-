import os
import sqlite3
from contextlib import contextmanager
from typing import Iterable, List, Optional, Tuple
from app.utils.logger import logger

DB_PATH = os.getenv("WONK_DB_PATH", "data/database.db")

# 确保目录存在
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

@contextmanager
def get_conn() -> Iterable[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.exception(f"DB error: {e}")
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        # 基础表
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS faqs (
                id INTEGER PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                language TEXT DEFAULT 'auto',
                tags TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # 聊天会话表
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                user_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # 聊天消息表
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY,
                session_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
            );
            """
        )

        # 创建索引
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at ON chat_sessions(updated_at);")
        # FTS5 可选创建
        try:
            cur.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS faqs_fts USING fts5(
                    question, answer, tags, content='faqs', content_rowid='id'
                );
                """
            )
            conn.commit()
            logger.info("FTS5 virtual table ready")
        except sqlite3.OperationalError as e:
            logger.warning(f"FTS5 not available, fallback to LIKE search. Detail: {e}")
        # 触发器保持FTS同步
        try:
            cur.executescript(
                """
                CREATE TRIGGER IF NOT EXISTS faqs_ai AFTER INSERT ON faqs BEGIN
                  INSERT INTO faqs_fts(rowid, question, answer, tags) VALUES (new.id, new.question, new.answer, new.tags);
                END;
                CREATE TRIGGER IF NOT EXISTS faqs_ad AFTER DELETE ON faqs BEGIN
                  INSERT INTO faqs_fts(faqs_fts, rowid, question, answer, tags) VALUES ('delete', old.id, old.question, old.answer, old.tags);
                END;
                CREATE TRIGGER IF NOT EXISTS faqs_au AFTER UPDATE ON faqs BEGIN
                  INSERT INTO faqs_fts(faqs_fts, rowid, question, answer, tags) VALUES ('delete', old.id, old.question, old.answer, old.tags);
                  INSERT INTO faqs_fts(rowid, question, answer, tags) VALUES (new.id, new.question, new.answer, new.tags);
                END;
                """
            )
        except sqlite3.OperationalError:
            pass


def rebuild_fts() -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM faqs_fts;")
            cur.execute(
                "INSERT INTO faqs_fts(rowid, question, answer, tags) SELECT id, question, answer, tags FROM faqs;"
            )
            logger.info("FTS rebuilt")
        except sqlite3.OperationalError as e:
            logger.warning(f"Cannot rebuild FTS: {e}")


def insert_faqs(items: List[Tuple[str, str, str, Optional[str], Optional[str]]]) -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.executemany(
            "INSERT INTO faqs(question, answer, language, tags, source) VALUES (?, ?, ?, ?, ?);",
            items,
        )
        return cur.rowcount


def list_faqs(limit: int = 100, offset: int = 0) -> List[sqlite3.Row]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM faqs ORDER BY id DESC LIMIT ? OFFSET ?;", (limit, offset))
        return cur.fetchall()


def get_all_faqs() -> List[sqlite3.Row]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, question, answer, language, tags, source FROM faqs ORDER BY id ASC;")
        return cur.fetchall()


def count_faqs() -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as c FROM faqs;")
        row = cur.fetchone()
        return int(row[0]) if row else 0


def delete_faq(faq_id: int) -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM faqs WHERE id=?;", (faq_id,))
        return cur.rowcount


def update_faq(faq_id: int, question: str, answer: str, language: str, tags: Optional[str], source: Optional[str]) -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE faqs SET question=?, answer=?, language=?, tags=?, source=? WHERE id=?;",
            (question, answer, language, tags, source, faq_id),
        )
        return cur.rowcount


def search_bm25(query: str, top_k: int = 10) -> List[sqlite3.Row]:
    with get_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT faqs.id, faqs.question, faqs.answer, bm25(faqs_fts) as score FROM faqs_fts JOIN faqs ON faqs_fts.rowid = faqs.id WHERE faqs_fts MATCH ? ORDER BY score LIMIT ?;",
                (query, top_k),
            )
            rows = cur.fetchall()
            if rows:
                return rows
            # 空结果时回退到 LIKE 提高召回
            like_q = f"%{query}%"
            cur.execute(
                "SELECT id, question, answer, 0.0 as score FROM faqs WHERE question LIKE ? OR answer LIKE ? LIMIT ?;",
                (like_q, like_q, top_k),
            )
            return cur.fetchall()
        except sqlite3.OperationalError:
            # FTS不可用，回退到 LIKE
            like_q = f"%{query}%"
            cur.execute(
                "SELECT id, question, answer, 0.0 as score FROM faqs WHERE question LIKE ? OR answer LIKE ? LIMIT ?;",
                (like_q, like_q, top_k),
            )
            return cur.fetchall()


# ==================== 聊天相关方法 ====================

def create_chat_session(title: str, user_id: Optional[str] = None) -> int:
    """创建新的聊天会话"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat_sessions (title, user_id) VALUES (?, ?);",
            (title, user_id)
        )
        return cur.lastrowid


def get_chat_sessions(user_id: Optional[str] = None, limit: int = 50) -> List[sqlite3.Row]:
    """获取聊天会话列表"""
    with get_conn() as conn:
        cur = conn.cursor()
        if user_id:
            cur.execute(
                "SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC LIMIT ?;",
                (user_id, limit)
            )
        else:
            cur.execute(
                "SELECT * FROM chat_sessions ORDER BY updated_at DESC LIMIT ?;",
                (limit,)
            )
        return cur.fetchall()


def get_chat_session(session_id: int) -> Optional[sqlite3.Row]:
    """获取单个聊天会话"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM chat_sessions WHERE id = ?;", (session_id,))
        return cur.fetchone()


def update_chat_session_timestamp(session_id: int) -> None:
    """更新聊天会话的最后更新时间"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
            (session_id,)
        )


def add_chat_message(session_id: int, role: str, content: str) -> int:
    """添加聊天消息"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?);",
            (session_id, role, content)
        )
        message_id = cur.lastrowid

        # 在同一个事务中更新会话的最后更新时间
        cur.execute(
            "UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
            (session_id,)
        )

        return message_id


def get_chat_messages(session_id: int, limit: int = 100) -> List[sqlite3.Row]:
    """获取聊天消息历史"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY timestamp ASC LIMIT ?;",
            (session_id, limit)
        )
        return cur.fetchall()


def delete_chat_session(session_id: int) -> int:
    """删除聊天会话（级联删除消息）"""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM chat_sessions WHERE id = ?;", (session_id,))
        return cur.rowcount


def get_chat_session_by_latest_message(user_id: Optional[str] = None) -> Optional[sqlite3.Row]:
    """获取最近有消息的会话"""
    with get_conn() as conn:
        cur = conn.cursor()
        if user_id:
            cur.execute(
                """
                SELECT cs.* FROM chat_sessions cs
                INNER JOIN chat_messages cm ON cs.id = cm.session_id
                WHERE cs.user_id = ?
                ORDER BY cm.timestamp DESC
                LIMIT 1;
                """,
                (user_id,)
            )
        else:
            cur.execute(
                """
                SELECT cs.* FROM chat_sessions cs
                INNER JOIN chat_messages cm ON cs.id = cm.session_id
                ORDER BY cm.timestamp DESC
                LIMIT 1;
                """
            )
        return cur.fetchone()

