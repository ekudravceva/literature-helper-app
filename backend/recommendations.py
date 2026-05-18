from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session
from models import User
from auth import get_current_user, get_db
from recommendations_service import (
    generate_recommendations,
    get_cached_recommendations,
    cache_recommendations,
)

router = APIRouter(prefix="/recommendations", tags=["Рекомендации"])


@router.get("")
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    refresh: bool = False,
):
    """
    Возвращает персонализированные рекомендации.
    Если refresh=true — принудительно пересчитывает.
    """
    user_id = current_user.user_id

    # Пробуем взять из кэша
    if not refresh:
        cached = await get_cached_recommendations(user_id)
        if cached:
            return {"source": "cache", "count": len(cached), "books": cached}

    # Генерируем новые
    recommendations = await generate_recommendations(user_id, db)

    # Сохраняем в кэш
    await cache_recommendations(user_id, recommendations)

    return {"source": "fresh", "count": len(recommendations), "books": recommendations}