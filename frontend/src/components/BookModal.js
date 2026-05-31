import React, { useState } from 'react';
import api from '../services/api';

function BookModal({ book, onClose }) {
  const [statusLoading, setStatusLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');

  const handleSetStatus = async (status) => {
    setStatusLoading(true);
    setStatusMessage('');
    try {
      await api.post('/bookshelf', null, {
        params: { book_id: book.book_id, status },
      });
      setStatusMessage(
        status === 'want_to_read'
          ? 'Добавлено в «Хочу прочитать»'
          : status === 'currently_reading'
          ? 'Добавлено в «Читаю сейчас»'
          : 'Добавлено в «Прочитано»'
      );
    } catch (err) {
      setStatusMessage('Ошибка: ' + (err.response?.data?.detail || 'что-то пошло не так'));
    } finally {
      setStatusLoading(false);
      setTimeout(() => setStatusMessage(''), 2000);
    }
  };

  if (!book) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          ✕
        </button>

        {book.cover_url && (
          <img
            src={book.cover_url}
            alt={book.title}
            className="modal-cover"
            referrerPolicy="no-referrer"
          />
        )}

        <div className="modal-body">
          <h2>{book.title}</h2>

          {book.authors && (
            <p className="modal-authors">{book.authors.join(', ')}</p>
          )}

          {book.genres && (
            <div className="modal-genres">
              {book.genres.map((genre) => (
                <span key={genre} className="genre-tag">{genre}</span>
              ))}
            </div>
          )}

          {book.page_count && (
            <p className="modal-pages">{book.page_count} страниц</p>
          )}

          {book.description && (
            <div className="modal-description">
              <h3>Описание</h3>
              <p>{book.description.replace('...', '')}</p>
            </div>
          )}

          <div className="modal-actions">
            <h3>Добавить в дневник</h3>
            <div className="status-buttons">
              <button
                className="status-btn want"
                onClick={() => handleSetStatus('want_to_read')}
                disabled={statusLoading}
              >
                Хочу прочитать
              </button>
              <button
                className="status-btn reading"
                onClick={() => handleSetStatus('currently_reading')}
                disabled={statusLoading}
              >
                Читаю сейчас
              </button>
              <button
                className="status-btn read"
                onClick={() => handleSetStatus('read')}
                disabled={statusLoading}
              >
                Прочитано
              </button>
            </div>
            {statusMessage && <p className="status-message">{statusMessage}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default BookModal;