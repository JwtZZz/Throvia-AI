from __future__ import annotations

from app.graph.state import AgentState
from app.tools.stock_tools import fetch_financial_data


def run_financial_agent(state: AgentState) -> AgentState:
    print("[FinancialAgent] running...")
    next_state = state.copy()
    next_state["agent_status"]["FinancialAgent"] = "running"

    symbol = next_state.get("slots", {}).get("symbol") or "SPY"
    financial_analysis, notes = fetch_financial_data(symbol)
    next_state["financial_analysis"] = financial_analysis
    next_state["tool_calls"].append(
        {
            "agent": "FinancialAgent",
            "tool": "yfinance",
            "symbol": symbol,
        }
    )
    if notes:
        next_state["observations"].append({"agent": "FinancialAgent", "summary": notes})
    next_state["agent_status"]["FinancialAgent"] = "completed"
    print("[FinancialAgent] completed")
    return next_state
