import os
import tempfile
from fastapi.testclient import TestClient
from app.main import app
from app.core import data_manager as dm


def setup_module(module):
    # 用临时库隔离测试
    td = tempfile.TemporaryDirectory()
    module._td = td
    os.environ['WONK_DB_PATH'] = os.path.join(td.name, 'test.db')
    dm.DB_PATH = os.environ['WONK_DB_PATH']
    dm.init_db()
    dm.insert_faqs([
        ('What is Wonk?', 'Wonk is a local FAQ chatbot.', 'en', None, 'test'),
        ('什么是 Wonk？', 'Wonk 是一个本地运行的FAQ聊天机器人。', 'zh', None, 'test')
    ])


def teardown_module(module):
    module._td.cleanup()


def test_health():
    c = TestClient(app)
    r = c.get('/health')
    assert r.status_code == 200


def test_query():
    c = TestClient(app)
    r = c.post('/api/query', json={'query': '什么是 Wonk？', 'top_k': 5})
    assert r.status_code == 200
    data = r.json()
    assert data['answer']

