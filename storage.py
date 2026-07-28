import json
import os
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "config.json"

_lock_data: dict[str, Any] = {}


def _load() -> dict[str, Any]:
    global _lock_data
    if not DATA_FILE.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text("{}", encoding="utf-8")
        _lock_data = {}
        return _lock_data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        _lock_data = json.load(f)
    return _lock_data


def _save(data: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_guild_config(guild_id: int) -> dict[str, Any]:
    data = _load()
    return data.get(str(guild_id), {})


def set_guild_config(guild_id: int, **kwargs: Any) -> None:
    data = _load()
    key = str(guild_id)
    conf = data.get(key, {})
    conf.update(kwargs)
    data[key] = conf
    _save(data)
