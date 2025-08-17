import { useState, useEffect } from 'react';
import apiClient from '../api/axios';
import type { Plan } from '../types/plan';

export const usePlans = () => {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPlans = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/plans');
      setPlans(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching plans:', err);
      setError('Не удалось загрузить список планов');
      setPlans([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlans();
  }, []);

  return {
    plans,
    loading,
    error,
    refetch: fetchPlans
  };
};
