from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import async_session
from models import User, Bookshelf, ReadingGoal
from auth import get_current_user, get_db

router = APIRouter(prefix="/goals", tags=["Цели чтения"])


@router.post("")
async def set_goal(
    year: int,
    target_count: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Устанавливает или обновляет годовую цель по чтению."""
    if target_count < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Цель должна быть не меньше 1 книги",
        )

    # Проверяем, есть ли уже цель на этот год
    result = await db.execute(
        select(ReadingGoal).where(
            ReadingGoal.user_id == current_user.user_id,
            ReadingGoal.year == year,
        )
    )
    goal = result.scalar_one_or_none()

    if goal:
        goal.target_count = target_count
    else:
        goal = ReadingGoal(
            user_id=current_user.user_id,
            year=year,
            target_count=target_count,
        )
        db.add(goal)

    await db.commit()
    await db.refresh(goal)

    return {
        "goal_id": goal.goal_id,
        "year": goal.year,
        "target_count": goal.target_count,
    }


@router.get("")
async def get_goals(
    year: int | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Возвращает цели и прогресс по ним."""
    stmt = select(ReadingGoal).where(ReadingGoal.user_id == current_user.user_id)
    if year:
        stmt = stmt.where(ReadingGoal.year == year)
    stmt = stmt.order_by(ReadingGoal.year.desc())

    result = await db.execute(stmt)
    goals = result.scalars().all()

    response = []
    for goal in goals:
        # Считаем количество прочитанных книг за этот год
        count_result = await db.execute(
            select(func.count(Bookshelf.bookshelf_id)).where(
                Bookshelf.user_id == current_user.user_id,
                Bookshelf.status == "read",
                func.extract("year", Bookshelf.updated_at) == goal.year,
            )
        )
        read_count = count_result.scalar() or 0

        response.append({
            "goal_id": goal.goal_id,
            "year": goal.year,
            "target_count": goal.target_count,
            "read_count": read_count,
            "progress_percent": round(read_count / goal.target_count * 100, 1),
            "remaining": max(0, goal.target_count - read_count),
        })

    return {"count": len(response), "goals": response}