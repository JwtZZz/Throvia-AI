from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.core.config import settings


MEMORY_FILE = settings.data_dir / "long_term_memory.json"


def load_long_term_memory() -> List[Dict[str, Any]]:
    if not MEMORY_FILE.exists():
        return []
    try:
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_long_term_memory(memories: List[Dict[str, Any]]) -> None:
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(
        json.dumps(memories, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def append_long_term_memory(memory_item: Dict[str, Any]) -> None:
    memories = load_long_term_memory()
    content = str(memory_item.get("content", "")).strip()
    if content and any(entry.get("content") == content for entry in memories):
        return
    memories.append(memory_item)
    save_long_term_memory(memories)
