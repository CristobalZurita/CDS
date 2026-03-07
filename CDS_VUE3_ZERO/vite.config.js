import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

const localSrc = fileURLToPath(new URL('./src', import.meta.url))
const legacySrc = fileURLToPath(new URL('../src', import.meta.url))

export default defineConfig({
  plugins: [vue()],
  publicDir: '../public',
  resolve: {
    alias: [
      { find: '@new', replacement: localSrc },
      { find: '@', replacement: legacySrc },
      { find: '@legacy', replacement: legacySrc },
      { find: /^\/src\//, replacement: `${legacySrc}/` },
    ],
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
