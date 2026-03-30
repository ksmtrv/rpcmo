from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.categories import CategoryCreate, CategoryRead, CategoryUpdate
from app.core.db import get_db
from app.core.dependencies import get_current_user_id
from app.infrastructure.db.repositories import CategoryRepository

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
async def list_categories(
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = CategoryRepository(session)
    cats = await repo.get_by_user(user_id)
    return [CategoryRead.model_validate(c) for c in cats]


@router.post("", response_model=CategoryRead)
async def create_category(
    body: CategoryCreate,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = CategoryRepository(session)
    cat = await repo.create(user_id, body.name, body.type, body.color)
    return CategoryRead.model_validate(cat)


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: str,
    body: CategoryUpdate,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    from sqlalchemy import select
    from app.infrastructure.db.models import Category

    result = await session.execute(select(Category).where(Category.id == category_id, Category.user_id == user_id))
    cat = result.scalar_one_or_none()
    if not cat:
        from fastapi import HTTPException
        raise HTTPException(404, "Категория не найдена")
    if body.name is not None:
        cat.name = body.name
    if body.color is not None:
        cat.color = body.color
    await session.flush()
    return CategoryRead.model_validate(cat)
