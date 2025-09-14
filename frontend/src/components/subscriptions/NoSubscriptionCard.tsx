import React from 'react';
import { Card, CardContent, Typography, Button, Box } from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import CreditCardIcon from '@mui/icons-material/CreditCard';
import type { Plan } from '../../types/plan';

interface Props {
  plans: Plan[];
}

const NoSubscriptionCard: React.FC<Props> = ({ plans }) => {
  const handleSelectPlan = (planId: number) => {
    // Здесь будет логика покупки подписки
    console.log(`Выбран план с ID: ${planId}`);
  };

  return (
    <Box sx={{ mb: { xs: 3, md: 4 } }}>
      {/* Предупреждение о отсутствии подписки */}
      <Card sx={{ 
        mb: { xs: 2, md: 3 }, 
        backgroundColor: 'warning.light', 
        color: 'warning.contrastText',
        boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
        borderRadius: 2
      }}>
        <CardContent sx={{ p: { xs: 2.5, md: 4 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box sx={{ 
              p: 1, 
              borderRadius: 2, 
              bgcolor: 'warning.main', 
              color: 'white',
              mr: 2,
              display: 'inline-flex'
            }}>
              <WarningIcon sx={{ fontSize: { xs: 18, md: 24 } }} />
            </Box>
            <Typography variant="h5" component="div" sx={{ 
              fontWeight: 600,
              fontSize: { xs: '1.125rem', md: '1.5rem' }
            }}>
              У вас нет активной подписки
            </Typography>
          </Box>
          <Typography variant="body1" sx={{ fontSize: { xs: '0.875rem', md: '1rem' } , color: 'warning.contrastText' }}>
            Выберите тарифный план, чтобы начать пользоваться всеми возможностями сервиса.
          </Typography>
        </CardContent>
      </Card>

      {/* Заголовок тарифов */}
      <Typography variant="h5" gutterBottom sx={{ 
        fontWeight: 600,
        fontSize: { xs: '1.125rem', md: '1.5rem' },
        mb: { xs: 2, md: 3 }
      }}>
        Доступные тарифы
      </Typography>
      
      {/* Сетка тарифов */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }, 
        gap: { xs: 2, md: 3 } 
      }}>
        {plans.filter(plan => plan.is_active).map((plan) => (
          <Card key={plan.id} sx={{
            boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
            borderRadius: 2,
            transition: 'all 0.2s ease',
            '&:hover': { 
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              transform: 'translateY(-2px)',
            }
          }}>
            <CardContent sx={{ p: { xs: 2.5, md: 4 } }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Box sx={{ 
                  p: 1, 
                  borderRadius: 2, 
                  bgcolor: 'primary.light', 
                  color: 'primary.main',
                  mr: 2,
                  display: 'inline-flex'
                }}>
                  <CreditCardIcon sx={{ fontSize: { xs: 16, md: 20 } }} />
                </Box>
                <Typography variant="h6" component="div" sx={{ 
                  fontWeight: 600,
                  fontSize: { xs: '1rem', md: '1.25rem' }
                }}>
                  {plan.name}
                </Typography>
              </Box>
              
              <Typography variant="h4" color="primary" gutterBottom sx={{ 
                fontWeight: 700,
                fontSize: { xs: '1.5rem', md: '2.125rem' }
              }}>
                ${plan.price}
                <Typography component="span" variant="body2" color="text.secondary" sx={{ 
                  fontSize: { xs: '0.75rem', md: '1rem' }
                }}>
                  /{plan.duration_days} дней
                </Typography>
              </Typography>
              
              <Typography variant="body2" color="text.secondary" sx={{ 
                mb: { xs: 2, md: 3 },
                fontSize: { xs: '0.875rem', md: '1rem' }
              }}>
                {plan.description}
              </Typography>
              
              <Button 
                variant="contained" 
                fullWidth
                onClick={() => handleSelectPlan(plan.id)}
                sx={{ 
                  borderRadius: 1,
                  textTransform: 'none',
                  fontWeight: 600,
                  py: { xs: 0.75, md: 1.25 },
                  fontSize: { xs: '0.875rem', md: '1rem' }
                }}
              >
                Выбрать план
              </Button>
            </CardContent>
          </Card>
        ))}
      </Box>
    </Box>
  );
};

export default NoSubscriptionCard;