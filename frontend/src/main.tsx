import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthProvider.tsx';
import { useAuth } from './hooks/useAuth.ts'; // Добавляем импорт хука

// Импорты для темы
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';
import './index.css';

import Layout from './components/Layout.tsx';
import LoginPage from './pages/LoginPage.tsx';
import DashboardPage from './pages/DashboardPage.tsx';
import SubscriptionPage from './pages/SubscriptionPage.tsx';
import ReferralsPage from './pages/Referralspage.tsx';

// Создадим заглушки для других страниц
const ServersPage = () => <h1>Серверы</h1>;
const StatsPage = () => <h1>Стата</h1>;
const SettingsPage = () => <h1>Настройки</h1>;
const ProfilePage = () => <h1>Профиль</h1>;

// ИСПРАВЛЕННЫЙ ProtectedRoute - теперь использует useAuth вместо localStorage
const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const { user, loading } = useAuth();
  
  console.log('🛡️ ProtectedRoute check:', { user: !!user, loading });
  
  // Показываем загрузку пока идет проверка авторизации
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh' 
      }}>
        Проверка авторизации...
      </div>
    );
  }
  
  // Если пользователь не авторизован, перенаправляем на логин
  if (!user) {
    console.log('🛡️ ProtectedRoute: redirecting to login');
    return <Navigate to="/login" replace />;
  }
  
  console.log('🛡️ ProtectedRoute: user authenticated, rendering children');
  return children;
};

// Компонент для публичных роутов (опционально)
const PublicRoute = ({ children }: { children: JSX.Element }) => {
  const { user, loading } = useAuth();
  
  console.log('🌐 PublicRoute check:', { user: !!user, loading });
  
  // Показываем загрузку пока идет проверка авторизации
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh' 
      }}>
        Загрузка...
      </div>
    );
  }
  
  // Если пользователь уже авторизован, перенаправляем на dashboard
  if (user) {
    console.log('🌐 PublicRoute: authenticated user, redirecting to dashboard');
    return <Navigate to="/dashboard" replace />;
  }
  
  console.log('🌐 PublicRoute: rendering login page');
  return children;
};

// Компонент с роутами (должен быть внутри AuthProvider)
const AppRoutes = () => {
  return (
    <Routes>
      {/* Публичный роут для страницы логина */}
      <Route 
        path="/login" 
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        } 
      />

      {/* Группа защищенных роутов с Layout */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        {/* Дочерние роуты */}
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="servers" element={<ServersPage />} />
        <Route path="subscriptions" element={<SubscriptionPage />} />
        <Route path="stats" element={<StatsPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="referrals" element={<ReferralsPage />} />
        {/* Главный роут */}
        <Route index element={<Navigate to="/dashboard" replace />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<div>Страница не найдена</div>} />
    </Routes>
  );
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  </React.StrictMode>
);