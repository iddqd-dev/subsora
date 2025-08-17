import { useState, useEffect } from 'react';
import apiClient from '../api/axios';
import { enrichTiers, type DiscountLevel } from '../pages/referrals/tier-mapper';

// Тип данных, который мы ожидаем от API
export interface ReferralTierAPI {
  referrals: number;
  discount: number;
}

export const useReferralTiers = () => {
  const [tiers, setTiers] = useState<DiscountLevel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTiers = async () => {
      try {
        setLoading(true);
        // Предполагаем, что у вас есть такой эндпоинт
        const response = await apiClient.get<ReferralTierAPI[]>('/referrals/tiers');
        
        // Обогащаем данные с бэка презентационными данными
        const enrichedData = enrichTiers(response.data);
        setTiers(enrichedData);
        
      } catch (err) {
        console.error("Ошибка при загрузке уровней реферальной программы:", err);
        setError('Не удалось загрузить условия реферальной программы.');
      } finally {
        setLoading(false);
      }
    };

    fetchTiers();
  }, []);

  return { tiers, loading, error };
};