// import React, { useState } from 'react';
// import { useAuth } from '../services/AuthContext';
// import { Link, useNavigate } from 'react-router-dom';

// function LoginPage() {
//   const { login } = useAuth();
//   const navigate = useNavigate();
//   const [email, setEmail] = useState('');
//   const [password, setPassword] = useState('');
//   const [error, setError] = useState('');
//   const [loading, setLoading] = useState(false);

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setError('');
//     setLoading(true);
//     try {
//       await login(email, password);
//       navigate('/');  // ← редирект на главную
//     } catch (err) {
//       setError(err.response?.data?.detail || 'Ошибка входа');
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="auth-container">
//       <h1>Литературный помощник</h1>
//       <h2>Вход</h2>
//       <form onSubmit={handleSubmit} className="auth-form">
//         {error && <div className="error">{error}</div>}
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
//           {loading ? 'Вход...' : 'Войти'}
//         </button>
//       </form>
//       <p>
//         Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
//       </p>
//     </div>
//   );
// }

// export default LoginPage;

import React, { useState } from 'react';
import { useAuth } from '../services/AuthContext';
import { Link, useNavigate } from 'react-router-dom';

function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [serverError, setServerError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleEmailChange = (e) => {
    const value = e.target.value;
    setEmail(value);
    if (value && !/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(value)) {
      setEmailError('Некорректный формат email');
    } else {
      setEmailError('');
    }
  };

  const handlePasswordChange = (e) => {
    const value = e.target.value;
    setPassword(value);
    if (value && value.length < 6) {
      setPasswordError('Пароль не может быть короче 6 символов');
    } else {
      setPasswordError('');
    }
  };

  const isFormValid = () => {
    return email.trim() && password && !emailError && !passwordError;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError('');

    if (!email.trim()) {
      setEmailError('Email обязателен');
      return;
    }
    if (!password) {
      setPasswordError('Пароль обязателен');
      return;
    }

    setLoading(true);
    try {
      await login(email.trim().toLowerCase(), password);
      navigate('/');
    } catch (err) {
      setServerError(err.response?.data?.detail || 'Ошибка входа');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h1>Литературный помощник</h1>
      <h2>Вход</h2>

      <form onSubmit={handleSubmit} className="auth-form">
        {serverError && <div className="error">{serverError}</div>}

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
          {loading ? 'Вход...' : 'Войти'}
        </button>
      </form>

      <p>
        Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
      </p>
    </div>
  );
}

export default LoginPage;