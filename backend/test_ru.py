import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

async def test():
    params = {
        "q": "subject:fiction",
        "maxResults": 10,
        "langRestrict": "ru",
        "key": API_KEY,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            "https://www.googleapis.com/books/v1/volumes",
            params=params,
        )
        data = response.json()
        print("Статус:", response.status_code)
        print("Всего результатов:", data.get("totalItems", 0))
        for item in data.get("items", []):
            vol = item.get("volumeInfo", {})
            lang = vol.get("language", "не указан")
            title = vol.get("title", "?")
            print(f"  [{lang}] {title}")

asyncio.run(test())