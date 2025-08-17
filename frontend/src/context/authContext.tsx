import { createContext } from 'react';
import type { User } from '../types/user';

export interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (token: string, userData: User) => void;
    logout: () => void;
}

// Создаем и экспортируем ТОЛЬКО объект контекста
export const AuthContext = createContext<AuthContextType | undefined>(undefined);