from __future__ import annotations

from app.graph.state import AgentState
from app.tools.stock_tools import fetch_market_data


def run_market_data_agent(state: AgentState) -> AgentState:
    print("[MarketDataAgent] running...")
    next_state = state.copy()
    next_state["agent_status"]["MarketDataAgent"] = "running"

    symbol = next_state.get("slots", {}).get("symbol") or "SPY"
    time_range = next_state.get("slots", {}).get("time_range") or "1mo"
    market_data, notes, used_fallback = fetch_market_data(symbol=symbol, time_range=time_range)

    next_state["market_data"] = market_data
    next_state["tool_calls"].append(
        {
            "agent": "MarketDataAgent",
            "tool": "yfinance",
            "symbol": symbol,
            "time_range": time_range,
            "used_fallback": used_fallback,
        }
    )
    next_state["observations"].append(
        {
            "agent": "MarketDataAgent",
            "summary": notes,
        }
    )
    if used_fallback:
        next_state["errors"].append(f"MarketDataAgent used fallback market data for {symbol}.")

    next_state["agent_status"]["MarketDataAgent"] = "completed"
    print("[MarketDataAgent] completed")
    return next_state
