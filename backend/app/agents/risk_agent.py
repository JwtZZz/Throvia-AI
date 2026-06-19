from __future__ import annotations

from typing import List, Optional

from app.graph.state import AgentState


def _safe_float(value) -> Optional[float]:
    try:
        if value in {None, "unknown"}:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def run_risk_agent(state: AgentState) -> AgentState:
    print("[RiskAgent] running...")
    next_state = state.copy()
    next_state["agent_status"]["RiskAgent"] = "running"

    market = next_state.get("market_data") or {}
    news = next_state.get("news_sentiment") or {}
    financial = next_state.get("financial_analysis") or {}
    technical = next_state.get("technical_analysis") or {}

    score = 20
    main_risks: List[str] = []

    rsi = _safe_float(technical.get("rsi"))
    trailing_pe = _safe_float(financial.get("trailingPE"))
    change_percent = _safe_float(market.get("change_percent"))
    overall_sentiment = str(news.get("overall_sentiment", "neutral")).lower()

    if rsi is not None and rsi > 70:
        score += 18
        main_risks.append("Technical momentum appears stretched with RSI above 70.")

    if trailing_pe is not None and trailing_pe > 50:
        score += 18
        main_risks.append("Valuation looks elevated based on trailing PE above 50.")

    if overall_sentiment == "negative":
        score += 15
        main_risks.append("Recent headline sentiment is negative.")

    if change_percent is not None and abs(change_percent) > 5:
        score += 15
        main_risks.append("Recent price action shows elevated volatility.")

    unknown_fields = sum(1 for value in financial.values() if value == "unknown")
    if unknown_fields >= 3:
        score += 12
        main_risks.append("Financial coverage is incomplete, which lowers data confidence.")

    score = max(0, min(score, 100))
    risk_level = "low" if score < 35 else "medium" if score < 65 else "high"

    if not main_risks:
        main_risks.append("No major single-factor risk dominated the current dataset.")

    risk_summary = (
        f"Current risk appears {risk_level} with a score of {score}/100, driven by "
        + "; ".join(main_risks)
    )

    next_state["risk_level"] = risk_level
    next_state["risk_analysis"] = {
        "risk_level": risk_level,
        "risk_score": score,
        "main_risks": main_risks,
        "risk_summary": risk_summary,
    }
    next_state["observations"].append({"agent": "RiskAgent", "summary": risk_summary})
    next_state["agent_status"]["RiskAgent"] = "completed"
    print("[RiskAgent] completed")
    return next_state
