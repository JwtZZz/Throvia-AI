from __future__ import annotations

from typing import Any, Dict


def build_mock_news_sentiment(symbol: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
    change_percent = float(market_data.get("change_percent", 0) or 0)

    if change_percent > 2:
        overall_sentiment = "positive"
        impact_level = "medium"
    elif change_percent < -2:
        overall_sentiment = "negative"
        impact_level = "medium"
    else:
        overall_sentiment = "neutral"
        impact_level = "low"

    items = [
        {
            "headline": f"{symbol} remains in focus as investors reassess near-term demand signals.",
            "sentiment": overall_sentiment,
            "summary": "Market participants are weighing recent price action against still-evolving macro conditions.",
        },
        {
            "headline": f"Analysts debate whether {symbol} can sustain current expectations.",
            "sentiment": "neutral" if overall_sentiment == "positive" else overall_sentiment,
            "summary": "Commentary is mixed, with attention on execution quality and valuation discipline.",
        },
        {
            "headline": f"{symbol} trading narrative stays sensitive to AI and semiconductor positioning.",
            "sentiment": "neutral",
            "summary": "Sector leadership remains important, but narrative momentum could shift quickly with new data.",
        },
    ]

    risk_summary = (
        f"Mock headline flow for {symbol} is {overall_sentiment}, suggesting {impact_level} headline pressure."
    )
    return {
        "overall_sentiment": overall_sentiment,
        "impact_level": impact_level,
        "items": items,
        "risk_summary": risk_summary,
    }
