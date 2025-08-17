import {
    Card, CardContent, Box, Typography, TableContainer, Table, TableHead, TableBody, TableRow, TableCell, Avatar, Chip
  } from '@mui/material';
  import { Security as SecurityIcon, CheckCircle as CheckIcon } from '@mui/icons-material';
  import type { Referral } from '../../types/referral'; // Предполагаем, что у вас есть такой тип
  
  export const ReferralsTable = ({ referrals }: { referrals: Referral[] }) => (
    <Card>
      <CardContent sx={{ p: 0 }}>
        <Box sx={{ p: 3, borderBottom: '1px solid', borderColor: 'divider' }}>
          <Typography variant="h6" fontWeight={600}>
            Приглашённые пользователи ({referrals.length})
          </Typography>
        </Box>
        {referrals.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <SecurityIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">Пока нет рефералов</Typography>
            <Typography variant="body2" color="text.secondary">Поделитесь ссылкой, чтобы начать получать скидки!</Typography>
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Пользователь</TableCell>
                  <TableCell>Дата подключения</TableCell>
                  <TableCell align="right">Статус</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {referrals.map((referral) => (
                  <TableRow key={referral.id} sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: 'primary.light', color: 'primary.dark' }}>
                          {referral.referred.full_name?.charAt(0) || 'U'}
                        </Avatar>
                        <Typography variant="body2" fontWeight={500}>
                          {referral.referred.full_name || 'VPN Пользователь'}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      {new Date(referral.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell align="right">
                      <Chip icon={<CheckIcon />} label="Активен" color="success" size="small" variant="outlined" />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
    </Card>
  );