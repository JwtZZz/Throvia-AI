from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypedDict
from uuid import uuid4


class AgentState(TypedDict):
    user_id: str
    session_id: str
    user_input: str

    long_term_memory: List[Dict[str, Any]]
    retrieved_history: List[Dict[str, Any]]
    retrieved_knowledge: List[Dict[str, Any]]
    working_memory: Dict[str, Any]

    intent: Optional[str]
    confidence: Optional[float]
    slots: Dict[str, Any]
    missing_slots: List[str]

    decision: Optional[str]
    need_confirmation: bool
    risk_level: Optional[str]
    clarification_question: Optional[str]

    plan: List[Dict[str, Any]]

    market_data: Optional[Dict[str, Any]]
    news_sentiment: Optional[Dict[str, Any]]
    financial_analysis: Optional[Dict[str, Any]]
    technical_analysis: Optional[Dict[str, Any]]
    risk_analysis: Optional[Dict[str, Any]]

    final_report: Optional[str]

    agent_status: Dict[str, str]
    tool_calls: List[Dict[str, Any]]
    observations: List[Dict[str, Any]]
    errors: List[str]


def build_initial_state(
    user_input: str,
    user_id: str = "cli-user",
    session_id: Optional[str] = None,
) -> AgentState:
    session = session_id or f"session-{uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    return AgentState(
        user_id=user_id,
        session_id=session,
        user_input=user_input,
        long_term_memory=[],
        retrieved_history=[],
        retrieved_knowledge=[],
        working_memory={"created_at": now},
        intent=None,
        confidence=None,
        slots={},
        missing_slots=[],
        decision=None,
        need_confirmation=False,
        risk_level=None,
        clarification_question=None,
        plan=[],
        market_data=None,
        news_sentiment=None,
        financial_analysis=None,
        technical_analysis=None,
        risk_analysis=None,
        final_report=None,
        agent_status={},
        tool_calls=[],
        observations=[],
        errors=[],
    )
