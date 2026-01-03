import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'https://subsora.mywire.org:48080/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Interceptor для запросов (уже есть) ---
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// --- НОВЫЙ Interceptor для ответов ---
apiClient.interceptors.response.use(
  // 1. Функция, которая выполняется для УСПЕШНЫХ ответов (статус 2xx)
  (response) => {
    // Ничего не делаем, просто возвращаем ответ
    return response;
  },
  // 2. Функция, которая выполняется для ОШИБОЧНЫХ ответов
  (error) => {
    // Проверяем, есть ли вообще объект ответа
    if (error.response) {
      // Если сервер вернул статус 401 Unauthorized
      if (error.response.status === 401) {
        // Удаляем невалидный токен из хранилища
        localStorage.removeItem('accessToken');

        // Перезагружаем страницу. Роутер сам перенаправит на /login,
        // так как токена больше нет. Это самый простой и надежный способ
        // сбросить состояние всего приложения.
        window.location.href = '/login';

        console.error("Unauthorized! Logging out.");
      }
    }

    // Пробрасываем ошибку дальше, чтобы ее могли поймать в .catch()
    return Promise.reject(error);
  }
);


export default apiClient;