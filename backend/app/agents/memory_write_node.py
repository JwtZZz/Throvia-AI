from __future__ import annotations

from datetime import datetime, timezone

from app.graph.state import AgentState
from app.memory.history_store import append_history_entry
from app.memory.memory_extractor import extract_preference_memory
from app.memory.memory_store import append_long_term_memory


def run_memory_write_node(state: AgentState) -> AgentState:
    next_state = state.copy()
    next_state["agent_status"]["MemoryWriteNode"] = "running"

    extracted_memory = extract_preference_memory(next_state["user_input"])
    if extracted_memory:
        append_long_term_memory(
            {
                "type": "preference",
                "content": extracted_memory,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    append_history_entry(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": next_state["session_id"],
            "user_input": next_state["user_input"],
            "intent": next_state.get("intent"),
            "slots": next_state.get("slots"),
            "plan": next_state.get("plan"),
            "market_data": next_state.get("market_data"),
            "news_sentiment": next_state.get("news_sentiment"),
            "financial_analysis": next_state.get("financial_analysis"),
            "technical_analysis": next_state.get("technical_analysis"),
            "risk_analysis": next_state.get("risk_analysis"),
            "final_report": next_state.get("final_report"),
            "tool_calls": next_state.get("tool_calls"),
            "observations": next_state.get("observations"),
            "agent_status": next_state.get("agent_status"),
            "errors": next_state.get("errors"),
        }
    )

    next_state["agent_status"]["MemoryWriteNode"] = "completed"
    print("[MemoryWriteNode] saved run history")
    return next_state
