import React, { useState, useEffect } from 'react';
import api from '../services/api';

const TABS = [
  { key: 'want_to_read', label: 'Хочу прочитать' },
  { key: 'currently_reading', label: 'Читаю сейчас' },
  { key: 'read', label: 'Прочитано' },
];

function BookshelfPage() {
  const [activeTab, setActiveTab] = useState('want_to_read');
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchBooks = async (status) => {
    setLoading(true);
    try {
      const res = await api.get('/bookshelf', { params: { status } });
      setBooks(res.data.books);
    } catch (err) {
      console.error('Ошибка загрузки дневника:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooks(activeTab);
  }, [activeTab]);

  const handleRemove = async (bookId) => {
    try {
      await api.delete(`/bookshelf/${bookId}`);
      setBooks(books.filter((b) => b.book.book_id !== bookId));
    } catch (err) {
      console.error('Ошибка удаления:', err);
    }
  };

  return (
    <div className="bookshelf-container">
      <h2>Читательский дневник</h2>

      <div className="tabs">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            className={`tab ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="loading-text">Загрузка...</p>
      ) : books.length === 0 ? (
        <p className="empty-text">Здесь пока пусто</p>
      ) : (
        <div className="bookshelf-list">
          {books.map((item) => (
            <div key={item.bookshelf_id} className="bookshelf-item">
              {item.book.cover_url && (
                <img
                  src={item.book.cover_url}
                  alt={item.book.title}
                  className="bookshelf-cover"
                  referrerPolicy="no-referrer"
                />
              )}
              <div className="bookshelf-info">
                <h3>{item.book.title}</h3>
                {item.book.authors && (
                  <p className="bookshelf-authors">
                    {item.book.authors.join(', ')}
                  </p>
                )}
              </div>
              <button
                className="remove-btn"
                onClick={() => handleRemove(item.book.book_id)}
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default BookshelfPage;