from __future__ import annotations

from app.graph.state import AgentState
from app.tools.mock_news_tools import build_mock_news_sentiment


def run_news_sentiment_agent(state: AgentState) -> AgentState:
    print("[NewsSentimentAgent] running...")
    next_state = state.copy()
    next_state["agent_status"]["NewsSentimentAgent"] = "running"

    symbol = next_state.get("slots", {}).get("symbol") or "MARKET"
    market_data = next_state.get("market_data") or {}
    next_state["news_sentiment"] = build_mock_news_sentiment(symbol, market_data)
    next_state["observations"].append(
        {
            "agent": "NewsSentimentAgent",
            "summary": next_state["news_sentiment"]["risk_summary"],
        }
    )
    next_state["agent_status"]["NewsSentimentAgent"] = "completed"
    print("[NewsSentimentAgent] completed")
    return next_state
