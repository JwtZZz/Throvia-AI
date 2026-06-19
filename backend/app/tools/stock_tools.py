from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Tuple

import pandas as pd
import yfinance as yf


PERIOD_MAP = {
    "1d": "1d",
    "5d": "5d",
    "1mo": "1mo",
    "6mo": "6mo",
}


def _mock_history(symbol: str, time_range: str) -> pd.DataFrame:
    end = datetime.now(timezone.utc)
    periods = {"1d": 24, "5d": 5, "1mo": 22, "6mo": 132}.get(time_range, 22)
    rows = []
    base = 120.0 + (sum(ord(ch) for ch in symbol) % 90)
    for index in range(periods):
        timestamp = end - timedelta(days=periods - index)
        close = base + (index * 0.8) - ((index % 5) * 0.4)
        rows.append(
            {
                "Date": timestamp,
                "Open": round(close - 0.8, 2),
                "High": round(close + 1.2, 2),
                "Low": round(close - 1.5, 2),
                "Close": round(close, 2),
                "Volume": 1000000 + (index * 25000),
            }
        )
    frame = pd.DataFrame(rows)
    return frame


def _normalize_history(history: pd.DataFrame) -> list[dict[str, Any]]:
    if history.empty:
        return []
    frame = history.reset_index()
    if "Datetime" in frame.columns:
        frame["Date"] = frame["Datetime"]
    frame["Date"] = frame["Date"].astype(str)
    return frame[["Date", "Open", "High", "Low", "Close", "Volume"]].to_dict("records")


def fetch_price_history_only(symbol: str, time_range: str) -> pd.DataFrame:
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=PERIOD_MAP.get(time_range, "1mo"), auto_adjust=False)
        if history is None or history.empty:
            return _mock_history(symbol, time_range)
        return history
    except Exception:
        return _mock_history(symbol, time_range)


def fetch_market_data(symbol: str, time_range: str) -> Tuple[Dict[str, Any], str, bool]:
    used_fallback = False
    notes = "Loaded live market data."
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
        history = ticker.history(period=PERIOD_MAP.get(time_range, "1mo"), auto_adjust=False)
        if history is None or history.empty:
            raise ValueError("No history returned from yfinance")

        current_price = float(history["Close"].iloc[-1])
        previous_close = float(history["Close"].iloc[-2]) if len(history) > 1 else current_price
        change_percent = round(((current_price - previous_close) / previous_close) * 100, 2) if previous_close else 0.0
        market_data = {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "previous_close": round(previous_close, 2),
            "change_percent": change_percent,
            "volume": int(history["Volume"].iloc[-1]) if "Volume" in history else "unknown",
            "market_cap": info.get("marketCap", "unknown"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh", "unknown"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow", "unknown"),
            "historical_prices": _normalize_history(history),
        }
        return market_data, notes, used_fallback
    except Exception as exc:  # pragma: no cover - external API failure path
        used_fallback = True
        notes = f"Used mock market data due to yfinance issue: {exc}"
        history = _mock_history(symbol, time_range)
        current_price = float(history["Close"].iloc[-1])
        previous_close = float(history["Close"].iloc[-2]) if len(history) > 1 else current_price
        change_percent = round(((current_price - previous_close) / previous_close) * 100, 2) if previous_close else 0.0
        market_data = {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "previous_close": round(previous_close, 2),
            "change_percent": change_percent,
            "volume": int(history["Volume"].iloc[-1]),
            "market_cap": "unknown",
            "fifty_two_week_high": round(current_price * 1.18, 2),
            "fifty_two_week_low": round(current_price * 0.78, 2),
            "historical_prices": _normalize_history(history),
        }
        return market_data, notes, used_fallback


def fetch_financial_data(symbol: str) -> Tuple[Dict[str, Any], str]:
    notes = "Loaded financial fields from yfinance."
    try:
        info = yf.Ticker(symbol).info or {}
    except Exception as exc:  # pragma: no cover - external API failure path
        info = {}
        notes = f"Used partial fallback financial fields due to yfinance issue: {exc}"

    def _value(name: str):
        value = info.get(name)
        return "unknown" if value in (None, "") else value

    analysis = {
        "symbol": symbol,
        "trailingPE": _value("trailingPE"),
        "forwardPE": _value("forwardPE"),
        "eps": _value("trailingEps"),
        "revenueGrowth": _value("revenueGrowth"),
        "profitMargins": _value("profitMargins"),
        "freeCashflow": _value("freeCashflow"),
        "debtToEquity": _value("debtToEquity"),
    }
    return analysis, notes
