// LoginPage.tsx - убираем всю логику редиректа
import React, { useState } from 'react';
import apiClient from '../api/axios';
import { useAuth } from '../hooks/useAuth';
import type { User } from '../types/user';

import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Container, 
  Alert, 
  Paper,
  CircularProgress
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';

const LoginPage: React.FC = () => {
    const { login } = useAuth(); // Убираем user и loading - они нам здесь не нужны

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    // УБИРАЕМ весь useEffect с редиректом!
    // Пусть PublicRoute в main.tsx занимается редиректом

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setLoading(true);
        setError(null);

        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        try {
            console.log('🔐 Attempting login...');
            
            const tokenResponse = await apiClient.post('/auth/login', formData, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            });
            const accessToken = tokenResponse.data.access_token;
            
            apiClient.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;

            const userResponse = await apiClient.get<User>('/users/me');
            
            console.log('🔐 Login successful, updating auth state...');

            // Обновляем состояние через контекст
            login(accessToken, userResponse.data);
            
            // НЕ делаем navigate! Пусть PublicRoute автоматически перенаправит
            console.log('🔐 Auth state updated, waiting for automatic redirect...');

        } catch (err: any) {
            console.error('🔐 Login error:', err);
            const errorMessage = err.response?.data?.detail || 'Неправильный email или пароль.';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    console.log('📝 Rendering LoginPage form');

    return (
        <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                minHeight: '100vh',
                bgcolor: 'background.default',
                p: 2,
            }}
        >
            <Container component="main" maxWidth="xs">
                <Paper
                    elevation={0}
                    variant="outlined"
                    sx={{
                        p: { xs: 3, sm: 4 },
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        borderRadius: 3,
                        border: '1px solid',
                        borderColor: 'divider'
                    }}
                >
                    <Box sx={{
                        width: 56,
                        height: 56,
                        borderRadius: '50%',
                        bgcolor: 'primary.light',
                        color: 'primary.main',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mb: 2,
                    }}>
                        <LockOutlinedIcon fontSize="large" />
                    </Box>

                    <Typography component="h1" variant="h5" fontWeight={600}>
                        Вход в аккаунт
                    </Typography>
                    
                    <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 3, width: '100%' }}>
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            id="email"
                            label="Email"
                            name="email"
                            autoComplete="email"
                            autoFocus
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            disabled={loading}
                        />
                        <TextField
                            margin="normal"
                            required
                            fullWidth
                            name="password"
                            label="Пароль"
                            type="password"
                            id="password"
                            autoComplete="current-password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            disabled={loading}
                        />

                        {error && (
                            <Alert severity="error" sx={{ mt: 2, width: '100%' }}>
                                {error}
                            </Alert>
                        )}
                        
                        <Box sx={{ position: 'relative', mt: 3, mb: 2 }}>
                            <Button
                                type="submit"
                                fullWidth
                                variant="contained"
                                size="large"
                                sx={{ py: 1.5 }}
                                disabled={loading}
                            >
                                Войти
                            </Button>
                            {loading && (
                                <CircularProgress
                                    size={24}
                                    sx={{
                                        color: 'primary.contrastText',
                                        position: 'absolute',
                                        top: '50%',
                                        left: '50%',
                                        marginTop: '-12px',
                                        marginLeft: '-12px',
                                    }}
                                />
                            )}
                        </Box>
                    </Box>
                </Paper>
            </Container>
        </Box>
    );
};

export default LoginPage;