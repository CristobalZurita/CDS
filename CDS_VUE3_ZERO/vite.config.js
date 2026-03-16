import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import cloudinaryTransform from './plugins/cloudinaryTransform.js'

const localSrc = fileURLToPath(new URL('./src', import.meta.url))

export default defineConfig({
  plugins: [
    cloudinaryTransform(),
    vue(),
  ],
  publicDir: 'public',
  resolve: {
    alias: [
      { find: '@', replacement: localSrc },
    ],
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-charts': ['apexcharts', 'vue3-apexcharts'],
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
        },
      },
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
