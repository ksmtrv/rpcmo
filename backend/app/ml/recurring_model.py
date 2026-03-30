"""
ML-модель предсказания регулярности транзакций.
Использует RandomForest на признаках: количество, стабильность суммы, регулярность интервалов.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier


def _extract_features(
    count: int,
    amounts: list[float],
    intervals: list[float],
    desc_length: int,
    has_counterparty: bool,
) -> np.ndarray:
    """Извлечь признаки из группы транзакций."""
    amount_arr = np.array(amounts)
    interval_arr = np.array(intervals) if intervals else np.array([30.0])

    amount_std = float(np.std(amount_arr)) if len(amount_arr) > 1 else 0.0
    amount_cv = amount_std / (np.mean(amount_arr) + 1e-6)  # coefficient of variation
    interval_std = float(np.std(interval_arr)) if len(interval_arr) > 1 else 0.0
    interval_mean = float(np.mean(interval_arr))
    # Регулярность: низкий std при ~30 днях = месячный паттерн
    is_monthly_interval = 25 <= interval_mean <= 35
    interval_regularity = 1.0 - min(interval_std / 10.0, 1.0) if is_monthly_interval else 0.0

    return np.array([[
        count,
        np.log1p(np.mean(np.abs(amount_arr))),
        amount_cv,
        interval_mean,
        interval_std,
        interval_regularity,
        min(desc_length / 50.0, 1.0),
        1.0 if has_counterparty else 0.0,
    ]])


def _generate_training_data() -> tuple[np.ndarray, np.ndarray]:
    """Синтетические данные для обучения (регулярные vs нерегулярные)."""
    X_list, y_list = [], []

    # Положительные: 3+ транзакций, стабильная сумма, регулярные интервалы
    for _ in range(80):
        count = np.random.randint(3, 8)
        amount = np.random.uniform(500, 15000)
        amounts = [amount + np.random.normal(0, amount * 0.02) for _ in range(count)]
        intervals = [30 + np.random.normal(0, 2) for _ in range(count - 1)]
        X_list.append(_extract_features(count, amounts, intervals, 20, True))
        y_list.append(1)

    # Отрицательные: 1-2 транзакции или нерегулярные
    for _ in range(80):
        count = np.random.randint(1, 3)
        amounts = list(np.random.uniform(500, 20000, count))
        intervals = [np.random.uniform(5, 60) for _ in range(max(0, count - 1))]
        X_list.append(_extract_features(count, amounts, intervals, 10, np.random.random() > 0.5))
        y_list.append(0)

    # Отрицательные: нестабильная сумма
    for _ in range(40):
        count = 4
        amounts = list(np.random.uniform(1000, 10000, count))  # разные суммы
        intervals = [30] * (count - 1)
        X_list.append(_extract_features(count, amounts, intervals, 15, True))
        y_list.append(0)

    X = np.vstack(X_list)
    y = np.array(y_list)
    return X, y


class RecurringPredictor:
    """Классификатор регулярности по группе транзакций."""

    def __init__(self):
        self._model = RandomForestClassifier(n_estimators=50, max_depth=6, random_state=42)
        X, y = _generate_training_data()
        self._model.fit(X, y)

    def predict_proba(
        self,
        count: int,
        amounts: list[float],
        intervals: list[float],
        desc_length: int = 0,
        has_counterparty: bool = False,
    ) -> float:
        """Вероятность того, что группа — регулярный платёж (0..1)."""
        if count < 2:
            return 0.0
        X = _extract_features(count, amounts, intervals, desc_length, has_counterparty)
        proba = self._model.predict_proba(X)[0, 1]
        return float(proba)


# Синглтон для переиспользования
_predictor: RecurringPredictor | None = None


def get_recurring_predictor() -> RecurringPredictor:
    global _predictor
    if _predictor is None:
        _predictor = RecurringPredictor()
    return _predictor
