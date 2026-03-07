import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    target: 'esnext',
    cssCodeSplit: true,
    // Даем Vite/Rollup самому решать, как разбивать vendor‑чанки.
    // Ручное разбиение вызывало раннюю инициализацию кода Emotion
    // и ошибку "Cannot access 'j' before initialization" в vendor-emotion-*.js.
    chunkSizeWarningLimit: 15,
  }
});