import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Box } from '@mui/material';
import Sidebar from './Sidebar';
import TopNavbar from './TopNavbar'; // Импортируем наш новый компонент

const Layout: React.FC = () => {
  const [isSidebarOpen, setSidebarOpen] = useState(false);

  const handleDrawerToggle = () => {
    setSidebarOpen(!isSidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <Sidebar
        // Передаем состояние и функцию для управления мобильным меню
        isOpen={isSidebarOpen}
        onClose={handleDrawerToggle}
      />
      <Box component="main" sx={{ flexGrow: 1, height: '100vh', display: 'flex', flexDirection: 'column' }}>
        <TopNavbar onMenuClick={handleDrawerToggle} />
        <Box sx={{ flexGrow: 1, p: 3, overflow: 'auto' }}>
            <Outlet />
        </Box>
      </Box>
    </Box>
  );
};

export default Layout;