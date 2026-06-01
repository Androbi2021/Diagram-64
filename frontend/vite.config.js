import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Backend port can be overridden via the BACKEND_PORT env var (defaults to 8000).
// Keep this in sync with the port passed to `manage.py runserver`.
const backendPort = process.env.BACKEND_PORT || '8000';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: `http://localhost:${backendPort}`,
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
