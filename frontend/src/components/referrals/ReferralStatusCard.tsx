import {
    Card, CardContent, Box, Avatar, Typography, LinearProgress, Divider
  } from '@mui/material';
  import type { DiscountLevel } from '../../pages/referrals/tier-mapper';
  
  interface Props {
    level: DiscountLevel;
    referralsCount: number;
    nextLevel: DiscountLevel | null;
    progress: number;
    savings: {
      monthly: number;
      yearly: number;
    };
  }
  
  export const ReferralStatusCard = ({ level, referralsCount, nextLevel, progress, savings }: Props) => (
    <Card animation="disabled">
      <CardContent sx={{ p: { xs: 2, md: 3 } }}>
        {/* --- Верхний блок: Скидка и Аватар --- */}
        <Box 
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            mb: 3 // Добавим отступ до блока с экономией
          }}
        >
          <Avatar sx={{ bgcolor: `${level.color}.light`, color: `${level.color}.main`, width: 64, height: 64 }}>
            <level.Icon sx={{ fontSize: 32 }} />
          </Avatar>
          <Box>
            <Typography variant="overline" sx={{ color: `${level.color}.main`, fontWeight: 600, lineHeight: 1.2 }}>
              {level.title}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, flexWrap: 'wrap' }}>
              <Typography variant="h4" component="span" fontWeight={700}>
                {level.discount}%
              </Typography>
              <Typography variant="h5" component="span" fontWeight={500} color="text.primary">
                Скидка
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              {referralsCount} приглашенных
            </Typography>
          </Box>
        </Box>
  

        
        {/* Вставляем разделитель для визуальной иерархии */}
        {nextLevel && <Divider sx={{ my: 3 }} />}
  
        {/* --- Нижний блок с прогресс-баром --- */}
        {nextLevel && (
          <Box>
            <Box sx={{ 
              display: 'flex',
              // 👇 Вот магия для мобильной верстки!
              flexDirection: { xs: 'column', sm: 'row' }, // На маленьких экранах - колонка, на больших - строка
              justifyContent: 'space-between', 
              alignItems: { xs: 'flex-start', sm: 'center' }, // Выравнивание для разных режимов
              mb: 1 
            }}>
              <Typography variant="body2" color="text.secondary">
                До уровня "{nextLevel.title}" ({nextLevel.discount}% скидка)
              </Typography>
              <Typography variant="body2" fontWeight={600} color="text.primary" sx={{ mt: { xs: 0.5, sm: 0 } }}>
                {nextLevel.referrals - referralsCount} осталось
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={progress} 
              color={level.color === 'grey' ? 'primary' : level.color} 
            />
          </Box>
        )}
      </CardContent>
    </Card>
  );