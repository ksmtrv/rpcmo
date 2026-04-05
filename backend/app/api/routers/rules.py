from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.rules import RuleCreate, RuleRead, RuleSuggestionRead, RuleUpdate
from app.core.db import get_db
from app.core.dependencies import get_current_user_id
from app.infrastructure.db.repositories import (
    CategorizationRuleRepository,
    CategoryRepository,
    RuleSuggestionRepository,
)

router = APIRouter(prefix="/rules", tags=["rules"])


@router.get("/suggestions", response_model=list[RuleSuggestionRead])
async def list_suggestions(
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = RuleSuggestionRepository(session)
    items = await repo.list_by_user(user_id, status="pending")
    return [RuleSuggestionRead.model_validate(s) for s in items]


@router.post("/suggestions/{suggestion_id}/accept", response_model=RuleRead)
async def accept_suggestion(
    suggestion_id: str,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    sug_repo = RuleSuggestionRepository(session)
    rule_repo = CategorizationRuleRepository(session)
    s = await sug_repo.get_by_id(user_id, suggestion_id)
    if not s or s.status != "pending":
        raise HTTPException(404, "Предложение не найдено")
    name = f"Из предложения: {s.source_pattern[:48]}"
    rule = await rule_repo.create(
        user_id=user_id,
        name=name,
        priority=0,
        conditions_json=s.suggested_conditions_json,
        category_id=s.suggested_category_id,
        is_active=True,
    )
    s.status = "accepted"
    await session.flush()
    return RuleRead.model_validate(rule)


@router.post("/suggestions/{suggestion_id}/dismiss")
async def dismiss_suggestion(
    suggestion_id: str,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    sug_repo = RuleSuggestionRepository(session)
    s = await sug_repo.get_by_id(user_id, suggestion_id)
    if not s:
        raise HTTPException(404, "Предложение не найдено")
    s.status = "dismissed"
    await session.flush()
    return {"status": "dismissed"}


@router.get("", response_model=list[RuleRead])
async def list_rules(
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = CategorizationRuleRepository(session)
    items = await repo.list_by_user(user_id)
    return [RuleRead.model_validate(r) for r in items]


@router.post("", response_model=RuleRead)
async def create_rule(
    body: RuleCreate,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    cat_repo = CategoryRepository(session)
    if not await cat_repo.get_by_id_for_user(user_id, body.category_id):
        raise HTTPException(400, "Категория не найдена")
    if not _conditions_have_matcher(body.conditions_json):
        raise HTTPException(400, "conditions_json: нужно хотя бы одно текстовое условие")
    repo = CategorizationRuleRepository(session)
    r = await repo.create(
        user_id=user_id,
        name=body.name,
        priority=body.priority,
        conditions_json=body.conditions_json,
        category_id=body.category_id,
    )
    return RuleRead.model_validate(r)


def _conditions_have_matcher(conditions: dict) -> bool:
    if not conditions:
        return False
    kws = conditions.get("keywords_any") or []
    if isinstance(kws, list) and any(kws):
        return True
    if conditions.get("description_contains"):
        return True
    if conditions.get("normalized_description_equals"):
        return True
    if conditions.get("counterparty_contains"):
        return True
    return False


@router.patch("/{rule_id}", response_model=RuleRead)
async def update_rule(
    rule_id: str,
    body: RuleUpdate,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = CategorizationRuleRepository(session)
    cat_repo = CategoryRepository(session)
    r = await repo.get_by_id(user_id, rule_id)
    if not r:
        raise HTTPException(404, "Правило не найдено")
    if body.category_id is not None and not await cat_repo.get_by_id_for_user(user_id, body.category_id):
        raise HTTPException(400, "Категория не найдена")
    if body.name is not None:
        r.name = body.name
    if body.priority is not None:
        r.priority = body.priority
    if body.conditions_json is not None:
        if not _conditions_have_matcher(body.conditions_json):
            raise HTTPException(400, "conditions_json: нужно хотя бы одно текстовое условие")
        r.conditions_json = body.conditions_json
    if body.category_id is not None:
        r.category_id = body.category_id
    if body.is_active is not None:
        r.is_active = body.is_active
    await session.flush()
    return RuleRead.model_validate(r)


@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: str,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = CategorizationRuleRepository(session)
    r = await repo.get_by_id(user_id, rule_id)
    if not r:
        raise HTTPException(404, "Правило не найдено")
    await repo.delete(r)
    return {"status": "deleted"}
