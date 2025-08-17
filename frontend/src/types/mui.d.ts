export {};

declare module '@mui/material/Card' {
  // Расширяем интерфейс CardProps
  interface CardProps {
    animation?: 'disabled';
  }
}