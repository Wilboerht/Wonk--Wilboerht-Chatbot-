import os
import tempfile
from app.core import data_manager as dm


def test_insert_and_search_bm25():
    # 使用临时数据库
    with tempfile.TemporaryDirectory() as td:
        db_path = os.path.join(td, 'test.db')
        os.environ['WONK_DB_PATH'] = db_path
        # 重新加载模块以使用新的环境变量路径（简单起见，直接调用init_db会读取新的env）
        dm.DB_PATH = db_path
        dm.init_db()
        rows = [
            ('What is Wonk?', 'Wonk is a local FAQ chatbot.', 'en', None, 'test'),
            ('什么是Wonk', 'Wonk 是一个本地运行的FAQ机器人。', 'zh', None, 'test'),
        ]
        inserted = dm.insert_faqs(rows)
        assert inserted == 2
        # 基于关键词检索
        res = dm.search_bm25('Wonk', top_k=5)
        assert len(res) >= 1
        # 中文检索
        res_cn = dm.search_bm25('本地运行', top_k=5)
        assert len(res_cn) >= 1

