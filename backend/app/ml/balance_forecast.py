"""
ML-прогноз баланса на основе временных рядов.
Использует Exponential Smoothing (Holt) для учёта тренда.
"""

from datetime import date, timedelta

import numpy as np
import pandas as pd

try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
except ImportError:
    ExponentialSmoothing = None


def _build_daily_balance_series(
    dates: list[date], amounts: list[float], directions: list[str]
) -> pd.Series:
    """Построить ряд дневных балансов из транзакций."""
    if not dates:
        return pd.Series(dtype=float)

    df = pd.DataFrame({
        "date": pd.to_datetime(dates),
        "amount": amounts,
        "direction": directions,
    })
    df["signed"] = df.apply(lambda r: r["amount"] if r["direction"] == "in" else -r["amount"], axis=1)
    daily = df.groupby("date")["signed"].sum()
    # Кумулятивная сумма
    daily = daily.sort_index()
    balance = daily.cumsum()
    return balance


def forecast_balance_ml(
    dates: list[date],
    amounts: list[float],
    directions: list[str],
    base_balance: float,
    days_ahead: int = 14,
) -> list[tuple[date, float]]:
    """
    Прогноз баланса на N дней вперёд.
    Возвращает список (дата, прогноз_баланса).
    """
    if ExponentialSmoothing is None:
        return []

    balance_series = _build_daily_balance_series(dates, amounts, directions)
    if len(balance_series) < 5:
        return []

    today = pd.Timestamp(date.today())
    last_date = balance_series.index.max()
    if last_date < today:
        balance_series = pd.concat([
            balance_series,
            pd.Series({today: base_balance}),
        ]).sort_index()
    else:
        balance_series = balance_series.copy()
        balance_series.iloc[-1] = base_balance

    start = balance_series.index.min()
    end = balance_series.index.max()
    full_range = pd.date_range(start=start, end=end, freq="D")
    balance_filled = balance_series.reindex(full_range).ffill().bfill()

    try:
        model = ExponentialSmoothing(
            balance_filled,
            trend="add",
            seasonal=None,
            initialization_method="estimated",
        )
        fitted = model.fit(optimized=True)
        forecast = fitted.forecast(steps=days_ahead)
    except Exception:
        return []

    result = []
    for i in range(min(days_ahead, len(forecast))):
        d = date.today() + timedelta(days=i)
        result.append((d, float(forecast.iloc[i])))
    return result


def get_balance_trend(dates: list[date], amounts: list[float], directions: list[str]) -> float:
    """
    Оценка тренда баланса (руб/день). Положительный = рост.
    """
    balance_series = _build_daily_balance_series(dates, amounts, directions)
    if len(balance_series) < 3:
        return 0.0
    x = np.arange(len(balance_series))
    y = balance_series.values.astype(float)
    slope = np.polyfit(x, y, 1)[0]
    return float(slope)
