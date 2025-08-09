from app.core.data_manager import init_db, rebuild_fts

if __name__ == '__main__':
    init_db()
    rebuild_fts()
    print("FTS index rebuilt (if available)")

