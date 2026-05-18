import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from models import User, Book, Swipe, BookAuthor, BookGenre, Genre
from redis_client import redis_client, get_disliked_books


async def build_taste_profile(user_id: int, db: AsyncSession) -> dict:
    """
    Строит профиль вкуса пользователя на основе лайкнутых книг.
    Возвращает словарь: {genres: {name: weight}, authors: {name: weight}}
    """
    # Получаем все лайки пользователя с жадной загрузкой связанных данных
    result = await db.execute(
        select(Swipe)
        .options(
            selectinload(Swipe.book)
            .selectinload(Book.authors)
            .selectinload(BookAuthor.author),
        )
        .options(
            selectinload(Swipe.book)
            .selectinload(Book.genres)
            .selectinload(BookGenre.genre),
        )
        .where(Swipe.user_id == user_id, Swipe.is_liked == True)
    )
    liked_swipes = result.unique().scalars().all()

    genres_weight = {}
    authors_weight = {}

    for swipe in liked_swipes:
        book = swipe.book
        if book is None:
            continue
        # Учитываем авторов
        for ba in book.authors:
            name = ba.author.name
            authors_weight[name] = authors_weight.get(name, 0) + 1
        # Учитываем жанры
        for bg in book.genres:
            name = bg.genre.name
            genres_weight[name] = genres_weight.get(name, 0) + 1

    return {
        "genres": genres_weight,
        "authors": authors_weight,
    }


async def generate_recommendations(
    user_id: int,
    db: AsyncSession,
    limit: int = 20,
    serendipity_ratio: float = 0.3,
) -> list[dict]:
    """
    Генерирует персонализированные рекомендации.
    """
    # 1. Строим профиль вкуса
    profile = await build_taste_profile(user_id, db)

    # Если лайков нет — возвращаем случайные книги
    if not profile["genres"] and not profile["authors"]:
        return await _get_random_books(db, user_id, limit)

    # 2. Получаем ID уже свайпнутых книг
    swiped_result = await db.execute(
        select(Swipe.book_id).where(Swipe.user_id == user_id)
    )
    swiped_ids = set(swiped_result.scalars().all())

    # 3. Добавляем отклонённые из Redis
    disliked_ids = await get_disliked_books(user_id)
    excluded_ids = swiped_ids | disliked_ids

    # 4. Получаем все книги-кандидаты
    stmt = select(Book).options(
        selectinload(Book.authors).selectinload(BookAuthor.author),
        selectinload(Book.genres).selectinload(BookGenre.genre),
    )
    if excluded_ids:
        stmt = stmt.where(Book.book_id.notin_(excluded_ids))

    result = await db.execute(stmt)
    candidates = result.unique().scalars().all()

    # 5. Скоринг книг
    scored_books = []
    for book in candidates:
        score = _calculate_score(book, profile)
        if score > 0:
            scored_books.append({"book": book, "score": score})

    # 6. Сортировка по убыванию
    scored_books.sort(key=lambda x: x["score"], reverse=True)

    # 7. Формируем финальный список
    num_serendipity = int(limit * serendipity_ratio)
    num_main = limit - num_serendipity

    # Основной блок — топ-N
    main_recs = scored_books[:num_main]

    # Блок «Наугад из понравившегося» — книги из смежных жанров
    serendipity_recs = _get_serendipity_recommendations(
        scored_books, profile, num_serendipity, skip_first=num_main
    )

    # Объединяем и перемешиваем
    final_recs = main_recs + serendipity_recs
    random.shuffle(final_recs)

    # 8. Форматируем ответ
    return [
        {
            "book_id": r["book"].book_id,
            "title": r["book"].title,
            "description": (r["book"].description or "")[:300] + "...",
            "page_count": r["book"].page_count,
            "cover_url": r["book"].cover_url,
            "authors": [ba.author.name for ba in r["book"].authors],
            "genres": [bg.genre.name for bg in r["book"].genres],
            "score": round(r["score"], 1),
        }
        for r in final_recs
    ]


def _calculate_score(book: Book, profile: dict) -> float:
    """Вычисляет релевантность книги профилю пользователя."""
    GENRE_WEIGHT = 3.0
    AUTHOR_WEIGHT = 2.0

    score = 0.0

    for bg in book.genres:
        score += profile["genres"].get(bg.genre.name, 0) * GENRE_WEIGHT

    for ba in book.authors:
        score += profile["authors"].get(ba.author.name, 0) * AUTHOR_WEIGHT

    return score


def _get_serendipity_recommendations(
    scored_books: list[dict],
    profile: dict,
    count: int,
    skip_first: int = 20,
) -> list[dict]:
    """Выбирает книги из смежных категорий для разнообразия."""
    if not profile["genres"]:
        return []

    # Берём топ-3 любимых жанра
    top_genres = sorted(profile["genres"].items(), key=lambda x: x[1], reverse=True)
    top_genre_names = {g[0] for g in top_genres[:3]}

    # Ищем книги в этих жанрах, но не в топе
    candidates = []
    for item in scored_books[skip_first:]:
        book_genres = {bg.genre.name for bg in item["book"].genres}
        if book_genres & top_genre_names:  # пересечение жанров
            candidates.append(item)

    if not candidates:
        # Если нет подходящих — берём случайные из хвоста
        tail = scored_books[skip_first:]
        if tail:
            candidates = random.sample(tail, min(count, len(tail)))
            return candidates
        return []

    return random.sample(candidates, min(count, len(candidates)))


async def _get_random_books(db: AsyncSession, user_id: int, limit: int) -> list[dict]:
    """Возвращает случайные книги (для холодного старта)."""
    swiped_result = await db.execute(
        select(Swipe.book_id).where(Swipe.user_id == user_id)
    )
    swiped_ids = set(swiped_result.scalars().all())
    disliked_ids = await get_disliked_books(user_id)
    excluded_ids = swiped_ids | disliked_ids

    stmt = (
        select(Book)
        .options(
            selectinload(Book.authors).selectinload(BookAuthor.author),
            selectinload(Book.genres).selectinload(BookGenre.genre),
        )
    )
    if excluded_ids:
        stmt = stmt.where(Book.book_id.notin_(excluded_ids))
    stmt = stmt.order_by(func.random()).limit(limit)

    result = await db.execute(stmt)
    books = result.unique().scalars().all()

    return [
        {
            "book_id": b.book_id,
            "title": b.title,
            "description": (b.description or "")[:300] + "...",
            "page_count": b.page_count,
            "cover_url": b.cover_url,
            "authors": [ba.author.name for ba in b.authors],
            "genres": [bg.genre.name for bg in b.genres],
            "score": 0.0,
        }
        for b in books
    ]


# ─── Кэширование рекомендаций в Redis ───

async def get_cached_recommendations(user_id: int) -> list[dict] | None:
    """Пытается достать рекомендации из кэша Redis."""
    import json

    key = f"user:{user_id}:recommendations"
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None


async def cache_recommendations(user_id: int, recommendations: list[dict], ttl: int = 3600):
    """Сохраняет рекомендации в Redis с TTL (по умолчанию 1 час)."""
    import json

    key = f"user:{user_id}:recommendations"
    await redis_client.set(key, json.dumps(recommendations), ex=ttl)