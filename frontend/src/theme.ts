import { createTheme, alpha } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    primary: {
      main: '#5D87FF', // Более насыщенный, но спокойный синий
      light: '#ECF2FF', // Очень светлый фон для акцентов
      dark: '#4570EA',
      contrastText: '#ffffff',
    },
    success: {
      main: '#13DEB9', // Яркий, но приятный мятный
      light: '#E6FFFA',
      dark: '#02b3a9',
      contrastText: '#ffffff',
    },
    warning: {
      main: '#FFAE1F', // Теплый, солнечный оранжевый
      light: '#FEF5E5',
      dark: '#ae8e1a',
      contrastText: '#ffffff',
    },
    error: {
      main: '#FA896B', // Мягкий, но заметный красный (коралл)
      light: '#FDEDE8',
      dark: '#e57c5f',
      contrastText: '#ffffff',
    },
    background: {
      default: '#F8F9FA',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#2A3547', // Более темный основной текст для контраста
      secondary: '#5A6A85',
    }
  },
  typography: {
    fontFamily: 'Inter, sans-serif', // Убедитесь, что используете свой шрифт
    h3: { fontWeight: 700 },
    h4: { fontWeight: 600 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          // Тень стала чуть заметнее и имеет цвет, а не просто черная
          boxShadow: '0 4px 12px rgba(58, 53, 65, 0.08)', 
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            boxShadow: '0 8px 24px rgba(58, 53, 65, 0.12)',
            transform: 'translateY(-4px)',
          }
        }
      },
      variants: [
        {
          props: { animation: 'disabled' },
          style: {
            '&:hover': {
              transform: 'none',
              boxShadow: '0 4px 12px rgba(58, 53, 65, 0.08)',
            }
          }
        }
      ]
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
        // Усилим цвет обводки для outlined кнопок
        outlined: ({ theme, ownerState }) => {
          const color = (ownerState.color && ownerState.color !== 'inherit') ? ownerState.color : 'primary';
          return {
            borderColor: alpha(theme.palette[color].main, 0.7),
            '&:hover': {
              borderColor: theme.palette[color].main,
              backgroundColor: alpha(theme.palette[color].main, 0.08),
            },
          };
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        // Сделаем filled чипы более контрастными
        filled: ({ theme, ownerState }) => {
          const color = (ownerState.color && ownerState.color !== 'default') ? ownerState.color : 'primary';
          return {
            backgroundColor: theme.palette[color].light,
            color: theme.palette[color].dark,
            fontWeight: 600,
          };
        },
      }
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: ({ theme, ownerState }) => {
          const color = (ownerState.color && ownerState.color !== 'inherit') ? ownerState.color : 'primary';
          return {
            height: 6,
            borderRadius: 3,
            backgroundColor: theme.palette[color].light,
          };
        },
        bar: {
          borderRadius: 3,
        }
      }
    }
  },
});

export default theme;
