from __future__ import annotations

import pandas as pd

from app.graph.state import AgentState
from app.tools.stock_tools import fetch_price_history_only
from app.tools.technical_tools import compute_technical_indicators


def run_technical_agent(state: AgentState) -> AgentState:
    print("[TechnicalAgent] running...")
    next_state = state.copy()
    next_state["agent_status"]["TechnicalAgent"] = "running"

    symbol = next_state.get("slots", {}).get("symbol") or "SPY"
    historical_prices = (next_state.get("market_data") or {}).get("historical_prices") or []

    if historical_prices:
        frame = pd.DataFrame(historical_prices)
    else:
        frame = fetch_price_history_only(symbol=symbol, time_range=next_state.get("slots", {}).get("time_range") or "1mo")
        next_state["errors"].append(f"TechnicalAgent re-fetched history for {symbol} because market data history was missing.")

    next_state["technical_analysis"] = compute_technical_indicators(frame)
    next_state["observations"].append(
        {
            "agent": "TechnicalAgent",
            "summary": next_state["technical_analysis"].get("summary"),
        }
    )
    next_state["agent_status"]["TechnicalAgent"] = "completed"
    print("[TechnicalAgent] completed")
    return next_state
