import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/run_harvester': 'http://localhost:8000',
    },
  },
  build: {
    outDir: 'dist',
  },
});
