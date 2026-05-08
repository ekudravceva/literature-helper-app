from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, UniqueConstraint, Index, SmallInteger, BigInteger
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    swipes = relationship("Swipe", back_populates="user")
    bookshelves = relationship("Bookshelf", back_populates="user")
    reading_goals = relationship("ReadingGoal", back_populates="user")


class Book(Base):
    __tablename__ = "books"

    book_id = Column(String(50), primary_key=True)  # Google Books ID
    title = Column(String(500), nullable=False)
    description = Column(Text)
    page_count = Column(Integer)
    cover_url = Column(String(500))

    # Связи
    authors = relationship("BookAuthor", back_populates="book")
    genres = relationship("BookGenre", back_populates="book")
    swipes = relationship("Swipe", back_populates="book")
    bookshelves = relationship("Bookshelf", back_populates="book")


class Author(Base):
    __tablename__ = "authors"

    author_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)

    # Связи
    books = relationship("BookAuthor", back_populates="author")


class BookAuthor(Base):
    __tablename__ = "book_authors"

    book_id = Column(
        String(50),
        ForeignKey("books.book_id", ondelete="CASCADE"),
        primary_key=True,
    )
    author_id = Column(
        Integer,
        ForeignKey("authors.author_id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Связи
    book = relationship("Book", back_populates="authors")
    author = relationship("Author", back_populates="books")


class Genre(Base):
    __tablename__ = "genres"

    genre_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)

    # Связи
    books = relationship("BookGenre", back_populates="genre")


class BookGenre(Base):
    __tablename__ = "book_genres"

    book_id = Column(
        String(50),
        ForeignKey("books.book_id", ondelete="CASCADE"),
        primary_key=True,
    )
    genre_id = Column(
        Integer,
        ForeignKey("genres.genre_id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Связи
    book = relationship("Book", back_populates="genres")
    genre = relationship("Genre", back_populates="books")


class Swipe(Base):
    __tablename__ = "swipes"

    swipe_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    book_id = Column(
        String(50),
        ForeignKey("books.book_id", ondelete="CASCADE"),
        nullable=False,
    )
    is_liked = Column(Boolean, nullable=False)
    swiped_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    user = relationship("User", back_populates="swipes")
    book = relationship("Book", back_populates="swipes")

    # Индексы для быстрых запросов
    __table_args__ = (
        Index("ix_swipes_user_id", "user_id"),
        Index("ix_swipes_user_book", "user_id", "book_id"),
    )


class Bookshelf(Base):
    __tablename__ = "bookshelves"

    bookshelf_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    book_id = Column(
        String(50),
        ForeignKey("books.book_id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(
        String(20),
        nullable=False,
        comment="want_to_read, currently_reading, read",
    )
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Связи
    user = relationship("User", back_populates="bookshelves")
    book = relationship("Book", back_populates="bookshelves")

    # Одна книга — один статус у пользователя
    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="uq_bookshelf_user_book"),
        Index("ix_bookshelves_user_id", "user_id"),
    )


class ReadingGoal(Base):
    __tablename__ = "reading_goals"

    goal_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    year = Column(SmallInteger, nullable=False)
    target_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    user = relationship("User", back_populates="reading_goals")

    # Одна цель на год для пользователя
    __table_args__ = (
        UniqueConstraint("user_id", "year", name="uq_goal_user_year"),
        Index("ix_reading_goals_user_id", "user_id"),
    )