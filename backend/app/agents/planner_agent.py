from __future__ import annotations

from app.graph.state import AgentState


def _stock_analysis_plan() -> list[dict]:
    return [
        {"step": 1, "agent": "MarketDataAgent", "task": "Fetch stock quote and historical prices"},
        {"step": 2, "agent": "NewsSentimentAgent", "task": "Collect and summarize recent news"},
        {"step": 3, "agent": "FinancialAgent", "task": "Analyze basic financial metrics"},
        {"step": 4, "agent": "TechnicalAgent", "task": "Calculate technical indicators"},
        {"step": 5, "agent": "RiskAgent", "task": "Evaluate major risks"},
        {"step": 6, "agent": "ReportAgent", "task": "Generate final research report"},
    ]


def run_planner_agent(state: AgentState) -> AgentState:
    next_state = state.copy()
    next_state["agent_status"]["PlannerAgent"] = "running"

    intent = next_state.get("intent")
    if intent in {"stock_analysis", "financial_report", "technical_analysis", "news_search"}:
        plan = _stock_analysis_plan()
    elif intent == "market_overview":
        plan = [
            {"step": 1, "agent": "MarketDataAgent", "task": "Fetch market proxy data"},
            {"step": 2, "agent": "NewsSentimentAgent", "task": "Summarize broad market sentiment"},
            {"step": 3, "agent": "RiskAgent", "task": "Highlight macro risk signals"},
            {"step": 4, "agent": "ReportAgent", "task": "Generate market overview report"},
        ]
    elif intent == "create_alert":
        plan = [
            {"step": 1, "agent": "MarketDataAgent", "task": "Fetch current price for the target symbol"},
            {"step": 2, "agent": "RiskAgent", "task": "Assess market volatility around the alert setup"},
            {"step": 3, "agent": "ReportAgent", "task": "Summarize alert setup and caveats"},
        ]
    else:
        plan = []

    next_state["plan"] = plan
    next_state["agent_status"]["PlannerAgent"] = "completed"
    next_state["observations"].append({"agent": "PlannerAgent", "steps": len(plan)})
    print(f"[PlannerAgent] {len(plan)} steps planned")
    return next_state
