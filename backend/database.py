# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
# from sqlalchemy.orm import DeclarativeBase
# from config import DATABASE_URL

# engine = create_async_engine(DATABASE_URL, echo=True)
# async_session = async_sessionmaker(engine, expire_on_commit=False)

# class Base(DeclarativeBase):
#     pass

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)  # echo=False убирает SQL-логи
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Импортируем Base из models, а не создаём здесь
from base import Base