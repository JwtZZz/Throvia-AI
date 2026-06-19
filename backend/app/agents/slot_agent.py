from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings
from app.core.llm import invoke_with_fallback
from app.graph.state import AgentState


TIME_RANGE_PATTERNS = {
    "1d": ["1d", "today", "intraday", "今天"],
    "5d": ["5d", "5 days", "this week", "本周"],
    "1mo": ["1mo", "1 month", "最近", "近期", "这个月"],
    "6mo": ["6mo", "6 months", "半年", "六个月"],
}

PREFERENCE_KEYWORDS = ["remember", "i prefer", "focus on", "记住", "我偏好", "更关注"]
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


def _extract_symbol(user_input: str) -> Optional[str]:
    lowered = user_input.lower()
    if any(keyword in lowered for keyword in PREFERENCE_KEYWORDS):
        return None
    for alias, symbol in COMPANY_ALIASES.items():
        if alias in lowered:
            return symbol
    matches = re.findall(r"\b[A-Z]{1,5}\b", user_input.upper())
    if not matches:
        return None
    reserved = {"AI", "I", "A"}
    for symbol in matches:
        if symbol not in reserved:
            return symbol
    return matches[0] if matches else None


def _extract_time_range(user_input: str) -> str:
    lowered = user_input.lower()
    for time_range, patterns in TIME_RANGE_PATTERNS.items():
        if any(pattern.lower() in lowered for pattern in patterns):
            return time_range
    return "1mo"


def _extract_focus(user_input: str) -> List[str]:
    lowered = user_input.lower()
    focus: List[str] = []
    mapping = {
        "news": ["news", "headline", "消息", "新闻"],
        "technical": ["technical", "chart", "技术", "技术面", "rsi"],
        "financial": ["financial", "fundamental", "财务", "基本面"],
        "risk": ["risk", "风险"],
    }
    for focus_name, keywords in mapping.items():
        if any(keyword in lowered for keyword in keywords):
            focus.append(focus_name)
    return focus or ["full"]


def _extract_alert_fields(user_input: str) -> Tuple[Optional[float], Optional[str]]:
    lowered = user_input.lower()
    condition = None
    if any(keyword in lowered for keyword in ["above", "突破", "高于", "涨到"]):
        condition = "price_above"
    elif any(keyword in lowered for keyword in ["below", "跌破", "低于", "跌到"]):
        condition = "price_below"

    price_match = re.search(r"(\d+(?:\.\d+)?)", user_input)
    target_price = float(price_match.group(1)) if price_match else None
    return target_price, condition


def _rule_slots(user_input: str) -> Dict[str, Any]:
    target_price, condition = _extract_alert_fields(user_input)
    lowered = user_input.lower()
    report_type = "full"
    if any(keyword in lowered for keyword in ["quick", "brief", "简短", "快速"]):
        report_type = "quick"

    return {
        "symbol": _extract_symbol(user_input),
        "time_range": _extract_time_range(user_input),
        "focus": _extract_focus(user_input),
        "report_type": report_type,
        "target_price": target_price,
        "condition": condition,
    }


def _llm_slots(user_input: str) -> Optional[Dict[str, Any]]:
    if not settings.llm_enabled:
        return None

    messages = [
        SystemMessage(
            content=(
                "You are the SlotAgent for AnthroVest AI.\n"
                "Extract task parameters from the user's request.\n\n"
                "Return strict JSON:\n"
                '{\n'
                '  "symbol": "NVDA or null",\n'
                '  "time_range": "1d | 5d | 1mo | 6mo | null",\n'
                '  "focus": ["full" | "news" | "technical" | "financial" | "risk"],\n'
                '  "report_type": "quick | full",\n'
                '  "target_price": number or null,\n'
                '  "condition": "price_above | price_below | null"\n'
                '}'
            )
        ),
        HumanMessage(content=user_input),
    ]
    raw = invoke_with_fallback(messages, purpose="slot_extraction")
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

    if not isinstance(data, dict):
        return None
    return data


def run_slot_agent(state: AgentState) -> AgentState:
    print("[SlotAgent] running...")
    next_state = state.copy()
    next_state["agent_status"]["SlotAgent"] = "running"

    slots = _rule_slots(next_state["user_input"])
    llm_slots = _llm_slots(next_state["user_input"])
    if llm_slots:
        slots = {
            "symbol": llm_slots.get("symbol") or slots["symbol"],
            "time_range": llm_slots.get("time_range") or slots["time_range"],
            "focus": llm_slots.get("focus") or slots["focus"],
            "report_type": llm_slots.get("report_type") or slots["report_type"],
            "target_price": llm_slots.get("target_price", slots["target_price"]),
            "condition": llm_slots.get("condition") or slots["condition"],
        }

    if not isinstance(slots.get("focus"), list) or not slots["focus"]:
        slots["focus"] = ["full"]

    next_state["slots"] = slots
    next_state["missing_slots"] = []
    next_state["agent_status"]["SlotAgent"] = "completed"
    next_state["observations"].append({"agent": "SlotAgent", "slots": slots})
    focus_display = ",".join(slots["focus"])
    print(
        f"[SlotAgent] symbol = {slots.get('symbol')}, time_range = {slots.get('time_range')}, focus = {focus_display}"
    )
    return next_state
