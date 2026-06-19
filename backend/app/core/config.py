from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field


BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_ROOT / ".env")


class Settings(BaseModel):
    app_name: str = "AnthroVest AI"
    backend_root: Path = BACKEND_ROOT
    data_dir: Path = BACKEND_ROOT / "data"

    openrouter_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("OPENROUTER_API_KEY") or None
    )
    openrouter_model: str = Field(
        default_factory=lambda: os.getenv("OPENROUTER_MODEL", "openrouter/free")
    )
    openrouter_fallback_models_raw: str = Field(
        default_factory=lambda: os.getenv(
            "OPENROUTER_FALLBACK_MODELS",
            "openrouter/free,qwen/qwen3-coder:free,deepseek/deepseek-r1:free,meta-llama/llama-3.3-70b-instruct:free",
        )
    )

    @property
    def openrouter_fallback_models(self) -> List[str]:
        seen: List[str] = []
        for model in self.openrouter_fallback_models_raw.split(","):
            clean = model.strip()
            if clean and clean not in seen:
                seen.append(clean)
        return seen

    @property
    def llm_enabled(self) -> bool:
        return bool(self.openrouter_api_key)


settings = Settings()
