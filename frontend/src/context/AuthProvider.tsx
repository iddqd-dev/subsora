// AuthProvider.tsx
import { useState, useEffect, type ReactNode } from 'react';
import apiClient from '../api/axios';
import { AuthContext } from './authContext';
import type { User } from '../types/user';

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const initializeAuth = async () => {
            try {
                const token = localStorage.getItem('token');
                
                if (token) {
                    // Устанавливаем токен в заголовки
                    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
                    
                    // Проверяем валидность токена
                    const response = await apiClient.get<User>('/users/me');
                    setUser(response.data);
                } else {
                    // Токена нет, пользователь не авторизован
                    setUser(null);
                }
            } catch (error) {
                // Токен невалидный или произошла ошибка
                console.error('Auth initialization error:', error);
                localStorage.removeItem('token');
                delete apiClient.defaults.headers.common['Authorization'];
                setUser(null);
            } finally {
                // КРИТИЧЕСКИ ВАЖНО: всегда устанавливаем loading в false
                setLoading(false);
            }
        };

        initializeAuth();
    }, []);

    const login = (token: string, userData: User) => {
        localStorage.setItem('token', token);
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        setUser(userData);
    };

    const logout = () => {
        localStorage.removeItem('token');
        delete apiClient.defaults.headers.common['Authorization'];
        setUser(null);
    };

    const value = { 
        user, 
        loading, 
        login, 
        logout 
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthProvider;