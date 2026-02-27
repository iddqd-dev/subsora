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
          // Все node_modules в отдельный чанк
          if (id.includes('node_modules')) return 'vendor';

          // Каждая страница из pages/ в отдельный чанк
          if (id.includes('/pages/')) {
            const parts = id.split('/');
            const name = parts[parts.length - 1].replace(/\.[jt]sx?$/, '');
            return `page-${name}`;
          }

          // Каждый компонент из components/ в отдельный чанк
          if (id.includes('/components/')) {
            const parts = id.split('/');
            const name = parts[parts.length - 1].replace(/\.[jt]sx?$/, '');
            return `comp-${name}`;
          }
        }
      }
    },
    chunkSizeWarningLimit: 20, // предупреждение для больших чанков
  }
});