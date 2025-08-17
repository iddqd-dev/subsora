import React from 'react';
import { Card, CardContent, Typography, Button, Box, Select, MenuItem, FormControl, InputLabel, LinearProgress} from '@mui/material';
import CreditCardIcon from '@mui/icons-material/CreditCard';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import type { Subscription } from '../../types/subscription';
import type { Plan } from '../../types/plan';

interface Props {
  subscription: Subscription;
  plans: Plan[];
}

const ActiveSubscriptionCard: React.FC<Props> = ({ subscription, plans }) => {
  // Логика смены плана и т.д. будет здесь
  
  const getSubscriptionProgress = () => {
    const startDate = new Date(subscription.start_date);
    const endDate = new Date(subscription.end_date);
    const now = new Date();
    
    const totalDuration = endDate.getTime() - startDate.getTime();
    const elapsed = now.getTime() - startDate.getTime();
    
    return Math.min(Math.max((elapsed / totalDuration) * 100, 0), 100);
  };

  const getDaysRemaining = () => {
    const endDate = new Date(subscription.end_date);
    const now = new Date();
    const diffTime = endDate.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return Math.max(diffDays, 0);
  };

  return (
    <Card sx={{ 
      boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
      borderRadius: 2,
      transition: 'all 0.2s ease',
      '&:hover': { 
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        transform: 'translateY(-2px)',
      }
    }}>
      <CardContent sx={{ p: { xs: 2.5, md: 4 } }}>
        {/* Заголовок с иконкой */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: { xs: 1.5, md: 3 } }}>
          <Box sx={{ 
            p: { xs: 0.75, md: 1.5 }, 
            borderRadius: 2, 
            bgcolor: 'primary.light', 
            color: 'primary.main', 
            mr: 2, 
            display: 'inline-flex' 
          }}>
            <CreditCardIcon sx={{ fontSize: { xs: 18, md: 24 } }} />
          </Box>
          <Box>
            <Typography variant="h5" sx={{ 
              fontWeight: 600, 
              color: 'text.primary',
              fontSize: { xs: '1.125rem', md: '1.5rem' }
            }}>
              Ваша подписка
            </Typography>
          </Box>
        </Box>

        {/* Информация о подписке */}
        <Box sx={{ mb: { xs: 2, md: 4 } }}>
          <Typography variant="h6" sx={{ 
            mb: 1, 
            color: 'primary.main', 
            fontWeight: 600,
            fontSize: { xs: '1rem', md: '1.25rem' }
          }}>
            {subscription.plan.name}
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <CalendarTodayIcon sx={{ fontSize: 16, color: 'text.secondary', mr: 1 }} />
            <Typography variant="body2" color="text.secondary" sx={{ fontSize: { xs: '0.875rem', md: '1rem' } }}>
              Активна до: {new Date(subscription.end_date).toLocaleDateString()}
            </Typography>
          </Box>

          {/* Прогресс подписки */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="caption" color="text.secondary" sx={{ fontSize: { xs: '0.75rem', md: '0.875rem' } }}>
                Прогресс подписки
              </Typography>
              <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ fontSize: { xs: '0.75rem', md: '0.875rem' } }}>
                {getDaysRemaining()} дней осталось
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={getSubscriptionProgress()} 
              sx={{ 
                height: 6, 
                borderRadius: 3,
                bgcolor: 'rgba(25, 118, 210, 0.1)',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 3,
                  bgcolor: 'primary.main'
                }
              }} 
            />
          </Box>
        </Box>

        {/* Дропдаун смены тарифа */}
        <FormControl fullWidth sx={{ mb: { xs: 1.5, md: 3 } }}>
          <InputLabel id="change-plan-label" sx={{ fontSize: { xs: '0.875rem', md: '1rem' } }}>
            Сменить тариф
          </InputLabel>
          <Select
            labelId="change-plan-label"
            defaultValue={subscription.plan_id}
            label="Сменить тариф"
            sx={{ borderRadius: 1 }}
          >
            {plans.map(plan => (
              <MenuItem key={plan.id} value={plan.id} sx={{ fontSize: { xs: '0.875rem', md: '1rem' } }}>
                {plan.name} - ${plan.price}/{plan.duration_days} дней
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Кнопки действий */}
        <Box sx={{ 
          display: 'flex', 
          gap: { xs: 1, md: 2 }, 
          flexDirection: { xs: 'column', sm: 'row' },
          flexWrap: 'wrap' 
        }}>
          <Button 
            variant="contained" 
            color="primary"
            sx={{ 
              borderRadius: 1,
              textTransform: 'none',
              fontWeight: 600,
              py: { xs: 0.75, md: 1.25 },
              px: { xs: 1.5, md: 3 },
              fontSize: { xs: '0.875rem', md: '1rem' }
            }}
          >
            Продлить подписку
          </Button>
          <Button 
            variant="outlined" 
            color="error"
            sx={{ 
              borderRadius: 1,
              textTransform: 'none',
              fontWeight: 600,
              py: { xs: 0.75, md: 1.25 },
              px: { xs: 1.5, md: 3 },
              fontSize: { xs: '0.875rem', md: '1rem' }
            }}
          >
            Отменить подписку
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ActiveSubscriptionCard;