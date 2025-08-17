import React from 'react';
import { NavLink } from 'react-router-dom';
import { Box, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Typography } from '@mui/material';
import { useAuth } from '../hooks/useAuth';

// Импортируем иконки
import HomeIcon from '@mui/icons-material/Home';
import CreditCardIcon from '@mui/icons-material/CreditCard';
import ViewModuleIcon from '@mui/icons-material/ViewModule';
import LocalOfferIcon from '@mui/icons-material/LocalOffer';
import PeopleIcon from '@mui/icons-material/People';
import ReceiptIcon from '@mui/icons-material/Receipt';
import ShareIcon from '@mui/icons-material/Share';
import { Logo } from './Logo';


interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const menuItems = [
  { text: 'Dashboard', path: '/dashboard', icon: <HomeIcon />, adminOnly: false },
  { text: 'Subscriptions', path: '/subscriptions', icon: <CreditCardIcon />, adminOnly: false },
  { text: 'Referrals', path: '/referrals', icon: <ShareIcon />, adminOnly: false }, // Добавили рефералы
  { text: 'Plans', path: '/plans', icon: <ViewModuleIcon />, adminOnly: true },
  { text: 'Coupons', path: '/coupons', icon: <LocalOfferIcon />, adminOnly: true },
  { text: 'Users', path: '/users', icon: <PeopleIcon />, adminOnly: true },
  { text: 'Payments', path: '/payments', icon: <ReceiptIcon />, adminOnly: false },
];

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
    const { user } = useAuth();
    const drawerWidth = 250;

    // --- Вот этот блок ---
    // Это не компонент, а просто JSX-фрагмент, который мы используем дважды ниже
    const drawerContent = (
      <div>
      
        <Box sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
        <Logo />
        </Box>
        <List>
          {menuItems.map((item) => {
            // Условный рендеринг для админских пунктов
            if (item.adminOnly && !user?.is_superuser) {
              return null;
            }
            return (
              <ListItem key={item.text} disablePadding>
                <ListItemButton
                  component={NavLink}
                  to={item.path}
                  onClick={onClose} // Закрываем мобильное меню по клику на ссылку
                  sx={{
                    margin: '4px 8px',
                    borderRadius: '8px',
                    '&.active': {
                      backgroundColor: 'primary.main',
                      color: 'white',
                      '& .MuiListItemIcon-root': { color: 'white' },
                      '&:hover': { backgroundColor: 'primary.dark' },
                    },
                    '&:not(.active):hover': {
                      backgroundColor: 'action.hover',
                    },
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 40, color: 'inherit' }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
        <Box sx={{ position: 'absolute', bottom: 0, width: '100%', p: 2, borderTop: '1px solid #E0E0E0' }}>
            {user ? (
                <>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                        {user.full_name || 'Пользователь'}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        {user.email}
                    </Typography>
                </>
            ) : (
                <Typography variant="body2">Загрузка...</Typography>
            )}
        </Box>
      </div>
    );
    // --- Конец блока drawerContent ---

    return (
        <Box component="nav" sx={{ width: { lg: drawerWidth }, flexShrink: { lg: 0 } }}>
            {/* Мобильная версия - временный Drawer, "выезжает" */}
            <Drawer
                variant="temporary"
                open={isOpen}
                onClose={onClose}
                ModalProps={{ keepMounted: true }} // Для лучшей производительности на мобильных
                sx={{
                    display: { xs: 'block', lg: 'none' }, // Показываем только на маленьких экранах
                    '& .MuiDrawer-paper': {
                      boxSizing: 'border-box',
                      width: drawerWidth,
                      borderRight: 'none', // Убираем границу, т.к. он поверх контента
                    },
                }}
            >
                {drawerContent}
            </Drawer>

            {/* Десктопная версия - постоянный Drawer, "стоит на месте" */}
            <Drawer
                variant="permanent"
                sx={{
                    display: { xs: 'none', lg: 'block' }, // Показываем только на больших экранах
                    '& .MuiDrawer-paper': {
                      boxSizing: 'border-box',
                      width: drawerWidth,
                      borderRight: '1px solid #E0E0E0'
                    },
                }}
                open // Постоянный Drawer всегда открыт
            >
                {drawerContent}
            </Drawer>
        </Box>
    );
};

export default Sidebar;