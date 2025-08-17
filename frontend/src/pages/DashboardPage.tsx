// frontend/src/pages/DashboardPage.tsx
import React from 'react';
import { 
  Box, Typography, Button, CircularProgress, 
  Card, CardContent, Chip, Alert, Container, LinearProgress
} from '@mui/material';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import CancelOutlinedIcon from '@mui/icons-material/CancelOutlined';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import PeopleIcon from '@mui/icons-material/People';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { useAuth } from '../hooks/useAuth';
import { useSubscription } from '../hooks/useSubscription';
import { useReferrals } from '../hooks/useReferrals';

const DashboardPage: React.FC = () => {
  const { user, loading: authLoading } = useAuth();
  const { subscription, loading: subLoading, error: subError } = useSubscription();
  const { referralsCount, earnings, loading: refLoading, error: refError } = useReferrals();

  // Показываем загрузку, если хотя бы один запрос еще идет
  const isLoading = authLoading || subLoading || refLoading;
  
  // Собираем все ошибки
  const errors = [subError, refError].filter(Boolean);

  if (isLoading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '50vh',
        gap: 2
      }}>
        <CircularProgress size={60} />
        <Typography variant="body1" color="text.secondary">
          Загружаем данные дашборда...
        </Typography>
      </Box>
    );
  }

  if (errors.length > 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ borderRadius: 2 }}>
          {errors.join('. ')}
        </Alert>
      </Container>
    );
  }

  // Определяем статус подписки
  const getSubscriptionStatus = () => {
    if (!subscription) return 'inactive';
    const endDate = new Date(subscription.end_date);
    const now = new Date();
    return endDate > now ? 'active' : 'expired';
  };

  const subscriptionStatus = getSubscriptionStatus();

  const getSubscriptionStatusChip = () => {
    switch (subscriptionStatus) {
      case 'active':
        return (
          <Chip 
            icon={<CheckCircleOutlineIcon />} 
            label="Активна" 
            color="success" 
            variant="filled"
            size="small"
            sx={{ fontWeight: 500 }}
          />
        );
      case 'expired':
        return (
          <Chip 
            icon={<CancelOutlinedIcon />} 
            label="Истекла" 
            color="error" 
            variant="filled"
            size="small"
            sx={{ fontWeight: 500 }}
          />
        );
      default:
        return (
          <Chip 
            icon={<CancelOutlinedIcon />} 
            label="Неактивна" 
            color="default" 
            variant="filled"
            size="small"
            sx={{ fontWeight: 500 }}
          />
        );
    }
  };

  const getSubscriptionProgress = () => {
    if (!subscription) return 0;
    
    const startDate = new Date(subscription.start_date);
    const endDate = new Date(subscription.end_date);
    const now = new Date();
    
    const totalDuration = endDate.getTime() - startDate.getTime();
    const elapsed = now.getTime() - startDate.getTime();
    
    return Math.min(Math.max((elapsed / totalDuration) * 100, 0), 100);
  };

  const getDaysRemaining = () => {
    if (!subscription) return 0;
    
    const endDate = new Date(subscription.end_date);
    const now = new Date();
    const diffTime = endDate.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return Math.max(diffDays, 0);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Заголовок */}
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography 
          variant="h4" 
          sx={{ 
            fontWeight: 600,
            color: 'text.primary',
            mb: 1
          }}
        >
          Добро пожаловать!
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ fontWeight: 400 }}>
          {user?.full_name || 'Пользователь'}
        </Typography>
      </Box>
      
      {/* Карточки статистики */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' }, gap: 3, mb: 6 }}>
        {/* Карточка подписки */}
        <Card sx={{
          height: 280,
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
          borderRadius: 2,
          transition: 'all 0.2s ease',
          '&:hover': { 
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            transform: 'translateY(-2px)',
          }
        }}>
          <CardContent sx={{ 
            flexGrow: 1, 
            display: 'flex', 
            flexDirection: 'column',
            p: 3
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Box sx={{ 
                p: 1, 
                borderRadius: 1, 
                bgcolor: 'primary.main', 
                color: 'white',
                mr: 2
              }}>
                <AttachMoneyIcon sx={{ fontSize: 20 }} />
              </Box>
              <Typography variant="h6" fontWeight={600} color="text.primary">
                Подписка
              </Typography>
            </Box>
            
            <Box sx={{ mb: 2 }}>
              {getSubscriptionStatusChip()}
            </Box>
            
            {subscription ? (
              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="h6" sx={{ mb: 1, fontWeight: 600, color: 'primary.main' }}>
                  {subscription.plan.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Активна до: {new Date(subscription.end_date).toLocaleDateString()}
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      Прогресс подписки
                    </Typography>
                    <Typography variant="caption" color="text.secondary" fontWeight={600}>
                      {getDaysRemaining()} дней осталось
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={getSubscriptionProgress()} 
                    sx={{ 
                      height: 4, 
                      borderRadius: 2,
                      bgcolor: 'rgba(25, 118, 210, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 2,
                        bgcolor: 'primary.main'
                      }
                    }} 
                  />
                </Box>
                
                <Typography variant="body2" color="text.secondary">
                  Полный доступ ко всем функциям
                </Typography>
              </Box>
            ) : (
              <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  Выберите тарифный план для доступа ко всем функциям
                </Typography>
              </Box>
            )}
            
            {subscriptionStatus !== 'active' && (
              <Button 
                variant="contained" 
                fullWidth
                size="medium"
                sx={{ 
                  mt: 'auto',
                  py: 1,
                  borderRadius: 1,
                  textTransform: 'none',
                  fontWeight: 600
                }}
                href="/subscriptions"
              >
                Оформить подписку
              </Button>
            )}
          </CardContent>
        </Card>

        {/* Карточка рефералов */}
        <Card sx={{
          height: 280,
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
          borderRadius: 2,
          transition: 'all 0.2s ease',
          '&:hover': { 
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            transform: 'translateY(-2px)',
          }
        }}>
          <CardContent sx={{ 
            flexGrow: 1, 
            display: 'flex', 
            flexDirection: 'column',
            justifyContent: 'space-between',
            textAlign: 'center',
            p: 3
          }}>
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
                <Box sx={{ 
                  p: 1, 
                  borderRadius: 1, 
                  bgcolor: 'success.main', 
                  color: 'white',
                  mr: 2
                }}>
                  <PeopleIcon sx={{ fontSize: 20 }} />
                </Box>
                <Typography variant="h6" fontWeight={600} color="text.primary">
                  Рефералы
                </Typography>
              </Box>
              <Typography variant="h3" color="success.main" sx={{ mb: 1, fontWeight: 700 }}>
                {referralsCount}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Всего приглашенных пользователей
              </Typography>
            </Box>
            
            <Button 
              variant="outlined" 
              size="medium"
              sx={{ 
                borderRadius: 1,
                textTransform: 'none',
                fontWeight: 600,
                borderColor: 'success.main',
                color: 'success.main',
                '&:hover': {
                  borderColor: 'success.dark',
                  backgroundColor: 'rgba(76, 175, 80, 0.04)'
                }
              }}
              href="/referrals"
            >
              Пригласить друзей
            </Button>
          </CardContent>
        </Card>

        {/* Карточка заработка */}
        <Card sx={{
          height: 280,
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
          borderRadius: 2,
          transition: 'all 0.2s ease',
          '&:hover': { 
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            transform: 'translateY(-2px)',
          }
        }}>
          <CardContent sx={{ 
            flexGrow: 1, 
            display: 'flex', 
            flexDirection: 'column',
            justifyContent: 'space-between',
            textAlign: 'center',
            p: 3
          }}>
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
                <Box sx={{ 
                  p: 1, 
                  borderRadius: 1, 
                  bgcolor: 'warning.main', 
                  color: 'white',
                  mr: 2
                }}>
                  <TrendingUpIcon sx={{ fontSize: 20 }} />
                </Box>
                <Typography variant="h6" fontWeight={600} color="text.primary">
                  Заработок
                </Typography>
              </Box>
              <Typography variant="h3" color="warning.main" sx={{ mb: 1, fontWeight: 700 }}>
                ${earnings.toFixed(2)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Общий доход с рефералов
              </Typography>
            </Box>
            
            <Button 
              variant="outlined" 
              size="medium"
              sx={{ 
                borderRadius: 1,
                textTransform: 'none',
                fontWeight: 600,
                borderColor: 'warning.main',
                color: 'warning.main',
                '&:hover': {
                  borderColor: 'warning.dark',
                  backgroundColor: 'rgba(255, 152, 0, 0.04)'
                }
              }}
              href="/payments"
            >
              История платежей
            </Button>
          </CardContent>
        </Card>
      </Box>

      {/* Быстрые действия */}
      <Card sx={{
        boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
        borderRadius: 2,
        transition: 'all 0.2s ease',
        '&:hover': { 
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          transform: 'translateY(-2px)',
        }
      }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom align="center" sx={{ mb: 4, fontWeight: 600, color: 'text.primary' }}>
            Быстрые действия
          </Typography>
          <Box sx={{ 
            display: 'flex', 
            gap: 2, 
            flexWrap: 'wrap',
            justifyContent: 'center'
          }}>
            <Button 
              variant="outlined" 
              size="large"
              sx={{ 
                minWidth: 180,
                py: 1.5,
                borderRadius: 1,
                textTransform: 'none',
                fontWeight: 600,
                '&:hover': {
                  transform: 'translateY(-1px)',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                }
              }}
              href="/subscriptions"
              endIcon={<ArrowForwardIcon />}
            >
              Управление подпиской
            </Button>
            <Button 
              variant="outlined" 
              size="large"
              sx={{ 
                minWidth: 180,
                py: 1.5,
                borderRadius: 1,
                textTransform: 'none',
                fontWeight: 600,
                '&:hover': {
                  transform: 'translateY(-1px)',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                }
              }}
              href="/referrals"
              endIcon={<ArrowForwardIcon />}
            >
              Пригласить друзей
            </Button>
            <Button 
              variant="outlined" 
              size="large"
              sx={{ 
                minWidth: 180,
                py: 1.5,
                borderRadius: 1,
                textTransform: 'none',
                fontWeight: 600,
                '&:hover': {
                  transform: 'translateY(-1px)',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                }
              }}
              href="/payments"
              endIcon={<ArrowForwardIcon />}
            >
              История платежей
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
};

export default DashboardPage;