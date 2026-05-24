import asyncio
from database import async_session
from books_service import search_books, save_book_to_db

async def main():
    async with async_session() as db:
        count = 0
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
        for query in queries:
            try:
                books_data = await search_books(query=query, max_results=25)
                for book_data in books_data:
                    try:
                        await save_book_to_db(db, book_data)
                        count += 1
                        print(f"[{count}] {book_data['title']}")
                    except Exception as e:
                        print(f"  Ошибка сохранения: {e}")
            except Exception as e:
                print(f"Ошибка запроса '{query}': {e}")

        print(f"\nГотово! Загружено: {count} книг")

asyncio.run(main())