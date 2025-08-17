export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_superuser?: boolean;
}

// Эта строчка заставит Vite обрабатывать файл как полноценный модуль.
export {};