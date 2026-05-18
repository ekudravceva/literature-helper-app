import redis.asyncio as redis
from config import REDIS_URL

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# async def add_swipe_to_redis(user_id: int, book_id: str, is_liked: bool):
#     """Добавляет свайп в список для пакетной записи."""
#     key = f"user:{user_id}:swipes"
#     value = f"{book_id}:{'like' if is_liked else 'dislike'}"
#     await redis_client.rpush(key, value)


# async def get_pending_swipes(user_id: int) -> list[dict]:
#     """Извлекает все накопленные свайпы из Redis."""
#     key = f"user:{user_id}:swipes"
#     raw = await redis_client.lrange(key, 0, -1)
#     await redis_client.delete(key)  # Очищаем после чтения
#     swipes = []
#     for item in raw:
#         book_id, action = item.split(":")
#         swipes.append({"book_id": book_id, "is_liked": action == "like"})
#     return swipes


# async def add_disliked_book(user_id: int, book_id: str):
#     """Добавляет book_id в множество отклонённых книг."""
#     key = f"user:{user_id}:disliked"
#     await redis_client.sadd(key, book_id)


# async def is_book_disliked(user_id: int, book_id: str) -> bool:
#     """Проверяет, отклонял ли пользователь эту книгу."""
#     key = f"user:{user_id}:disliked"
#     return await redis_client.sismember(key, book_id)


# async def get_disliked_books(user_id: int) -> set[str]:
#     """Возвращает множество всех отклонённых книг пользователя."""
#     key = f"user:{user_id}:disliked"
#     return await redis_client.smembers(key)