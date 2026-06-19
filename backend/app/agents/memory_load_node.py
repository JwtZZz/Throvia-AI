from __future__ import annotations

from app.graph.state import AgentState
from app.memory.history_store import load_recent_history
from app.memory.memory_store import load_long_term_memory


def run_memory_load_node(state: AgentState) -> AgentState:
    print("[MemoryLoadNode] loading memory...")
    next_state = state.copy()
    next_state["agent_status"]["MemoryLoadNode"] = "running"

    long_term_memory = load_long_term_memory()
    retrieved_history = load_recent_history(limit=5)
    retrieved_knowledge = [
        {
            "source": "knowledge_base",
            "topic": "research_principles",
            "content": "AnthroVest AI produces research-oriented analysis and avoids direct buy or sell advice.",
        },
        {
            "source": "knowledge_base",
            "topic": "data_quality",
            "content": "When live data is missing or incomplete, agents should clearly mention the limitation and use cautious fallback logic.",
        },
    ]

    preference_notes = [item["content"] for item in long_term_memory if item.get("type") == "preference"]
    next_state["long_term_memory"] = long_term_memory
    next_state["retrieved_history"] = retrieved_history
    next_state["retrieved_knowledge"] = retrieved_knowledge
    next_state["working_memory"]["user_preferences"] = preference_notes
    next_state["agent_status"]["MemoryLoadNode"] = "completed"
    next_state["observations"].append(
        {
            "agent": "MemoryLoadNode",
            "memory_items": len(long_term_memory),
            "history_items": len(retrieved_history),
        }
    )
    return next_state
