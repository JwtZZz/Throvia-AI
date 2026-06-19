from __future__ import annotations

from typing import Any, Dict, Union

import numpy as np
import pandas as pd


def _to_float_or_unknown(value: Any) -> Union[float, str]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "unknown"
    return round(float(value), 2)


def _compute_rsi(close_series: pd.Series, window: int = 14) -> pd.Series:
    delta = close_series.diff()
    gain = delta.clip(lower=0).rolling(window=window).mean()
    loss = (-delta.clip(upper=0)).rolling(window=window).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def compute_technical_indicators(history: pd.DataFrame) -> Dict[str, Any]:
    if history is None or history.empty or "Close" not in history:
        return {
            "ma5": "unknown",
            "ma20": "unknown",
            "ma60": "unknown",
            "rsi": "unknown",
            "volume_ratio": "unknown",
            "trend": "unknown",
            "summary": "Technical history was unavailable, so indicators could not be computed reliably.",
        }

    frame = history.copy()
    frame["Close"] = pd.to_numeric(frame["Close"], errors="coerce")
    frame["Volume"] = pd.to_numeric(frame.get("Volume"), errors="coerce")
    frame = frame.dropna(subset=["Close"])

    frame["ma5"] = frame["Close"].rolling(window=5).mean()
    frame["ma20"] = frame["Close"].rolling(window=20).mean()
    frame["ma60"] = frame["Close"].rolling(window=60).mean()
    frame["rsi"] = _compute_rsi(frame["Close"])
    frame["avg_volume_20"] = frame["Volume"].rolling(window=20).mean()

    latest = frame.iloc[-1]
    volume_ratio = (
        latest["Volume"] / latest["avg_volume_20"]
        if latest.get("avg_volume_20") not in (0, None) and not np.isnan(latest.get("avg_volume_20", np.nan))
        else np.nan
    )

    if latest["Close"] > latest.get("ma20", np.nan) > latest.get("ma60", np.nan):
        trend = "uptrend"
    elif latest["Close"] < latest.get("ma20", np.nan) < latest.get("ma60", np.nan):
        trend = "downtrend"
    else:
        trend = "mixed"

    summary = (
        f"Trend looks {trend}; MA5={_to_float_or_unknown(latest.get('ma5'))}, "
        f"MA20={_to_float_or_unknown(latest.get('ma20'))}, RSI={_to_float_or_unknown(latest.get('rsi'))}."
    )

    return {
        "ma5": _to_float_or_unknown(latest.get("ma5")),
        "ma20": _to_float_or_unknown(latest.get("ma20")),
        "ma60": _to_float_or_unknown(latest.get("ma60")),
        "rsi": _to_float_or_unknown(latest.get("rsi")),
        "volume_ratio": _to_float_or_unknown(volume_ratio),
        "trend": trend,
        "summary": summary,
    }
