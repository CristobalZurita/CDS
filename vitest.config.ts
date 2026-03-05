import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler',
        silenceDeprecations: ['legacy-js-api', 'color-functions', 'global-builtin', 'import'],
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      all: true,
      provider: 'v8',
      reportsDirectory: './coverage',
      reporter: ['text', 'json', 'json-summary', 'html', 'lcov', 'text-summary'],
      include: ['src/**/*.{js,ts,vue}'],
      exclude: [
        'src/**/*.d.ts',
        'src/**/mockData.ts',
        'src/**/fixtures/**',
        'src/**/__mocks__/**',
        'src/**/tests/**',
        '**/*.d.ts',
        '**/mockData.ts',
        '**/fixtures/**'
      ],
      thresholds: {
        lines: 90,
        functions: 90,
        branches: 85,
        statements: 90,
      },
    },
    include: ['tests/**/*.test.ts', 'tests/**/*.spec.ts'],
    exclude: ['node_modules', 'dist', 'tests/e2e/**'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@stores': path.resolve(__dirname, './src/stores'),
      '@composables': path.resolve(__dirname, './src/composables'),
      '@services': path.resolve(__dirname, './src/services'),
      '@types': path.resolve(__dirname, './src/types'),
      '@utils': path.resolve(__dirname, './src/utils'),
    }
  }
})
