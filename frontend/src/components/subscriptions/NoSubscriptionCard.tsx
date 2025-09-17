import React, { useState } from 'react';
import { Card, CardContent, Typography, Button, Box, TextField, Dialog, DialogTitle, DialogContent, DialogActions, DialogContentText } from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import CreditCardIcon from '@mui/icons-material/CreditCard';
import apiClient from '../../api/axios';
import type { Plan } from '../../types/plan';
import type { Transaction } from '../../types/transaction';

interface Props {
  plans: Plan[];
}

const NoSubscriptionCard: React.FC<Props> = ({ plans }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [couponCode, setCouponCode] = useState('');
  const [pendingModalOpen, setPendingModalOpen] = useState(false);
  const [pendingTransaction, setPendingTransaction] = useState<Transaction | null>(null);

  const handleSelectPlan = async (planId: number) => {
    if (isLoading) return;

    setIsLoading(true);
    try {
      // Prepare request body
      const requestBody = { plan_id: planId, coupon_code: couponCode.trim() || undefined };

      // Step 1: Initiate purchase
      const purchaseResponse = await apiClient.post('subscriptions/purchase', requestBody);
      const transaction = purchaseResponse.data;
      console.log('Purchase initiated:', transaction);

      // Step 2: Mock confirm payment (for testing)
      const confirmResponse = await apiClient.post(`transactions/${transaction.id}/confirm_payment_mock`);
      console.log('Purchase confirmed:', confirmResponse.data);

      // Show pending modal
      setPendingTransaction(transaction);
      setPendingModalOpen(true);
    } catch (error) {
      console.error('Error initiating purchase:', error);
      alert('Ошибка при инициации покупки. Попробуйте позже.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClosePendingModal = () => {
    setPendingModalOpen(false);
    setPendingTransaction(null);
    window.location.reload();
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
              fontSize: { xs: '1.125rem', md: '1.5rem' },
              color: 'warning.main'
            }}>
              У вас нет активной подписки
            </Typography>
          </Box>
          <Typography variant="body1" sx={{ fontSize: { xs: '0.875rem', md: '1rem' } , color: 'text.primary' }}>
            Выберите тарифный план, чтобы начать пользоваться всеми возможностями сервиса.
          </Typography>
        </CardContent>
      </Card>

      {/* Поле для кода купона */}
      <Box sx={{ mb: { xs: 2, md: 3 } }}>
        <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
          Есть промокод? Введите его для скидки:
        </Typography>
        <TextField
          fullWidth
          placeholder="Введите код купона"
          value={couponCode}
          onChange={(e) => setCouponCode(e.target.value)}
          variant="outlined"
          size="small"
          sx={{
            '& .MuiOutlinedInput-root': { borderRadius: 1 },
            maxWidth: { xs: '100%', md: 300 }
          }}
        />
      </Box>

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
                disabled={isLoading}
                sx={{ 
                  borderRadius: 1,
                  textTransform: 'none',
                  fontWeight: 600,
                  py: { xs: 0.75, md: 1.25 },
                  fontSize: { xs: '0.875rem', md: '1rem' }
                }}
              >
                {isLoading ? 'Обработка...' : 'Выбрать план'}
              </Button>
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* Модал для pending-транзакции */}
      <Dialog open={pendingModalOpen} onClose={handleClosePendingModal} maxWidth="sm" fullWidth>
        <DialogTitle>Транзакция создана</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Ваша транзакция #{pendingTransaction?.id} на сумму ${pendingTransaction?.amount.toFixed(2)} {pendingTransaction?.currency} инициирована.
            <br />
            <strong>Инструкции по оплате:</strong> Для тестирования оплатите вручную (например, через банковский перевод). После подтверждения статус обновится автоматически.
            <br />
            ID плана: {pendingTransaction?.plan_id}. Статус: {pendingTransaction?.status}.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePendingModal} color="primary">
            OK
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default NoSubscriptionCard;