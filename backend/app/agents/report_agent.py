from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm import invoke_with_fallback
from app.graph.state import AgentState
from app.memory.memory_extractor import extract_preference_memory


EN_DISCLAIMER = "This report is for research purposes only and is not financial advice."
CN_DISCLAIMER = "本报告仅供研究参考，不构成任何投资建议。"


def _contains_chinese(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def _disclaimer(is_chinese: bool) -> str:
    return CN_DISCLAIMER if is_chinese else EN_DISCLAIMER


def _is_identity_question(text: str) -> bool:
    lowered = text.lower()
    patterns = [
        "你是谁",
        "你是啥",
        "你是什么",
        "你是什么模型",
        "what model",
        "who are you",
        "what are you",
    ]
    return any(pattern in lowered for pattern in patterns)


def _is_help_question(text: str) -> bool:
    lowered = text.lower()
    patterns = ["help", "帮助", "怎么用", "如何用", "能做什么", "可以做什么"]
    return any(pattern in lowered for pattern in patterns)


def _build_prompt_payload(state: AgentState) -> str:
    payload = {
        "market_data": state.get("market_data"),
        "news_sentiment": state.get("news_sentiment"),
        "financial_analysis": state.get("financial_analysis"),
        "technical_analysis": state.get("technical_analysis"),
        "risk_analysis": state.get("risk_analysis"),
        "user_working_memory": state.get("working_memory"),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _localize_text(value, is_chinese: bool) -> str:
    text = str(value if value not in (None, "") else "unknown")
    if not is_chinese:
        return text

    replacements = {
        "unknown": "未知",
        "Recent coverage is limited, so sentiment confidence is moderate.": "近期可用新闻有限，因此情绪判断的置信度适中。",
        "No major single-factor risk dominated the current dataset.": "当前数据里没有特别突出的单一主导风险。",
        "Financial coverage is incomplete, which lowers data confidence.": "财务数据覆盖不完整，降低了结论可信度。",
        "Technical momentum appears stretched with RSI above 70.": "RSI 高于 70，技术面存在一定过热风险。",
        "Valuation looks elevated based on trailing PE above 50.": "基于 trailing PE 高于 50，估值水平偏高。",
        "Recent headline sentiment is negative.": "近期新闻情绪偏负面。",
        "Recent price action shows elevated volatility.": "近期价格波动较大，波动风险上升。",
        "Data coverage remains imperfect, so conclusions should be treated cautiously.": "当前数据覆盖仍不完整，结论需要谨慎解读。",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def _localize_sentiment(value: str, is_chinese: bool) -> str:
    if not is_chinese:
        return str(value)
    mapping = {"positive": "偏正面", "negative": "偏负面", "neutral": "中性"}
    return mapping.get(str(value).lower(), str(value))


def _localize_impact(value: str, is_chinese: bool) -> str:
    if not is_chinese:
        return str(value)
    mapping = {"low": "低", "medium": "中", "high": "高"}
    return mapping.get(str(value).lower(), str(value))


def _localize_trend(value: str, is_chinese: bool) -> str:
    if not is_chinese:
        return str(value)
    mapping = {"uptrend": "上行趋势", "downtrend": "下行趋势", "mixed": "震荡整理"}
    return mapping.get(str(value).lower(), str(value))


def _localize_news_context(symbol: str, sentiment: str, impact: str, fallback: str, is_chinese: bool) -> str:
    if not is_chinese:
        return str(fallback)
    if "Mock headline flow" in str(fallback):
        sentiment_cn = _localize_sentiment(sentiment, True)
        impact_cn = _localize_impact(impact, True)
        return f"{symbol} 的模拟新闻流整体{sentiment_cn}，意味着新闻面对股价的影响程度{impact_cn}。"
    return _localize_text(fallback, True)


def _build_template_report(state: AgentState) -> str:
    user_input = state.get("user_input", "")
    is_chinese = _contains_chinese(user_input)
    disclaimer = _disclaimer(is_chinese)

    if state.get("decision") == "ask_clarification":
        if is_chinese:
            return "请补充缺失的信息后我再继续，比如股票代码、目标价格或你想看的分析重点。\n\n" + disclaimer
        return state.get("clarification_question") or "Please clarify the missing inputs so I can continue."
    if state.get("decision") == "unsupported":
        if is_chinese:
            return (
                "我现在可以帮你做美股分析、市场概览、新闻情绪、技术面、财务面和价格提醒。"
                "你也可以直接输入公司名或股票代码，比如“英伟达”或“Analyze NVDA”。\n\n"
                + disclaimer
            )
        return state.get("clarification_question") or "This request is outside the current CLI prototype scope."
    if state.get("intent") == "chat":
        if _is_identity_question(user_input):
            if is_chinese:
                return (
                    "我是 AnthroVest AI 的 CLI 多 Agent 原型。\n"
                    "当前这套系统会用 LangGraph 编排多个节点，比如 IntentAgent、SlotAgent、"
                    "MarketDataAgent、TechnicalAgent、RiskAgent 和 ReportAgent。\n"
                    "如果你没有配置 OpenRouter key，我主要通过规则逻辑、yfinance 数据和模板报告来运行；"
                    "如果配置了 OpenRouter，我会优先调用你在 `backend/.env` 里设置的模型，默认是 "
                    "`openrouter/free`，失败时再按 fallback 列表切换。\n\n"
                    f"{disclaimer}"
                )
            return (
                "I am the AnthroVest AI CLI multi-agent prototype. "
                "This system uses LangGraph to orchestrate agents such as IntentAgent, SlotAgent, "
                "MarketDataAgent, TechnicalAgent, RiskAgent, and ReportAgent. "
                "Without an OpenRouter key, I primarily run on rules, yfinance data, and template reports. "
                "With an OpenRouter key configured, I will try the model set in `backend/.env`, "
                "defaulting to `openrouter/free` with fallback models if needed.\n\n"
                f"{disclaimer}"
            )
        if _is_help_question(user_input):
            if is_chinese:
                return (
                    "你可以这样问我：\n"
                    "- 帮我分析一下英伟达\n"
                    "- 帮我分析一下 TSLA 最近怎么样，重点看技术面\n"
                    "- 看一下苹果的财务面\n"
                    "- 看一下特斯拉最近的新闻情绪\n"
                    "- 帮我设置 NVDA 价格高于 150 的提醒\n"
                    "- 记住，我更关注半导体和 AI 股票\n\n"
                    f"{disclaimer}"
                )
            return (
                "You can ask things like:\n"
                "- Analyze NVDA\n"
                "- Analyze TSLA and focus on technicals\n"
                "- Show me Apple's financial view\n"
                "- Summarize recent Tesla news sentiment\n"
                "- Create an alert for NVDA above 150\n"
                "- Remember that I focus on semiconductors and AI stocks\n\n"
                f"{disclaimer}"
            )
        remembered = extract_preference_memory(state.get("user_input", ""))
        if remembered:
            if is_chinese:
                return (
                    "记住了，我会把这条偏好写进后续研究上下文：\n"
                    f"- {remembered}\n\n"
                    f"{disclaimer}"
                )
            return (
                "Understood. I will keep this preference in working memory for future research context:\n"
                f"- {remembered}\n\n"
                f"{disclaimer}"
            )
        if is_chinese:
            return (
                "你好，我可以帮你做美股研究分析。你可以直接输入股票代码或公司名，"
                "比如“英伟达”、“TSLA”或者“帮我分析一下苹果”。\n\n"
                f"{disclaimer}"
            )
        return (
            "I can help with stock analysis, market overviews, news, technical signals, financial views, "
            "and alert setup in this CLI prototype.\n\n"
            f"{disclaimer}"
        )

    market = state.get("market_data") or {}
    news = state.get("news_sentiment") or {}
    financial = state.get("financial_analysis") or {}
    technical = state.get("technical_analysis") or {}
    risk = state.get("risk_analysis") or {}
    symbol = state.get("slots", {}).get("symbol") or "the requested asset"

    if is_chinese:
        risk_items = risk.get("main_risks", ["Data coverage remains imperfect, so conclusions should be treated cautiously."])
        lines = [
            "1. 执行摘要",
            f"{symbol} 当前呈现出一个相对克制、可研究的观察框架。以下结论综合了行情、新闻、财务和技术信号，仅用于研究参考，不构成任何买卖指令。",
            "",
            "2. 市场快照",
            f"当前价格：{_localize_text(market.get('current_price', 'unknown'), True)}。前收盘价：{_localize_text(market.get('previous_close', 'unknown'), True)}。涨跌幅：{_localize_text(market.get('change_percent', 'unknown'), True)}%。成交量：{_localize_text(market.get('volume', 'unknown'), True)}。",
            "",
            "3. 新闻与情绪",
            f"整体情绪为{_localize_sentiment(news.get('overall_sentiment', 'neutral'), True)}，影响等级为{_localize_impact(news.get('impact_level', 'medium'), True)}。补充说明：{_localize_news_context(symbol, str(news.get('overall_sentiment', 'neutral')), str(news.get('impact_level', 'medium')), news.get('risk_summary', 'Recent coverage is limited, so sentiment confidence is moderate.'), True)}",
            "",
            "4. 财务视角",
            f"Trailing PE：{_localize_text(financial.get('trailingPE', 'unknown'), True)}，Forward PE：{_localize_text(financial.get('forwardPE', 'unknown'), True)}，EPS：{_localize_text(financial.get('eps', 'unknown'), True)}，营收增速：{_localize_text(financial.get('revenueGrowth', 'unknown'), True)}。",
            "",
            "5. 技术信号",
            f"MA5：{_localize_text(technical.get('ma5', 'unknown'), True)}，MA20：{_localize_text(technical.get('ma20', 'unknown'), True)}，MA60：{_localize_text(technical.get('ma60', 'unknown'), True)}，RSI：{_localize_text(technical.get('rsi', 'unknown'), True)}，趋势：{_localize_trend(technical.get('trend', 'unknown'), True)}。",
            "",
            "6. 关键风险",
            *[f"- {_localize_text(item, True)}" for item in risk_items],
            "",
            "7. 最终结论",
            "当前更适合把这只股票视为一个需要持续跟踪的研究对象，而不是直接给出交易结论。解读时仍需结合数据缺口、新闻变化速度以及你自己的研究判断。",
            "",
            disclaimer,
        ]
    else:
        lines = [
            "1. Executive Summary",
            f"{symbol} shows a measured research setup based on the available market, news, financial, and technical inputs. This summary stays descriptive and avoids directional investment calls.",
            "",
            "2. Market Snapshot",
            f"Current price: {market.get('current_price', 'unknown')}. Previous close: {market.get('previous_close', 'unknown')}. Change: {market.get('change_percent', 'unknown')}%. Volume: {market.get('volume', 'unknown')}.",
            "",
            "3. News & Sentiment",
            f"Overall sentiment is {news.get('overall_sentiment', 'neutral')} with impact level {news.get('impact_level', 'medium')}. Key context: {news.get('risk_summary', 'Recent coverage is limited, so sentiment confidence is moderate.')}",
            "",
            "4. Financial View",
            f"Trailing PE: {financial.get('trailingPE', 'unknown')}, Forward PE: {financial.get('forwardPE', 'unknown')}, EPS: {financial.get('eps', 'unknown')}, Revenue growth: {financial.get('revenueGrowth', 'unknown')}.",
            "",
            "5. Technical Signals",
            f"MA5: {technical.get('ma5', 'unknown')}, MA20: {technical.get('ma20', 'unknown')}, MA60: {technical.get('ma60', 'unknown')}, RSI: {technical.get('rsi', 'unknown')}, Trend: {technical.get('trend', 'unknown')}.",
            "",
            "6. Key Risks",
            *[f"- {item}" for item in risk.get("main_risks", ["Data coverage remains imperfect, so conclusions should be treated cautiously."])],
            "",
            "7. Final Takeaway",
            "The current picture suggests a balanced research view rather than a trading instruction. Any interpretation should account for data gaps, fast-changing headlines, and the user's own diligence.",
            "",
            disclaimer,
        ]
    return "\n".join(lines)


def run_report_agent(state: AgentState) -> AgentState:
    print("[ReportAgent] running...")
    next_state = state.copy()
    next_state["agent_status"]["ReportAgent"] = "running"
    is_chinese = _contains_chinese(next_state.get("user_input", ""))
    disclaimer = _disclaimer(is_chinese)

    report_text = None
    if next_state.get("decision") == "execute":
        messages = [
            SystemMessage(
                content=(
                    "You are AnthroVest AI's ReportAgent, a U.S. equity research report generation agent.\n"
                    "You are not an investment advisor and you do not provide buy or sell recommendations.\n"
                    "Your task is to read structured outputs from multiple agents and produce a clear, restrained, professional research report.\n\n"
                    "Input includes:\n"
                    "- market_data\n"
                    "- news_sentiment\n"
                    "- financial_analysis\n"
                    "- technical_analysis\n"
                    "- risk_analysis\n"
                    "- user working_memory\n\n"
                    "Write a structured report with these sections:\n"
                    "1. Executive Summary\n"
                    "2. Market Snapshot\n"
                    "3. News & Sentiment\n"
                    "4. Financial View\n"
                    "5. Technical Signals\n"
                    "6. Key Risks\n"
                    "7. Final Takeaway\n\n"
                    "Style:\n"
                    "- Calm, concise, professional\n"
                    "- Similar to a research assistant\n"
                    "- No hype\n"
                    "- No guaranteed returns\n"
                    "- No direct buy/sell recommendation\n"
                    "- Mention data quality limitations when data is missing\n"
                    f"- Write the report in {'Chinese' if is_chinese else 'English'} to match the user's language\n"
                    f"- End with: {disclaimer}"
                )
            ),
            HumanMessage(content=_build_prompt_payload(next_state)),
        ]
        report_text = invoke_with_fallback(messages, purpose="report_generation")

    if not report_text:
        report_text = _build_template_report(next_state)

    if disclaimer not in report_text:
        report_text = report_text.rstrip() + "\n\n" + disclaimer

    next_state["final_report"] = report_text
    next_state["agent_status"]["ReportAgent"] = "completed"
    next_state["observations"].append({"agent": "ReportAgent", "summary": "Final report prepared."})
    print("[ReportAgent] completed")
    return next_state
