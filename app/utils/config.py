import os
import yaml
from functools import lru_cache
from typing import Any, Dict

CONFIG_PATH = os.getenv('WONK_CONFIG', 'config.yaml')

@lru_cache(maxsize=1)
def load_config() -> Dict[str, Any]:
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data or {}
    except Exception:
        return {}


def reload_config_cache():
    try:
        load_config.cache_clear()
    except Exception:
        pass


def save_config(data: Dict[str, Any]) -> None:
    # 确保目录存在
    d = os.path.dirname(CONFIG_PATH)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
    reload_config_cache()


def get_conf(path: str, default=None):
    data = load_config()
    cur = data
    for part in path.split('.'):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


def set_conf(path: str, value: Any) -> Dict[str, Any]:
    data = load_config() or {}
    cur = data
    parts = path.split('.')
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value
    save_config(data)
    return data

