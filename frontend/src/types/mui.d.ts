export {};

declare module '@mui/material/Card' {
  // Расширяем интерфейс CardProps
  interface CardOwnProps {
    animation?: 'disabled';
  }
}