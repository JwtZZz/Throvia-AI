from __future__ import annotations

from app.graph.state import AgentState


def run_decision_agent(state: AgentState) -> AgentState:
    next_state = state.copy()
    next_state["agent_status"]["DecisionAgent"] = "running"

    intent = next_state.get("intent")
    slots = next_state.get("slots", {})
    missing_slots: list[str] = []
    decision = "execute"
    need_confirmation = False
    clarification_question = None

    if intent == "stock_analysis" and not slots.get("symbol"):
        missing_slots.append("symbol")
        decision = "ask_clarification"
        clarification_question = "Which stock symbol would you like me to analyze?"
    elif intent == "create_alert":
        if not slots.get("symbol"):
            missing_slots.append("symbol")
        if slots.get("target_price") is None:
            missing_slots.append("target_price")
        if missing_slots:
            decision = "ask_clarification"
            clarification_question = "Please tell me the stock symbol and target price for the alert."
        need_confirmation = True
    elif intent == "unsupported":
        decision = "unsupported"
        clarification_question = "I can help with stock analysis, market overview, news, technicals, financials, or alerts."
    elif intent == "chat":
        decision = "respond"

    next_state["missing_slots"] = missing_slots
    next_state["decision"] = decision
    next_state["need_confirmation"] = need_confirmation
    next_state["clarification_question"] = clarification_question
    next_state["agent_status"]["DecisionAgent"] = "completed"
    next_state["observations"].append(
        {
            "agent": "DecisionAgent",
            "decision": decision,
            "missing_slots": missing_slots,
        }
    )
    print("[DecisionAgent] decision = " + decision)
    return next_state
