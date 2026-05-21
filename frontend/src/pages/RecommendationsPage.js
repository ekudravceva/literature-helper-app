import React, { useState, useEffect } from 'react';
import api from '../services/api';
import BookModal from '../components/BookModal';

function RecommendationsPage() {
  const [books, setBooks] = useState([]);
  const [source, setSource] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedBook, setSelectedBook] = useState(null);

  const fetchRecommendations = async (refresh = false) => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get('/recommendations', { params: { refresh } });
      setBooks(res.data.books);
      setSource(res.data.source);
    } catch (err) {
      setError('Не удалось загрузить рекомендации');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const handleRefresh = () => {
    fetchRecommendations(true);
  };

  if (loading) {
    return <div className="container">Загружаем рекомендации...</div>;
  }

  return (
    <div className="recs-container">
      <div className="recs-header">
        <h2>Ваши рекомендации</h2>
        <button onClick={handleRefresh} className="refresh-btn">
          Обновить
        </button>
      </div>

      {source && (
        <p className="recs-source">
          {source === 'cache' ? '📦 Из кэша' : '🔄 Свежие рекомендации'}
        </p>
      )}

      {error && <p className="error">{error}</p>}

      {books.length === 0 ? (
        <div className="container">
          <p>Пока нет рекомендаций. Поставьте больше лайков!</p>
        </div>
      ) : (
        <div className="recs-grid">
          {books.map((book) => (
            <div
            key={book.book_id}
            className="recs-card"
            onClick={() => setSelectedBook(book)}
            >
              {book.cover_url && (
                <img
                  src={book.cover_url}
                  alt={book.title}
                  className="recs-cover"
                  referrerPolicy="no-referrer"
                />
              )}
              <div className="recs-info">
                <h3>{book.title}</h3>
                {book.authors && (
                  <p className="recs-authors">{book.authors.join(', ')}</p>
                )}
                {book.genres && (
                  <p className="recs-genres">
                    {book.genres.slice(0, 3).join(' • ')}
                  </p>
                )}
                {book.score > 0 && (
                  <span className="recs-score">{book.score}%</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
      {selectedBook && (
        <BookModal
            book={selectedBook}
            onClose={() => setSelectedBook(null)}
        />
        )}
    </div>
  );
}

export default RecommendationsPage;