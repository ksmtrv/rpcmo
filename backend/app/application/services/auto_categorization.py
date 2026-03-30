"""
Авто-категоризация по ключевым словам в назначении и контрагенте.
Похожие назначения (продукты, обед, еда, кафе) → одна категория.
"""

# (ключевые слова, название категории, тип: expense/income)
DEFAULT_KEYWORDS: list[tuple[list[str], str, str]] = [
    # Расходы
    (["продукты", "обед", "еда", "кафе", "магнит", "пятерочка", "перекус", "ресторан"], "Продукты и питание", "expense"),
    (["транспорт", "такси", "бензин", "заправка", "яндекс такси"], "Транспорт", "expense"),
    (["связь", "интернет", "мтс", "ростелеком", "билайн", "мегафон", "телефон"], "Связь и интернет", "expense"),
    (["аренда", "арендодатель"], "Аренда", "expense"),
    (["подписка", "яндекс плюс", "нетология", "курсы", "обучение"], "Подписки и обучение", "expense"),
    (["канцтовары", "офисмаг", "офис"], "Канцтовары", "expense"),
    (["закупка", "материалы", "стройматериалы", "закупка материалов"], "Закупки", "expense"),
    (["возврат"], "Возврат", "income"),
]

# Цвета для категорий
CATEGORY_COLORS: dict[str, str] = {
    "Продукты и питание": "#22c55e",
    "Транспорт": "#3b82f6",
    "Связь и интернет": "#8b5cf6",
    "Аренда": "#f59e0b",
    "Подписки и обучение": "#ec4899",
    "Канцтовары": "#6b7280",
    "Закупки": "#ea580c",
    "Возврат": "#10b981",
}


def suggest_category(description: str, counterparty: str, direction: str) -> str | None:
    """
    Возвращает название категории по ключевым словам или None.
    Ищет в description и counterparty (lowercase).
    """
    text = f"{(description or '').lower()} {(counterparty or '').lower()}"
    for keywords, cat_name, cat_type in DEFAULT_KEYWORDS:
        if cat_type == "expense" and direction != "out":
            continue
        if cat_type == "income" and direction != "in":
            continue
        for kw in keywords:
            if kw in text:
                return cat_name
    return None


def get_category_color(category_name: str) -> str | None:
    return CATEGORY_COLORS.get(category_name)
