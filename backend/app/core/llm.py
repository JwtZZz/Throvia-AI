from __future__ import annotations

import logging
from typing import Iterable, List, Optional

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings


logger = logging.getLogger(__name__)


def _sanitize_exception_message(exc: Exception) -> str:
    message = str(exc)
    if settings.openrouter_api_key:
        message = message.replace(settings.openrouter_api_key, "***")
    return message


def get_openrouter_llm(model: Optional[str] = None) -> Optional[ChatOpenAI]:
    if not settings.llm_enabled:
        return None

    return ChatOpenAI(
        model=model or settings.openrouter_model,
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.2,
        timeout=60,
        max_retries=1,
    )


def invoke_with_fallback(
    messages: Iterable[BaseMessage],
    purpose: str,
) -> Optional[str]:
    if not settings.llm_enabled:
        return None

    ordered_models: List[str] = []
    for model_name in [settings.openrouter_model, *settings.openrouter_fallback_models]:
        clean = model_name.strip()
        if clean and clean not in ordered_models:
            ordered_models.append(clean)

    for model_name in ordered_models:
        try:
            llm = get_openrouter_llm(model_name)
            if llm is None:
                return None
            response = llm.invoke(list(messages))
            content = getattr(response, "content", None)
            if isinstance(content, list):
                content = "\n".join(str(item) for item in content)
            if content:
                return str(content).strip()
        except Exception as exc:  # pragma: no cover - network/provider failures
            logger.warning(
                "OpenRouter invocation failed",
                extra={
                    "purpose": purpose,
                    "model": model_name,
                    "error": _sanitize_exception_message(exc),
                },
            )

    return None
