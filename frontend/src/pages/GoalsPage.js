import React, { useState, useEffect } from 'react';
import api from '../services/api';

function GoalsPage() {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [year, setYear] = useState(new Date().getFullYear());
  const [target, setTarget] = useState(30);
  const [showForm, setShowForm] = useState(false);

  const fetchGoals = async () => {
    setLoading(true);
    try {
      const res = await api.get('/goals');
      setGoals(res.data.goals);
    } catch (err) {
      console.error('Ошибка загрузки целей:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGoals();
  }, []);

  const handleSetGoal = async (e) => {
    e.preventDefault();
    try {
      await api.post('/goals', null, { params: { year, target_count: target } });
      setShowForm(false);
      fetchGoals();
    } catch (err) {
      console.error('Ошибка установки цели:', err);
    }
  };

  if (loading) {
    return <div className="container">Загрузка...</div>;
  }

  return (
    <div className="goals-container">
      <h2>Цели чтения</h2>

      <button className="add-goal-btn" onClick={() => setShowForm(!showForm)}>
        {showForm ? 'Отмена' : '+ Новая цель'}
      </button>

      {showForm && (
        <form onSubmit={handleSetGoal} className="goal-form">
          <input
            type="number"
            placeholder="Год"
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            required
          />
          <input
            type="number"
            placeholder="Количество книг"
            value={target}
            onChange={(e) => setTarget(Number(e.target.value))}
            required
            min="1"
          />
          <button type="submit">Установить цель</button>
        </form>
      )}

      {goals.length === 0 ? (
        <p className="empty-text">Целей пока нет. Установите первую!</p>
      ) : (
        <div className="goals-list">
          {goals.map((goal) => (
            <div key={goal.goal_id} className="goal-card">
              <h3>{goal.year} год</h3>
              <div className="goal-progress-bar">
                <div
                  className="goal-progress-fill"
                  style={{ width: `${Math.min(goal.progress_percent, 100)}%` }}
                />
              </div>
              <div className="goal-stats">
                <span>
                  {goal.read_count} / {goal.target_count} книг
                </span>
                <span>{goal.progress_percent}%</span>
              </div>
              {goal.remaining > 0 ? (
                <p className="goal-remaining">
                  Осталось: {goal.remaining} книг
                </p>
              ) : (
                <p className="goal-done">🎉 Цель достигнута!</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default GoalsPage;