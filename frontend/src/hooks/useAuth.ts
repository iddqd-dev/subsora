import { useContext } from 'react';
import { AuthContext, type AuthContextType } from '../context/authContext';

export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);
    
    // Проверка, что хук используется внутри провайдера, остается
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    
    return context;
};