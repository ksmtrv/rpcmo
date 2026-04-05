"""Сопоставление транзакции с conditions_json правила категоризации.

Формат conditions_json (все поля опциональны, но нужно хотя бы одно текстовое условие):
- keywords_any: list[str] — любое вхождение подстроки в (description + counterparty), без учёта регистра
- description_contains: str — подстрока в назначении платежа
- normalized_description_equals: str — точное совпадение нормализованного назначения (как в БД)
- counterparty_contains: str — подстрока в контрагенте
- direction: "in" | "out" — направление должно совпасть, если поле задано
"""

from app.domain.services.text_normalize import normalize_description


def matches_rule_conditions(
    conditions: dict | None,
    description: str,
    counterparty: str | None,
    direction: str,
) -> bool:
    if not conditions or not isinstance(conditions, dict):
        return False

    d = str(direction).lower()
    dir_req = conditions.get("direction")
    if dir_req is not None:
        dr = str(dir_req).lower()
        if dr in ("in", "out") and dr != d:
            return False

    desc_l = (description or "").lower()
    cp_l = (counterparty or "").lower()
    hay = f"{desc_l} {cp_l}"

    has_text = False
    kws = conditions.get("keywords_any") or []
    if isinstance(kws, list) and kws:
        has_text = True
        if not any(str(kw).lower() in hay for kw in kws if kw):
            return False

    dc = conditions.get("description_contains")
    if dc:
        has_text = True
        if str(dc).lower() not in desc_l:
            return False

    nd_eq = conditions.get("normalized_description_equals")
    if nd_eq is not None and str(nd_eq).strip() != "":
        has_text = True
        if normalize_description(description) != str(nd_eq).strip().lower():
            return False

    cc = conditions.get("counterparty_contains")
    if cc:
        has_text = True
        if not counterparty or str(cc).lower() not in cp_l:
            return False

    return has_text
