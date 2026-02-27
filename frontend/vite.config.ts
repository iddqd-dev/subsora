import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173
  },
  build: {
      target: 'esnext',
      cssCodeSplit: true,
      rollupOptions: {
        output: {
          manualChunks(id: string) {
            if (id.includes('node_modules')) return 'vendor';
            if (id.includes('/pages/')) {
              const parts = id.split('/');
              const name = parts[parts.length - 1].replace(/\.[jt]sx?$/, '');
              return `page-${name}`;
            }
          }
        }
      }
    }
});