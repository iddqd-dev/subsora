import { useState, useEffect } from 'react';
import apiClient from '../api/axios';
import type { Transaction } from '../types/transaction';

export const useTransactions = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/transactions/my');
      setTransactions(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching transactions:', err);
      setError('Не удалось загрузить историю транзакций');
      setTransactions([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  return {
    transactions,
    loading,
    error,
    refetch: fetchTransactions
  };
};