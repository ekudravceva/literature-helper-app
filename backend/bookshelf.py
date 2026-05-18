from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import async_session
from models import User, Book, Bookshelf, BookAuthor, BookGenre
from auth import get_current_user, get_db
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/bookshelf", tags=["Читательский дневник"])


@router.post("")
async def set_book_status(
    book_id: str,
    status: str,  # "want_to_read", "currently_reading", "read"
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Добавляет книгу в читательский дневник или меняет её статус."""
    # Проверяем статус
    allowed = {"want_to_read", "currently_reading", "read"}
    if status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Допустимые статусы: {', '.join(allowed)}",
        )

    # Проверяем, что книга существует
    book_result = await db.execute(select(Book).where(Book.book_id == book_id))
    if not book_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена",
        )

    # Проверяем, есть ли уже запись
    existing = await db.execute(
        select(Bookshelf).where(
            Bookshelf.user_id == current_user.user_id,
            Bookshelf.book_id == book_id,
        )
    )
    entry = existing.scalar_one_or_none()

    if entry:
        # Обновляем статус
        entry.status = status
        entry.updated_at = func.now()
    else:
        # Создаём новую запись
        entry = Bookshelf(
            user_id=current_user.user_id,
            book_id=book_id,
            status=status,
        )
        db.add(entry)

    await db.commit()
    await db.refresh(entry)

    return {
        "bookshelf_id": entry.bookshelf_id,
        "book_id": entry.book_id,
        "status": entry.status,
        "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
    }


@router.get("")
async def get_bookshelf(
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Возвращает список книг пользователя. Можно фильтровать по статусу."""
    stmt = (
        select(Bookshelf)
        .options(
            selectinload(Bookshelf.book)
            .selectinload(Book.authors)
            .selectinload(BookAuthor.author),
            selectinload(Bookshelf.book)
            .selectinload(Book.genres)
            .selectinload(BookGenre.genre),
        )
        .where(Bookshelf.user_id == current_user.user_id)
    )

    if status:
        stmt = stmt.where(Bookshelf.status == status)

    stmt = stmt.order_by(Bookshelf.updated_at.desc())

    result = await db.execute(stmt)
    entries = result.unique().scalars().all()

    return {
        "count": len(entries),
        "books": [
            {
                "bookshelf_id": e.bookshelf_id,
                "status": e.status,
                "updated_at": e.updated_at.isoformat() if e.updated_at else None,
                "book": {
                    "book_id": e.book.book_id,
                    "title": e.book.title,
                    "cover_url": e.book.cover_url,
                    "authors": [ba.author.name for ba in e.book.authors],
                    "genres": [bg.genre.name for bg in e.book.genres],
                },
            }
            for e in entries
        ],
    }


@router.delete("/{book_id}")
async def remove_from_bookshelf(
    book_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Удаляет книгу из читательского дневника."""
    result = await db.execute(
        select(Bookshelf).where(
            Bookshelf.user_id == current_user.user_id,
            Bookshelf.book_id == book_id,
        )
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена в вашем дневнике",
        )

    await db.delete(entry)
    await db.commit()

    return {"message": "Книга удалена из дневника"}