import sys
import os
import json
from pathlib import Path

# 兼容直接运行脚本的导入路径
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.data_manager import init_db, insert_faqs, rebuild_fts  # noqa: E402


def main(path: str):
    p = Path(path)
    if not p.exists():
        print(f"File not found: {p}")
        sys.exit(1)
    init_db()
    items = []
    bad = 0
    with p.open('r', encoding='utf-8') as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                bad += 1
                continue
            q = obj.get('question')
            a = obj.get('answer')
            if not q or not a:
                bad += 1
                continue
            lang = obj.get('language', 'auto')
            tags = obj.get('tags')
            source = obj.get('source')
            items.append((q, a, lang, ",".join(tags) if isinstance(tags, list) else tags, source))
    if not items:
        print("No items to import")
        return
    count = insert_faqs(items)
    rebuild_fts()
    print(f"Imported {count} items and rebuilt FTS index; skipped {bad} bad lines")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_data.py data/samples/faq_sample.jsonl")
        sys.exit(1)
    main(sys.argv[1])

