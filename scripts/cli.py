import sys
import os
from pathlib import Path
import requests

BASE = os.environ.get('WONK_API', 'http://127.0.0.1:8000')

def usage():
    print('Usage: python scripts/cli.py "你的问题"')


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
    q = sys.argv[1]
    try:
        r = requests.post(f'{BASE}/api/query', json={'query': q, 'top_k': 5}, timeout=10)
        r.raise_for_status()
        data = r.json()
        print('Answer:', data.get('answer'))
        print('Confidence:', data.get('confidence'))
        if data.get('candidates'):
            print('Candidates:')
            for c in data['candidates'][:3]:
                print('-', c['question'], f"[{c['score']:.2f}]")
    except Exception as e:
        print('Error:', e)
        sys.exit(2)

if __name__ == '__main__':
    main()

