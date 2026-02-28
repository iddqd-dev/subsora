import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    target: 'esnext',
    cssCodeSplit: true,
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          // React core — ~45kb gzip
          if (id.includes('node_modules/react/') ||
              id.includes('node_modules/react-dom/') ||
              id.includes('node_modules/react-router')) {
            return 'vendor-react';
          }

          // Emotion (нужен MUI) — ~15kb gzip
          if (id.includes('node_modules/@emotion/')) {
            return 'vendor-emotion';
          }

          // MUI иконки — большие, отдельно — ~30kb gzip
          if (id.includes('node_modules/@mui/icons-material/')) {
            const parts = id.split('/');
            // Каждая иконка в своей группе по первой букве
            const iconName = parts[parts.length - 1].replace(/\.[jt]sx?$/, '');
            const group = iconName.charAt(0).toLowerCase();
            return `vendor-icons-${group}`;
          }

          // MUI base/system — ~20kb gzip
          if (id.includes('node_modules/@mui/system') ||
              id.includes('node_modules/@mui/base') ||
              id.includes('node_modules/@mui/utils')) {
            return 'vendor-mui-base';
          }

          // MUI компоненты — ~60kb gzip, режем по группам
          if (id.includes('node_modules/@mui/material/')) {
            const parts = id.split('/');
            const componentName = parts[parts.length - 1].replace(/\.[jt]sx?$/, '');
            const first = componentName.charAt(0).toLowerCase();
            // A-F, G-M, N-Z — три группы
            if (first >= 'a' && first <= 'f') return 'vendor-mui-af';
            if (first >= 'g' && first <= 'm') return 'vendor-mui-gm';
            return 'vendor-mui-nz';
          }

          // Остальные node_modules (axios и т.д.) — ~5kb gzip
          if (id.includes('node_modules/')) {
            return 'vendor-misc';
          }

          // Страницы
          if (id.includes('/pages/')) {
            const parts = id.split('/');
            const name = parts[parts.length - 1].replace(/\.[jt]sx?$/, '');
            return `page-${name}`;
          }

          // Компоненты
          if (id.includes('/components/')) {
            const parts = id.split('/');
            const name = parts[parts.length - 1].replace(/\.[jt]sx?$/, '');
            return `comp-${name}`;
          }
        }
      }
    },
    chunkSizeWarningLimit: 15,
  }
});