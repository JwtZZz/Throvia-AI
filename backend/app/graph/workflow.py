from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agents.decision_agent import run_decision_agent
from app.agents.financial_agent import run_financial_agent
from app.agents.intent_agent import run_intent_agent
from app.agents.market_data_agent import run_market_data_agent
from app.agents.memory_load_node import run_memory_load_node
from app.agents.memory_write_node import run_memory_write_node
from app.agents.news_sentiment_agent import run_news_sentiment_agent
from app.agents.planner_agent import run_planner_agent
from app.agents.report_agent import run_report_agent
from app.agents.risk_agent import run_risk_agent
from app.agents.slot_agent import run_slot_agent
from app.agents.technical_agent import run_technical_agent
from app.graph.state import AgentState


def _route_from_decision(state: AgentState) -> str:
    return "planner" if state.get("decision") == "execute" else "report"


def build_workflow():
    graph = StateGraph(AgentState)

    graph.add_node("memory_load", run_memory_load_node)
    graph.add_node("intent", run_intent_agent)
    graph.add_node("slot", run_slot_agent)
    graph.add_node("decision", run_decision_agent)
    graph.add_node("planner", run_planner_agent)
    graph.add_node("market_data", run_market_data_agent)
    graph.add_node("news_sentiment", run_news_sentiment_agent)
    graph.add_node("financial", run_financial_agent)
    graph.add_node("technical", run_technical_agent)
    graph.add_node("risk", run_risk_agent)
    graph.add_node("report", run_report_agent)
    graph.add_node("memory_write", run_memory_write_node)

    graph.set_entry_point("memory_load")
    graph.add_edge("memory_load", "intent")
    graph.add_edge("intent", "slot")
    graph.add_edge("slot", "decision")
    graph.add_conditional_edges(
        "decision",
        _route_from_decision,
        {
            "planner": "planner",
            "report": "report",
        },
    )
    graph.add_edge("planner", "market_data")
    graph.add_edge("market_data", "news_sentiment")
    graph.add_edge("news_sentiment", "financial")
    graph.add_edge("financial", "technical")
    graph.add_edge("technical", "risk")
    graph.add_edge("risk", "report")
    graph.add_edge("report", "memory_write")
    graph.add_edge("memory_write", END)

    return graph.compile()
