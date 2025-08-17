import React from 'react';
import {
    Table, TableBody, TableCell, TableContainer,
    TableHead, TableRow, Chip, Typography, Box, Card, CardContent
} from '@mui/material';
import ReceiptIcon from '@mui/icons-material/Receipt';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import PendingIcon from '@mui/icons-material/Pending';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import type { Transaction } from '../../types/transaction';

interface Props {
  transactions: Transaction[];
}

// Функция для определения цвета Chip в зависимости от статуса
const getStatusChipColor = (status: string): 'success' | 'warning' | 'error' | 'default' => {
    switch (status.toLowerCase()) {
        case 'completed':
            return 'success';
        case 'pending':
            return 'warning';
        case 'failed':
            return 'error';
        default:
            return 'default';
    }
};

const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
        case 'completed':
            return <CheckCircleOutlineIcon sx={{ fontSize: 16 }} />;
        case 'pending':
            return <PendingIcon sx={{ fontSize: 16 }} />;
        case 'failed':
            return <ErrorOutlineIcon sx={{ fontSize: 16 }} />;
        default:
            return <ReceiptIcon sx={{ fontSize: 16 }} />;
    }
};

const PaymentsHistoryTable: React.FC<Props> = ({ transactions }) => {
    if (transactions.length === 0) {
        return (
            <Card sx={{ 
                boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
                borderRadius: 2
            }}>
                <CardContent sx={{ p: { xs: 3, md: 4 }, textAlign: 'center' }}>
                    <Box sx={{ 
                        p: { xs: 1.5, md: 2 }, 
                        borderRadius: 2, 
                        bgcolor: 'grey.50', 
                        display: 'inline-flex',
                        mb: 2
                    }}>
                        <ReceiptIcon sx={{ fontSize: { xs: 24, md: 32 }, color: 'text.secondary' }} />
                    </Box>
                    <Typography variant="h6" color="text.secondary" sx={{ 
                        mb: 1,
                        fontSize: { xs: '1.125rem', md: '1.25rem' }
                    }}>
                        История платежей пуста
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Здесь будут отображаться все ваши транзакции
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card sx={{ 
            boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
            borderRadius: 2,
            overflow: 'hidden'
        }}>
            <TableContainer>
                <Table sx={{ 
                    width: '100%',
                    '& .MuiTableCell-root': {
                        px: { xs: 0.5, md: 2 },
                        py: { xs: 1, md: 2 },
                        fontSize: { xs: '0.75rem', md: '1rem' }
                    }
                }} aria-label="payments history table">
                    <TableHead sx={{ 
                        backgroundColor: 'grey.50',
                        '& .MuiTableCell-head': {
                            fontWeight: 600,
                            color: 'text.primary',
                            borderBottom: '2px solid',
                            borderColor: 'divider',
                            fontSize: { xs: '0.75rem', md: '1rem' }
                        }
                    }}>
                        <TableRow>
                            <TableCell sx={{ width: { xs: '25%', md: 'auto' } }}>Дата</TableCell>
                            <TableCell sx={{ width: { xs: '35%', md: 'auto' } }}>Описание</TableCell>
                            <TableCell align="right" sx={{ width: { xs: '25%', md: 'auto' } }}>Сумма</TableCell>
                            <TableCell align="center" sx={{ width: { xs: '15%', md: 'auto' } }}>Статус</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {transactions.map((transaction) => (
                            <TableRow 
                                key={transaction.id}
                                sx={{ 
                                    '&:hover': { 
                                        backgroundColor: 'action.hover' 
                                    },
                                    '&:last-child td': { 
                                        border: 0 
                                    }
                                }}
                            >
                                <TableCell component="th" scope="row">
                                    <Typography variant="body2" fontWeight={500} sx={{ fontSize: { xs: '0.75rem', md: '1rem' } }}>
                                        {new Date(transaction.created_at).toLocaleDateString()}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary" sx={{ fontSize: { xs: '0.625rem', md: '0.875rem' } }}>
                                        {new Date(transaction.created_at).toLocaleTimeString()}
                                    </Typography>
                                </TableCell>
                                <TableCell>
                                    <Typography variant="body2" fontWeight={500} sx={{ fontSize: { xs: '0.75rem', md: '1rem' } }}>
                                        Оплата
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary" sx={{ fontSize: { xs: '0.625rem', md: '0.875rem' } }}>
                                        {transaction.subscription?.plan?.name || `ID: ${transaction.plan_id}`}
                                    </Typography>
                                </TableCell>
                                <TableCell align="right">
                                    <Typography variant="body2" fontWeight={600} color="text.primary" sx={{ fontSize: { xs: '0.75rem', md: '1rem' } }}>
                                        ${transaction.amount.toFixed(2)}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary" sx={{ fontSize: { xs: '0.625rem', md: '0.875rem' } }}>
                                        {transaction.currency}
                                    </Typography>
                                </TableCell>
                                <TableCell align="center">
                                    <Chip
                                        icon={getStatusIcon(transaction.status)}
                                        label={transaction.status}
                                        color={getStatusChipColor(transaction.status)}
                                        size="small"
                                        sx={{ 
                                            fontWeight: 500,
                                            textTransform: 'capitalize',
                                            fontSize: { xs: '0.625rem', md: '0.875rem' },
                                            height: { xs: 20, md: 24 },
                                            '& .MuiChip-icon': {
                                                fontSize: { xs: 12, md: 16 }
                                            }
                                        }}
                                    />
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Card>
    );
};

export default PaymentsHistoryTable;