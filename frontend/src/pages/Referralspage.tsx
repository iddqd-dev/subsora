import React from 'react';
import ReferralStatusCard from '../components/referrals/ReferralStatusCard';
import ReferralLinkCard from '../components/referrals/ReferralLinkCard';
import ReferralsTable from '../components/referrals/ReferralsTable';
import { DiscountLevel } from './referrals/tier-mapper';
import type { Referral } from '../types/referral';

// Заглушки
const referralLink = 'https://example.com/referral';
const handleCopyReferral = () => navigator.clipboard.writeText(referralLink);

const dummyReferrals: Referral[] = []; // Пустой массив для примера

const dummyLevel: DiscountLevel = {
  title: 'Bronze',
  discount: 5,
  color: 'primary',
  Icon: () => <span>B</span>,
  referrals: 5,
};

const Referralspage: React.FC = () => {
  return (
    <div style={{ display: 'grid', gap: '16px' }}>
      <ReferralStatusCard
        level={dummyLevel}
        referralsCount={2}
        nextLevel={{ ...dummyLevel, title: 'Silver', discount: 10, referrals: 10 }}
        progress={20}
        savings={{ monthly: 5, yearly: 60 }}
      />
      <ReferralLinkCard referralLink={referralLink} onCopy={handleCopyReferral} />
      <ReferralsTable referrals={dummyReferrals} />
    </div>
  );
};

export default Referralspage;