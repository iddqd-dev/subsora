import { useState } from 'react';
import { Container, Box, Typography, Stack, Snackbar, Alert, CircularProgress } from '@mui/material';
import { useAuth } from '../hooks/useAuth';
import { useReferrals } from '../hooks/useReferrals';
import { useReferralTiers } from '../hooks/useReferralTiers';

// Импортируем наши новые компоненты и константы
import { ReferralStatusCard } from '../components/referrals/ReferralStatusCard';
import { ReferralLinkCard } from '../components/referrals/ReferralLinkCard';
import { ReferralsTable } from '../components/referrals/ReferralsTable';

const ReferralsPage: React.FC = () => {
  const { user } = useAuth();
  const { referrals, referralsCount, loading: referralsLoading, error: referralsError } = useReferrals();
  const { tiers, loading: tiersLoading, error: tiersError } = useReferralTiers();
  
  const [copySuccess, setCopySuccess] = useState(false);

  const isLoading = referralsLoading || tiersLoading;
  const error = referralsError || tiersError;

  // --- Логика вычислений ---
  const referralCode = user?.id ? `VPN${user.id.toString().padStart(6, '0')}` : 'VPN000000';
  const referralLink = `https://subsora-vpn.com/signup?ref=${referralCode}`;

  const getCurrentLevel = () => {
    // Ищем подходящий уровень с конца, чтобы найти самый высокий достигнутый
    for (let i = tiers.length - 1; i >= 0; i--) {
      if (referralsCount >= tiers[i].referrals) {
        return tiers[i];
      }
    }
    // Если уровни еще не загрузились или что-то пошло не так
    return tiers[0] || { referrals: 0, discount: 0, title: 'Загрузка...', Icon: () => null, color: 'grey' };
  };


  const getNextLevel = () => {
    const currentLevel = getCurrentLevel();
    const currentIndex = tiers.findIndex(level => level.referrals === currentLevel.referrals);
    return currentIndex < tiers.length - 1 ? tiers[currentIndex + 1] : null;
  };

 const currentLevel = isLoading ? getCurrentLevel() : getCurrentLevel();
  const nextLevel = isLoading ? null : getNextLevel()

  const getProgressToNextLevel = () => {
    if (isLoading || !nextLevel) return 0;
    const referralsSinceLastLevel = referralsCount - currentLevel.referrals;
    const neededForNextLevel = nextLevel.referrals - currentLevel.referrals;
    return Math.min((referralsSinceLastLevel / neededForNextLevel) * 100, 100);
  };
  
  const monthlyPrice = 9.99;
  const monthlySavings = (monthlyPrice * currentLevel.discount) / 100;

  // --- Обработчики ---
  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(referralLink);
      setCopySuccess(true);
    } catch (err) {
      console.error('Ошибка копирования:', err);
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Stack spacing={4}>
        {/* Заголовок */}
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h4" fontWeight={700}>Реферальная программа</Typography>
          <Typography variant="h6" color="text.secondary" sx={{ fontWeight: 400 }}>
            Приглашайте друзей и получайте скидки на VPN!
          </Typography>
        </Box>

        {/* Карточка статуса */}
        <ReferralStatusCard
          level={currentLevel}
          referralsCount={referralsCount}
          nextLevel={nextLevel}
          progress={getProgressToNextLevel()}
          savings={{ monthly: monthlySavings, yearly: monthlySavings * 12 }}
        />
        
        {/* Карточка с реферальной ссылкой */}
        <ReferralLinkCard referralLink={referralLink} onCopy={handleCopyLink} />
        
        {/* Таблица рефералов */}
        <ReferralsTable referrals={referrals} />

        {/* Уведомление о копировании */}
        <Snackbar
          open={copySuccess}
          autoHideDuration={3000}
          onClose={() => setCopySuccess(false)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert severity="success" sx={{ width: '100%' }}>Ссылка успешно скопирована!</Alert>
        </Snackbar>
        </Stack>
    </Container>
  );
};

export default ReferralsPage;
