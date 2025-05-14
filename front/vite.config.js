import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

/**
 * Vite configuration
 *
 * @returns {import('vite').UserConfig} Vite configuration object
 */
export default defineConfig({
  plugins: [
    react({
      jsxRuntime: 'automatic',
      include: '**/*.{jsx,js}',
    })
  ],
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
    },
    extensions: ['.mjs', '.js', '.jsx', '.ts', '.tsx', '.json']
  },
  define: {
    'process.env.REACT_APP_API_URL': JSON.stringify('/api/v1')
  },
  esbuild: {
    loader: 'jsx',
    include: /src\/.*\.jsx?$/,
    exclude: [],
    jsx: 'automatic'
  },
  optimizeDeps: {
    esbuildOptions: {
      loader: {
        '.js': 'jsx',
      },
    },
  }
}) 