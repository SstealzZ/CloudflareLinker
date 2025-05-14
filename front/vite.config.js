import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * Vite configuration
 *
 * @returns {import('vite').UserConfig} Vite configuration object
 */
export default defineConfig({
  plugins: [react()],
  server: {
    port: parseInt(process.env.FRONTEND_PORT || '3000'),
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: process.env.API_HOST || `http://localhost:${process.env.BACKEND_PORT || '8000'}`,
        changeOrigin: true,
        secure: false,
      }
    }
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  define: {
    'process.env.REACT_APP_API_URL': JSON.stringify('/api/v1')
  }
}) 