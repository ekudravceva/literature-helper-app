from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_client import redis_client
from database import engine, Base
from auth import router as auth_router
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session
from books_service import seed_books
from auth import get_current_user
from swipes import router as swipes_router
from recommendations import router as recommendations_router
from bookshelf import router as bookshelf_router
from goals import router as goals_router

app = FastAPI(title="Литературный помощник")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(swipes_router)
app.include_router(recommendations_router)
app.include_router(bookshelf_router)
app.include_router(goals_router)

@app.post("/seed")
async def seed_test_books():
    """Загружает тестовые книги из Google Books API."""
    async with async_session() as db:
        books = await seed_books(db, count=40)
        return {"message": f"Загружено книг: {len(books)}"}

@app.on_event("startup")
async def startup():
    # Создаём все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Проверяем Redis
    await redis_client.ping()
    print("База данных и Redis готовы")


@app.get("/health")
async def health_check():
    redis_ok = False
    try:
        await redis_client.ping()
        redis_ok = True
    except Exception:
        pass
    return {
        "status": "ok",
        "redis": redis_ok,
        "database": "connected",
    }

