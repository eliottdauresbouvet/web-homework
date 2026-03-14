import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'https://pixels-war.fly.dev',
        changeOrigin: true,
        secure: true,
      }
    }
  }
})