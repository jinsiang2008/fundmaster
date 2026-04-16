import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        /** 与前端 axios 长请求一致，避免开发时代理提前断开 */
        timeout: 120_000,
        proxyTimeout: 120_000,
      },
    },
  },
})
