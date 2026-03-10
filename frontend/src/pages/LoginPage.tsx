import React, { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Paper,
  TextField,
  Typography,
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';

import apiClient from '../api/axios';
import { useAuth } from '../hooks/useAuth';
import type { User } from '../types/user';

type BootstrapStatus = {
  needs_bootstrap: boolean;
};

const passwordPattern = /^(?=.*[A-Za-z])(?=.*\d).{8,}$/;

const LoginPage: React.FC = () => {
  const { login } = useAuth();

  const [bootstrapLoading, setBootstrapLoading] = useState(true);
  const [needsBootstrap, setNeedsBootstrap] = useState(false);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadBootstrapStatus = async () => {
      try {
        const response = await apiClient.get<BootstrapStatus>('/misc/bootstrap-status');
        setNeedsBootstrap(Boolean(response.data?.needs_bootstrap));
      } catch {
        setNeedsBootstrap(false);
      } finally {
        setBootstrapLoading(false);
      }
    };

    void loadBootstrapStatus();
  }, []);

  const finishAuth = async (accessToken: string) => {
    apiClient.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
    const userResponse = await apiClient.get<User>('/users/me');
    login(accessToken, userResponse.data);
  };

  const handleLoginSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new URLSearchParams();
    formData.append('username', email.trim());
    formData.append('password', password);

    try {
      const tokenResponse = await apiClient.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      const accessToken: string = tokenResponse.data.access_token;
      await finishAuth(accessToken);
    } catch (err: any) {
      const errorMessage =
        err?.response?.data?.detail ?? 'Invalid email or password.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleBootstrapSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    const normalizedEmail = email.trim().toLowerCase();
    const normalizedFullName = fullName.trim();

    if (!normalizedFullName) {
      setError('Full name is required.');
      return;
    }
    if (!passwordPattern.test(password)) {
      setError('Password must be at least 8 characters and include letters and numbers.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post('/misc/bootstrap-admin', {
        email: normalizedEmail,
        password,
        full_name: normalizedFullName,
      });
      const accessToken: string = response.data.access_token;
      await finishAuth(accessToken);
    } catch (err: any) {
      const errorMessage =
        err?.response?.data?.detail ?? 'Failed to complete initial setup.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (bootstrapLoading) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

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
            borderColor: 'divider',
          }}
        >
          <Box
            sx={{
              width: 56,
              height: 56,
              borderRadius: '50%',
              bgcolor: 'primary.light',
              color: 'primary.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mb: 2,
            }}
          >
            <LockOutlinedIcon fontSize="large" />
          </Box>

          <Typography component="h1" variant="h5" fontWeight={600}>
            {needsBootstrap ? 'Initial Setup' : 'Sign In'}
          </Typography>

          <Box
            component="form"
            onSubmit={needsBootstrap ? handleBootstrapSubmit : handleLoginSubmit}
            noValidate
            sx={{ mt: 3, width: '100%' }}
          >
            {needsBootstrap && (
              <TextField
                margin="normal"
                required
                fullWidth
                id="fullName"
                label="Full Name"
                name="fullName"
                autoComplete="name"
                autoFocus
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                disabled={loading}
              />
            )}

            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email"
              name="email"
              autoComplete="email"
              autoFocus={!needsBootstrap}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
            />

            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete={needsBootstrap ? 'new-password' : 'current-password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
            />

            {needsBootstrap && (
              <TextField
                margin="normal"
                required
                fullWidth
                name="confirmPassword"
                label="Confirm Password"
                type="password"
                id="confirmPassword"
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={loading}
              />
            )}

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
                {needsBootstrap ? 'Create Admin' : 'Sign In'}
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
