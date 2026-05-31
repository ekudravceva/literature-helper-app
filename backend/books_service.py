import os
import httpx
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Book, Author, Genre, BookAuthor, BookGenre
import asyncio
from translator import translate_text

load_dotenv()

GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"
API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")


async def search_books(
    query: str = "subject:fiction",
    max_results: int = 20,
    start_index: int = 0,
) -> list[dict]:
    params = {
        "q": query,
        "maxResults": max_results,
        "startIndex": start_index,
        "lang_Restrict": "ru",  
        "orderBy": "relevance",
    }
    if API_KEY:
        params["key"] = API_KEY

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(GOOGLE_BOOKS_API, params=params)
        response.raise_for_status()
        data = response.json()

    books = []
    for item in data.get("items", []):
        volume_info = item.get("volumeInfo", {})
        book_data = {
            "book_id": item["id"],
            "title": volume_info.get("title", "Без названия"),
            "description": volume_info.get("description", ""),
            "page_count": volume_info.get("pageCount"),
            "cover_url": _get_cover_url(volume_info),
            "authors": volume_info.get("authors", []),
            "genres": volume_info.get("categories", []),
        }
        books.append(book_data)

    return books


def _get_cover_url(volume_info: dict) -> str | None:
    image_links = volume_info.get("imageLinks", {})
    for size in ["medium", "thumbnail", "smallThumbnail"]:
        url = image_links.get(size)
        if url:
            url = url.replace("http://", "https://")
            url = url.replace("&edge=curl", "")
            return url
    return None

async def save_book_to_db(db: AsyncSession, book_data: dict) -> Book:
    result = await db.execute(
        select(Book).where(Book.book_id == book_data["book_id"])
    )
    existing_book = result.scalar_one_or_none()
    if existing_book:
        return existing_book

    print(f"Перевод: {book_data['title'][:50]}...")
    translated_title = translate_text(book_data["title"])
    translated_description = translate_text(book_data["description"] or "")

    book = Book(
        book_id=book_data["book_id"],
        title=translated_title,
        description=translated_description,
        page_count=book_data["page_count"],
        cover_url=book_data["cover_url"],
    )
    db.add(book)

    for author_name in book_data["authors"]:
        author = await _get_or_create_author(db, author_name)
        db.add(BookAuthor(book_id=book.book_id, author_id=author.author_id))

    for genre_name in book_data["genres"]:
        translated_genre = translate_text(genre_name)
        genre = await _get_or_create_genre(db, translated_genre)
        db.add(BookGenre(book_id=book.book_id, genre_id=genre.genre_id))

    await db.commit()
    await db.refresh(book)
    return book

async def _get_or_create_author(db: AsyncSession, name: str) -> Author:
    result = await db.execute(select(Author).where(Author.name == name))
    author = result.scalar_one_or_none()
    if author is None:
        author = Author(name=name)
        db.add(author)
        await db.flush()
    return author


async def _get_or_create_genre(db: AsyncSession, name: str) -> Genre:
    result = await db.execute(select(Genre).where(Genre.name == name))
    genre = result.scalar_one_or_none()
    if genre is None:
        genre = Genre(name=name)
        db.add(genre)
        await db.flush()
    return genre


import asyncio

async def seed_books(db: AsyncSession, count: int = 80) -> list[Book]:
    queries = [
        "subject:fiction",
        "subject:fantasy",
        "subject:romance",
        "subject:mystery",
        "subject:horror",
        "subject:adventure",
        "subject:philosophy",
        "subject:poetry",
    ]

    saved_books = []
    for query in queries:
        if len(saved_books) >= count:
            break
        try:
            books_data = await search_books(query=query, max_results=15)
            for book_data in books_data:
                if len(saved_books) >= count:
                    break
                book = await save_book_to_db(db, book_data)
                saved_books.append(book)
                print(f"[{len(saved_books)}] {book.title}")
        except Exception as e:
            print(f"Ошибка '{query}': {e}")

    return saved_books