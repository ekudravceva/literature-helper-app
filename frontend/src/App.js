import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [backendStatus, setBackendStatus] = useState('Проверяем...');

  useEffect(() => {
    axios.get('/health')
      .then(response => {
        setBackendStatus(response.data.status);
      })
      .catch(error => {
        setBackendStatus('Бэкенд не отвечает');
      });
  }, []);

  return (
    <div className="App">
      <h1>Литературный помощник</h1>
      <p>Статус сервера: {backendStatus}</p>
    </div>
  );
}

export default App;