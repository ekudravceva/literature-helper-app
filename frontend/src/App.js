import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './services/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import SwipePage from './pages/SwipePage';
import RecommendationsPage from './pages/RecommendationsPage';
import BookshelfPage from './pages/BookshelfPage';
import GoalsPage from './pages/GoalsPage';
import './App.css';

function NavBar() {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <nav className="navbar">
      <Link to="/" className="nav-link">Свайпы</Link>
      <Link to="/recommendations" className="nav-link">Рекомендации</Link>
      <Link to="/bookshelf" className="nav-link">Дневник</Link>
      <Link to="/goals" className="nav-link">Цели</Link>
      <button onClick={logout} className="nav-logout">Выйти</button>
    </nav>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="App">
          <NavBar />
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <SwipePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/recommendations"
              element={
                <ProtectedRoute>
                  <RecommendationsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/bookshelf"
              element={
                <ProtectedRoute>
                  <BookshelfPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/goals"
              element={
                <ProtectedRoute>
                  <GoalsPage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;