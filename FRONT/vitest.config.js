import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    include: ['tests/unit/**/*.spec.{js,ts}'],
    exclude: ['MODELOS/**', 'node_modules/**']
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  }
})
