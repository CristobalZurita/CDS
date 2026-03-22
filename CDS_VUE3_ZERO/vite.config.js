import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import cloudinaryTransform from './plugins/cloudinaryTransform.js'

const localSrc = fileURLToPath(new URL('./src', import.meta.url))

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const cloudName = String(env.VITE_CLOUDINARY_CLOUD_NAME || '').trim()

  return {
    plugins: [
      cloudinaryTransform({ cloudName }),
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
            'vendor-vue': ['vue', 'vue-router', 'pinia'],
          },
        },
      },
    },
    server: {
      host: '0.0.0.0',
      port: 5174,
      cors: {
        origin: true,
        credentials: true,
        allowedHeaders: ['Content-Type', 'Authorization', 'X-CSRF-Token'],
        methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
      },
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
  }
})
