from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.categories import CategoryCreate, CategoryRead, CategoryUpdate
from app.core.db import get_db
from app.core.dependencies import get_current_user_id
from app.infrastructure.db.models import Category
from app.infrastructure.db.repositories import CategoryRepository, UserRepository

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
async def list_categories(
    response: Response,
    session: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
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
    result = await session.execute(select(Category).where(Category.id == category_id, Category.user_id == user_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "Категория не найдена")
    if body.name is not None:
        cat.name = body.name
    if body.color is not None:
        cat.color = body.color
    await session.flush()
    return CategoryRead.model_validate(cat)


@router.delete("/{category_id}", status_code=204, response_class=Response)
async def delete_category(
    category_id: str,
    session: AsyncSession = Depends(get_db),
) -> None:
    """Без Depends(get_current_user_id): иначе два вызова get_db → две сессии, commit не попадает в ту, где DELETE."""
    user = await UserRepository(session).get_or_create_local_user()
    user_id = user.id
    result = await session.execute(select(Category).where(Category.id == category_id, Category.user_id == user_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "Категория не найдена")
    if cat.is_system:
        raise HTTPException(400, "Системную категорию удалить нельзя")
    await session.delete(cat)
    await session.flush()
