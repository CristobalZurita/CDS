import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

const legacySrc = '/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: [
      { find: '@new', replacement: fileURLToPath(new URL('./src', import.meta.url)) },
      { find: '@legacy', replacement: legacySrc },
      { find: '@', replacement: legacySrc },
      { find: /^\/src\//, replacement: legacySrc + '/' },
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
