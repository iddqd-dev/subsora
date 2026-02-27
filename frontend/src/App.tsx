import React, { Suspense } from 'react';

// Ленивый импорт страниц
const DashboardPage = React.lazy(() => import('./pages/DashboardPage'));
const LoginPage = React.lazy(() => import('./pages/LoginPage'));
const Referralspage = React.lazy(() => import('./pages/Referralspage'));
const SubscriptionPage = React.lazy(() => import('./pages/SubscriptionPage'));

// Ленивый импорт крупных компонентов (опционально, если надо дробить ещё)
const ActiveSubscriptionCard = React.lazy(
  () => import('./components/subscriptions/ActiveSubscriptionCard')
);
const NoSubscriptionCard = React.lazy(
  () => import('./components/subscriptions/NoSubscriptionCard')
);
const ReferralLinkCard = React.lazy(
  () => import('./components/referrals/ReferralLinkCard')
);

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      {/* Основные страницы */}
      <DashboardPage />
      <LoginPage />
      <Referralspage />
      <SubscriptionPage />

      {/* Примеры ленивого компонента */}
      <ActiveSubscriptionCard />
      <NoSubscriptionCard />
      <ReferralLinkCard />
    </Suspense>
  );
}

export default App;