from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from database import async_session
from models import User, Book, Swipe, BookAuthor, BookGenre
from auth import get_current_user, get_db
from redis_client import (
    add_swipe_to_redis,
    add_disliked_book,
    is_book_disliked,
    get_disliked_books,
    get_pending_swipes,
)

router = APIRouter(prefix="/books", tags=["Свайпы"])


from sqlalchemy.orm import selectinload

async def get_unseen_books(
    db: AsyncSession,
    user_id: int,
    limit: int = 10,
) -> list[Book]:
    """
    Возвращает книги, которые пользователь ещё не свайпал.
    """
    swiped_result = await db.execute(
        select(Swipe.book_id).where(Swipe.user_id == user_id)
    )
    swiped_ids = set(swiped_result.scalars().all())

    disliked_ids = await get_disliked_books(user_id)
    excluded_ids = swiped_ids | disliked_ids

    if excluded_ids:
        stmt = (
            select(Book)
            .options(selectinload(Book.authors).selectinload(BookAuthor.author))
            .options(selectinload(Book.genres).selectinload(BookGenre.genre))
            .where(Book.book_id.notin_(excluded_ids))
            .order_by(func.random())
            .limit(limit)
        )
    else:
        stmt = (
            select(Book)
            .options(selectinload(Book.authors).selectinload(BookAuthor.author))
            .options(selectinload(Book.genres).selectinload(BookGenre.genre))
            .order_by(func.random())
            .limit(limit)
        )

    result = await db.execute(stmt)
    return list(result.unique().scalars().all())


@router.get("/swipe")
async def get_books_for_swiping(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Возвращает порцию книг для свайпов."""
    books = await get_unseen_books(db, current_user.user_id, limit=10)
    return {
        "count": len(books),
        "books": [
            {
                "book_id": b.book_id,
                "title": b.title,
                "description": (b.description or "")[:300] + "...",
                "page_count": b.page_count,
                "cover_url": b.cover_url,
                "authors": [ba.author.name for ba in b.authors],
                "genres": [bg.genre.name for bg in b.genres],
            }
            for b in books
        ],
    }


@router.post("/swipe")
async def swipe_book(
    book_id: str,
    is_liked: bool,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Сохраняет свайп (лайк/дизлайк)."""
    # Проверяем, что книга существует
    book_result = await db.execute(select(Book).where(Book.book_id == book_id))
    book = book_result.scalar_one_or_none()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена",
        )

    # Проверяем, что пользователь ещё не свайпал эту книгу
    existing = await db.execute(
        select(Swipe).where(
            Swipe.user_id == current_user.user_id,
            Swipe.book_id == book_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Вы уже оценили эту книгу",
        )

    # 1. Быстрая запись в Redis
    await add_swipe_to_redis(current_user.user_id, book_id, is_liked)

    # 2. Если дизлайк — добавляем в множество для исключения
    if not is_liked:
        await add_disliked_book(current_user.user_id, book_id)

    # 3. Сразу сохраняем в PostgreSQL (дублируем для надёжности)
    swipe = Swipe(
        user_id=current_user.user_id,
        book_id=book_id,
        is_liked=is_liked,
    )
    db.add(swipe)
    await db.commit()

    return {
        "status": "ok",
        "book_id": book_id,
        "is_liked": is_liked,
    }