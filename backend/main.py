from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_client import redis_client
from database import engine, Base

app = FastAPI(title="Литературный помощник")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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