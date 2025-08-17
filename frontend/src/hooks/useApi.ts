import { useState, useCallback } from 'react';
import { AxiosError } from 'axios';
import apiClient from '../api/axios';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export const useApi = <T = unknown>() => {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null
  });

  const execute = useCallback(async (
    method: 'get' | 'post' | 'put' | 'delete',
    url: string,
    data?: Record<string, unknown>
  ) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await apiClient[method](url, data);
      setState({
        data: response.data,
        loading: false,
        error: null
      });
      return response.data;
    } catch (err: unknown) {
      const axiosError = err as AxiosError;
      const errorMessage = (axiosError.response?.data as { detail?: string })?.detail || 'Произошла ошибка';
      setState({
        data: null,
        loading: false,
        error: errorMessage
      });
      throw err;
    }
  }, []);

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null
    });
  }, []);

  return {
    ...state,
    execute,
    reset
  };
};