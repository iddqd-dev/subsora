export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_superuser?: boolean;
  subscription_url?: string;
}

// Эта строчка заставит Vite обрабатывать файл как полноценный модуль.
export {};