import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import ActiveSubscriptionCard from './components/subscriptions/ActiveSubscriptionCard';
import NoSubscriptionCard from './components/subscriptions/NoSubscriptionCard';
import ReferralLinkCard from './components/referrals/ReferralLinkCard';
import { Subscription } from './types/subscription';
import { Plan } from './types/plan';

const App: React.FC = () => {
  // Заглушки данных
  const subscription: Subscription = {
    id: 1,
    plan_id: 1,
    plan: { id: 1, name: 'Basic', price: 10, duration_days: 30, description: 'Basic plan', is_active: true },
    start_date: new Date().toISOString(),
    end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    user: { subscription_url: '', full_name: 'User', email: 'user@example.com' },
  };

  const plans: Plan[] = [
    { id: 1, name: 'Basic', price: 10, duration_days: 30, description: 'Basic plan', is_active: true },
    { id: 2, name: 'Pro', price: 20, duration_days: 30, description: 'Pro plan', is_active: true },
  ];

  const referralLink = 'https://example.com/referral';

  const handleCopyReferral = () => {
    navigator.clipboard.writeText(referralLink);
    alert('Ссылка скопирована!');
  };

  return (
    <Router>
      <Layout>
        <Routes>
          <Route
            path="/subscriptions/active"
            element={<ActiveSubscriptionCard subscription={subscription} plans={plans} />}
          />
          <Route
            path="/subscriptions/none"
            element={<NoSubscriptionCard plans={plans} />}
          />
          <Route
            path="/referral"
            element={<ReferralLinkCard referralLink={referralLink} onCopy={handleCopyReferral} />}
          />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;