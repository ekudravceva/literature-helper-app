import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';

function SwipePage() {
  const [books, setBooks] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [finished, setFinished] = useState(false);
  const [lastDirection, setLastDirection] = useState(null);

  // Для анимации свайпа
  const cardRef = useRef(null);
  const [swipeX, setSwipeX] = useState(0);
  const [swipeOpacity, setSwipeOpacity] = useState(1);
  const [isDragging, setIsDragging] = useState(false);
  const dragStartX = useRef(0);

  const fetchBooks = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get('/books/swipe');
      if (res.data.books.length === 0) {
        setFinished(true);
        setBooks([]);
      } else {
        setBooks(res.data.books);
        setCurrentIndex(0);
        setFinished(false);
        setSwipeX(0);
        setSwipeOpacity(1);
      }
    } catch (err) {
      setError('Не удалось загрузить книги');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooks();
  }, []);

  const completeSwipe = async (direction) => {
    const book = books[currentIndex];
    if (!book) return;

    setLastDirection(direction);
    const isLiked = direction === 'right';

    try {
      await api.post('/books/swipe', null, {
        params: { book_id: book.book_id, is_liked: isLiked },
      });
    } catch (err) {
      console.error('Ошибка свайпа:', err);
    }

    // Анимация ухода карточки
    const screenWidth = window.innerWidth;
    setSwipeX(direction === 'right' ? screenWidth : -screenWidth);
    setSwipeOpacity(0);

    setTimeout(() => {
      if (currentIndex + 1 >= books.length) {
        fetchBooks();
      } else {
        setCurrentIndex(currentIndex + 1);
        setSwipeX(0);
        setSwipeOpacity(1);
        setLastDirection(null);
      }
    }, 300);
  };

  // Обработчики касаний и мыши
  const handleDragStart = (e) => {
    setIsDragging(true);
    const clientX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
    dragStartX.current = clientX;
  };

  const handleDragMove = (e) => {
    if (!isDragging) return;
    const clientX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
    const diff = clientX - dragStartX.current;
    setSwipeX(diff);
    setSwipeOpacity(1 - Math.abs(diff) / 300);
  };

  const handleDragEnd = () => {
    if (!isDragging) return;
    setIsDragging(false);

    if (swipeX > 100) {
      completeSwipe('right');
    } else if (swipeX < -100) {
      completeSwipe('left');
    } else {
      setSwipeX(0);
      setSwipeOpacity(1);
    }
  };

  if (loading) {
    return <div className="container">Загрузка книг...</div>;
  }

  if (finished) {
    return (
      <div className="container">
        <h2>Книги закончились!</h2>
        <p>Вы просмотрели все доступные книги.</p>
        <button onClick={() => {
        setFinished(false);
        fetchBooks();
        }}>
        Попробовать ещё
        </button>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <p className="error">{error}</p>
        <button onClick={fetchBooks}>Повторить</button>
      </div>
    );
  }

  if (books.length === 0) {
    return <div className="container">Книг пока нет.</div>;
  }

  const book = books[currentIndex];

  return (
    <div className="swipe-container">
      <h2>Выберите книги</h2>
      <p className="swipe-counter">
        {currentIndex + 1} / {books.length}
      </p>

      {lastDirection && (
        <p className={`swipe-feedback ${lastDirection}`}>
          {lastDirection === 'right' ? 'Понравилось!' : 'Пропущено'}
        </p>
      )}

      <div className="card-area">
        <div
          ref={cardRef}
          className="book-card"
          style={{
            transform: `translateX(${swipeX}px) rotate(${swipeX * 0.05}deg)`,
            opacity: swipeOpacity,
            transition: isDragging ? 'none' : 'transform 0.3s ease, opacity 0.3s ease',
          }}
          onMouseDown={handleDragStart}
          onMouseMove={handleDragMove}
          onMouseUp={handleDragEnd}
          onMouseLeave={handleDragEnd}
          onTouchStart={handleDragStart}
          onTouchMove={handleDragMove}
          onTouchEnd={handleDragEnd}
        >
          {book.cover_url && (
            <img src={book.cover_url} alt={book.title} className="book-cover" />
          )}
          <div className="book-info">
            <h3>{book.title}</h3>
            {book.authors && (
              <p className="book-authors">{book.authors.join(', ')}</p>
            )}
            {book.genres && (
              <p className="book-genres">{book.genres.slice(0, 3).join(' • ')}</p>
            )}
            {book.description && (
              <p className="book-description">{book.description}</p>
            )}
            {book.page_count && (
              <p className="book-pages">{book.page_count} стр.</p>
            )}
          </div>
        </div>
      </div>

      <div className="swipe-buttons">
        <button className="swipe-btn dislike" onClick={() => completeSwipe('left')}>
          ✕
        </button>
        <button className="swipe-btn like" onClick={() => completeSwipe('right')}>
          ♡
        </button>
      </div>
    </div>
  );
}

export default SwipePage;