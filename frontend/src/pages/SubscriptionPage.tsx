import React from 'react';
import { Box, Typography, CircularProgress, Alert, Container } from '@mui/material';
import ActiveSubscriptionCard from '../components/subscriptions/ActiveSubscriptionCard';
import NoSubscriptionCard from '../components/subscriptions/NoSubscriptionCard';
import PaymentsHistoryTable from '../components/subscriptions/PaymentsHistoryTable';

// Используем наши кастомные хуки
import { useSubscription } from '../hooks/useSubscription';
import { useTransactions } from '../hooks/useTransactions';
import { usePlans } from '../hooks/usePlans';

const SubscriptionPage: React.FC = () => {
    const { subscription, loading: subLoading, error: subError } = useSubscription();
    const { transactions, loading: transLoading, error: transError } = useTransactions();
    const { plans, loading: plansLoading, error: plansError } = usePlans();

    // Показываем загрузку, если хотя бы один запрос еще идет
    const isLoading = subLoading || transLoading || plansLoading;
    
    // Собираем все ошибки в одну
    const errors = [subError, transError, plansError].filter(Boolean);

    if (isLoading) {
        return (
            <Container maxWidth="lg" sx={{ py: { xs: 2, md: 4 } }}>
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
                        Загружаем данные подписки...
                    </Typography>
                </Box>
            </Container>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ py: { xs: 2, md: 4 } }}>
            {/* Заголовок страницы */}
            <Box sx={{ textAlign: 'center', mb: { xs: 4, md: 6 } }}>
                <Typography variant="h4" sx={{ 
                    fontWeight: 600,
                    color: 'text.primary',
                    mb: 1,
                    fontSize: { xs: '1.5rem', md: '2.125rem' }
                }}>
                    Управление подпиской
                </Typography>
                <Typography variant="h6" color="text.secondary" sx={{ 
                    fontWeight: 400,
                    fontSize: { xs: '1rem', md: '1.25rem' }
                }}>
                    {subscription ? 'Ваша активная подписка' : 'Выберите подходящий тариф'}
                </Typography>
            </Box>

            {/* Показываем ошибки, если есть */}
            {errors.length > 0 && (
                <Alert severity="error" sx={{ mb: { xs: 3, md: 4 }, borderRadius: 2 }}>
                    {errors.join('. ')}
                </Alert>
            )}

            {/* Блок подписки */}
            <Box sx={{ mb: { xs: 4, md: 6 } }}>
                {subscription ? (
                    <ActiveSubscriptionCard subscription={subscription} plans={plans} />
                ) : (
                    <NoSubscriptionCard plans={plans} />
                )}
            </Box>

            {/* История платежей */}
            <Box>
                <Typography variant="h5" sx={{ 
                    fontWeight: 600,
                    color: 'text.primary',
                    mb: { xs: 2, md: 3 },
                    fontSize: { xs: '1.25rem', md: '1.5rem' }
                }}>
                    История платежей
                </Typography>
                <PaymentsHistoryTable transactions={transactions} />
            </Box>
        </Container>
    );
};

export default SubscriptionPage;