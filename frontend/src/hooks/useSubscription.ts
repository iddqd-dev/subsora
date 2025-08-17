import { useState, useEffect } from 'react';
import { AxiosError } from 'axios';
import apiClient from '../api/axios';
import type { Subscription } from '../types/subscription';

// Кастомный хук для работы с подпиской
export const useSubscription = () => {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSubscription = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/subscriptions/my/active');
      setSubscription(response.data);
      setError(null);
    } catch (err) {
      if (err instanceof AxiosError && err.response?.status === 404) {
        setSubscription(null); // Нет активной подписки - это нормально
        setError(null);
      } else {
        setError('Не удалось загрузить данные о подписке');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubscription();
  }, []);

  return {
    subscription,
    loading,
    error,
    refetch: fetchSubscription
  };
};