## Развёртывание проекта «Literature Helper»

### Запущенные сервисы

| Сервис | Порт | Где запущен | Команда |
|---|---|---|---|
| **Backend** (FastAPI) | `8000` | Терминал (вручную) | `uvicorn main:app --reload` |
| **Frontend** (React) | `3000` | Терминал (вручную) | `npm start` |
| **PostgreSQL 16** | `5433` | Docker | `docker-compose up -d` |
| **Redis 7** | `6379` | Docker | `docker-compose up -d` |

### 3. Установленные библиотеки

**Backend (Python):**
- `fastapi` — веб-фреймворк
- `uvicorn` — ASGI-сервер
- `sqlalchemy` + `asyncpg` — работа с PostgreSQL (асинхронно)
- `redis` — клиент для Redis
- `greenlet` — требуется для асинхронного SQLAlchemy
- `httpx` — HTTP-клиент (для запросов к Google Books API)
- `python-dotenv` — переменные окружения
- `pydantic` — валидация данных
- `alembic` — миграции БД

**Frontend (JavaScript):**
- `react` + `react-dom` — React 19
- `react-scripts` — CRA-скрипты
- `axios` — HTTP-клиент
- `react-tinder-card` — библиотека свайпов

### 4. Проверка работоспособности

- **`GET http://localhost:8000/health`** возвращает:
  ```json
  {"status":"ok","redis":true}
  ```
- **`http://localhost:3000`** показывает страницу React с надписью «Литературный помощник» и статусом сервера `ok`
- **`docker ps`** показывает два контейнера со статусом `Up`