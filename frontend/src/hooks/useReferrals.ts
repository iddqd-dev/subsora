import { useState, useEffect } from 'react';
import apiClient from '../api/axios';
import type { Referral } from '../types/referral'; // Создадим этот тип

export const useReferrals = () => {
  const [referrals, setReferrals] = useState<Referral[]>([]);
  // Сразу считаем количество
  const referralsCount = referrals.length;
  // TODO: В будущем добавить логику подсчета заработка
  const earnings = 0.0; 

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReferrals = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get<Referral[]>('/referrals/my');
      setReferrals(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching referrals:', err);
      setError('Не удалось загрузить данные о рефералах');
      setReferrals([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReferrals();
  }, []);

  return {
    referrals,
    referralsCount,
    earnings,
    loading,
    error,
    refetch: fetchReferrals
  };
};