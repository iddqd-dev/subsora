import { Card, CardContent, Box, TextField, Button } from '@mui/material';
import { ContentCopy as CopyIcon } from '@mui/icons-material';

interface Props {
  referralLink: string;
  onCopy: () => void;
}

export const ReferralLinkCard = ({ referralLink, onCopy }: Props) => (
  <Card animation="disabled"> {/* Добавляем отключение анимации для этой карточки */}
    <CardContent sx={{ p: { xs: 2, md: 3 } }}>
      <Box
        sx={{
          display: 'flex',
          // На маленьких экранах (xs) - колонка, на больших (sm) - строка
          flexDirection: { xs: 'column', sm: 'row' },
          alignItems: 'center',
          gap: 2, // Отступ между полем и кнопкой
        }}
      >
        {/* Поле с ссылкой */}
        <Box sx={{ flexGrow: 1, width: '100%' }}>
          <TextField
            fullWidth
            label="Ваша реферальная ссылка"
            value={referralLink}
            slotProps={{ htmlInput: { readOnly: true }}}
          />
        </Box>
        
        {/* Кнопка "Копировать" */}
        <Box sx={{ width: { xs: '100%', sm: 'auto' } }}>
          <Button
            fullWidth // Растягиваем на всю ширину родительского Box
            variant="contained"
            size="large"
            startIcon={<CopyIcon />}
            onClick={onCopy}
            sx={{ height: '56px' }} // Высота как у стандартного TextField 'medium' size
          >
            Копировать
          </Button>
        </Box>
      </Box>
    </CardContent>
  </Card>
);