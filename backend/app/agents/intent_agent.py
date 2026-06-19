from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings
from app.core.llm import invoke_with_fallback
from app.graph.state import AgentState


SUPPORTED_INTENTS = {
    "stock_analysis",
    "market_overview",
    "news_search",
    "financial_report",
    "technical_analysis",
    "create_alert",
    "chat",
    "unsupported",
}

PREFERENCE_KEYWORDS = ["remember", "i prefer", "focus on", "记住", "我偏好", "更关注"]
CHAT_KEYWORDS = [
    "hi",
    "hello",
    "你好",
    "谢谢",
    "how are you",
    "help",
    "帮助",
    "怎么用",
    "如何用",
    "你是谁",
    "你是啥",
    "你是什么",
    "你是什么模型",
    "what model",
    "who are you",
    "what are you",
]
COMPANY_ALIASES = {
    "英伟达": "NVDA",
    "辉达": "NVDA",
    "英伟達": "NVDA",
    "苹果": "AAPL",
    "特斯拉": "TSLA",
    "微软": "MSFT",
    "谷歌": "GOOGL",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "亚马逊": "AMZN",
    "meta": "META",
    "脸书": "META",
    "amd": "AMD",
    "台积电": "TSM",
    "阿里": "BABA",
    "阿里巴巴": "BABA",
    "拼多多": "PDD",
    "网易": "NTES",
}


def _rule_intent(user_input: str) -> Dict[str, Any]:
    text = user_input.lower()

    if any(keyword in text for keyword in PREFERENCE_KEYWORDS):
        return {"intent": "chat", "confidence": 0.82, "reason": "Matched memory or preference keyword"}
    if any(keyword in text for keyword in CHAT_KEYWORDS):
        return {"intent": "chat", "confidence": 0.84, "reason": "Matched chat or identity keyword"}
    if any(keyword in text for keyword in ["price alert", "alert", "提醒", "价格提醒"]):
        return {"intent": "create_alert", "confidence": 0.84, "reason": "Matched alert keyword"}
    if any(keyword in text for keyword in ["market overview", "macro", "大盘", "市场概览", "市场总览"]):
        return {"intent": "market_overview", "confidence": 0.78, "reason": "Matched overview keyword"}
    if any(keyword in text for keyword in ["news", "headline", "消息", "新闻"]):
        return {"intent": "news_search", "confidence": 0.74, "reason": "Matched news keyword"}
    if any(keyword in text for keyword in ["financial", "财务", "fundamental", "基本面"]):
        return {"intent": "financial_report", "confidence": 0.76, "reason": "Matched financial keyword"}
    if any(keyword in text for keyword in ["technical", "chart", "rsi", "技术面", "技术"]):
        return {"intent": "technical_analysis", "confidence": 0.76, "reason": "Matched technical keyword"}
    if any(alias in text for alias in COMPANY_ALIASES):
        return {"intent": "stock_analysis", "confidence": 0.88, "reason": "Matched company alias"}
    if re.search(r"\b[A-Z]{1,5}\b", user_input.upper()) or any(
        keyword in text for keyword in ["analyze", "analysis", "分析", "看看", "最近怎么样"]
    ):
        return {"intent": "stock_analysis", "confidence": 0.8, "reason": "Matched stock analysis pattern"}
    return {"intent": "unsupported", "confidence": 0.35, "reason": "No supported pattern matched"}


def _llm_intent(user_input: str) -> Optional[Dict[str, Any]]:
    if not settings.llm_enabled:
        return None

    messages = [
        SystemMessage(
            content=(
                "You are the IntentAgent for AnthroVest AI.\n"
                "Classify the user's request into one of:\n"
                "- stock_analysis\n"
                "- market_overview\n"
                "- news_search\n"
                "- financial_report\n"
                "- technical_analysis\n"
                "- create_alert\n"
                "- chat\n"
                "- unsupported\n\n"
                "Return strict JSON:\n"
                '{\n  "intent": "...",\n  "confidence": 0.0,\n  "reason": "..."\n}'
            )
        ),
        HumanMessage(content=user_input),
    ]
    raw = invoke_with_fallback(messages, purpose="intent_classification")
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    intent = data.get("intent")
    confidence = data.get("confidence")
    reason = data.get("reason")
    if intent not in SUPPORTED_INTENTS:
        return None
    try:
        parsed_confidence = float(confidence)
    except (TypeError, ValueError):
        return None
    return {
        "intent": intent,
        "confidence": max(0.0, min(parsed_confidence, 1.0)),
        "reason": str(reason or "LLM classified the user request."),
    }


def run_intent_agent(state: AgentState) -> AgentState:
    print("[IntentAgent] running...")
    next_state = state.copy()
    next_state["agent_status"]["IntentAgent"] = "running"

    result = _rule_intent(next_state["user_input"])
    llm_result = _llm_intent(next_state["user_input"])
    if llm_result:
        result = llm_result

    next_state["intent"] = result["intent"]
    next_state["confidence"] = result["confidence"]
    next_state["agent_status"]["IntentAgent"] = "completed"
    next_state["observations"].append(
        {
            "agent": "IntentAgent",
            "intent": result["intent"],
            "reason": result["reason"],
        }
    )
    print(f"[IntentAgent] intent = {next_state['intent']}")
    return next_state
