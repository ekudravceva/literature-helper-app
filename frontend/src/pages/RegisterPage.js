// import React, { useState } from 'react';
// import { useAuth } from '../services/AuthContext';
// import { Link, useNavigate } from 'react-router-dom';

// function RegisterPage() {
//   const { register } = useAuth();
//   const navigate = useNavigate();
//   const [username, setUsername] = useState('');
//   const [email, setEmail] = useState('');
//   const [password, setPassword] = useState('');
//   const [error, setError] = useState('');
//   const [loading, setLoading] = useState(false);

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setError('');
//     setLoading(true);
//     try {
//       await register(username, email, password);
//       navigate('/');  // ← редирект на главную
//     } catch (err) {
//       setError(err.response?.data?.detail || 'Ошибка регистрации');
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="auth-container">
//       <h1>Литературный помощник</h1>
//       <h2>Регистрация</h2>
//       <form onSubmit={handleSubmit} className="auth-form">
//         {error && <div className="error">{error}</div>}
//         <input
//           type="text"
//           placeholder="Имя пользователя"
//           value={username}
//           onChange={(e) => setUsername(e.target.value)}
//           required
//         />
//         <input
//           type="email"
//           placeholder="Email"
//           value={email}
//           onChange={(e) => setEmail(e.target.value)}
//           required
//         />
//         <input
//           type="password"
//           placeholder="Пароль"
//           value={password}
//           onChange={(e) => setPassword(e.target.value)}
//           required
//         />
//         <button type="submit" disabled={loading}>
//           {loading ? 'Регистрация...' : 'Зарегистрироваться'}
//         </button>
//       </form>
//       <p>
//         Уже есть аккаунт? <Link to="/login">Войти</Link>
//       </p>
//     </div>
//   );
// }

// export default RegisterPage;

import React, { useState } from 'react';
import { useAuth } from '../services/AuthContext';
import { Link, useNavigate } from 'react-router-dom';

// Правила валидации
const validateUsername = (value) => {
  if (!value.trim()) return 'Имя пользователя обязательно';
  if (value.length < 3) return 'Минимум 3 символа';
  if (value.length > 30) return 'Максимум 30 символов';
  if (!/^[a-zA-Zа-яА-ЯёЁ0-9_-]+$/.test(value)) return 'Только буквы, цифры, дефис и подчёркивание';
  return '';
};

const validateEmail = (value) => {
  if (!value.trim()) return 'Email обязателен';
  if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(value)) return 'Некорректный формат email';
  return '';
};

const validatePassword = (value) => {
  if (!value) return 'Пароль обязателен';
  if (value.length < 6) return 'Минимум 6 символов';
  if (value.trim() !== value) return 'Пароль не может начинаться или заканчиваться пробелом';
  if (!/[a-zA-Zа-яА-ЯёЁ]/.test(value)) return 'Должна быть хотя бы одна буква';
  if (!/\d/.test(value)) return 'Должна быть хотя бы одна цифра';
  return '';
};

function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const [usernameError, setUsernameError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [serverError, setServerError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleUsernameChange = (e) => {
    const value = e.target.value;
    setUsername(value);
    setUsernameError(validateUsername(value));
  };

  const handleEmailChange = (e) => {
    const value = e.target.value;
    setEmail(value);
    setEmailError(validateEmail(value));
  };

  const handlePasswordChange = (e) => {
    const value = e.target.value;
    setPassword(value);
    setPasswordError(validatePassword(value));
  };

  const isFormValid = () => {
    return (
      username.trim() &&
      email.trim() &&
      password &&
      !validateUsername(username) &&
      !validateEmail(email) &&
      !validatePassword(password)
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError('');

    // Финальная проверка
    const uErr = validateUsername(username);
    const eErr = validateEmail(email);
    const pErr = validatePassword(password);

    if (uErr || eErr || pErr) {
      setUsernameError(uErr);
      setEmailError(eErr);
      setPasswordError(pErr);
      return;
    }

    setLoading(true);
    try {
      await register(username.trim(), email.trim().toLowerCase(), password);
      navigate('/');
    } catch (err) {
      setServerError(err.response?.data?.detail || 'Ошибка регистрации');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h1>Литературный помощник</h1>
      <h2>Регистрация</h2>

      <form onSubmit={handleSubmit} className="auth-form">
        {serverError && <div className="error">{serverError}</div>}

        <div className="input-group">
          <input
            type="text"
            placeholder="Имя пользователя"
            value={username}
            onChange={handleUsernameChange}
            className={usernameError ? 'input-error' : ''}
            required
          />
          {usernameError && <span className="field-error">{usernameError}</span>}
        </div>

        <div className="input-group">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={handleEmailChange}
            className={emailError ? 'input-error' : ''}
            required
          />
          {emailError && <span className="field-error">{emailError}</span>}
        </div>

        <div className="input-group">
          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={handlePasswordChange}
            className={passwordError ? 'input-error' : ''}
            required
          />
          {passwordError && <span className="field-error">{passwordError}</span>}
        </div>

        <button type="submit" disabled={loading || !isFormValid()}>
          {loading ? 'Регистрирация...' : 'Зарегистрироваться'}
        </button>
      </form>

      <p>
        Уже есть аккаунт? <Link to="/login">Войти</Link>
      </p>
    </div>
  );
}

export default RegisterPage;