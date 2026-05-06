import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5433/literature_helper")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")