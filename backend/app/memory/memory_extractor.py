from __future__ import annotations

from typing import Optional


PREFERENCE_KEYWORDS = [
    "remember",
    "i prefer",
    "focus on",
    "记住",
    "我偏好",
    "更关注",
]


def extract_preference_memory(user_input: str) -> Optional[str]:
    lowered = user_input.lower()
    if not any(keyword in lowered for keyword in PREFERENCE_KEYWORDS):
        return None
    cleaned = " ".join(user_input.strip().split())
    return cleaned if cleaned else None
