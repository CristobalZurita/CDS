import { defineConfig, devices } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

/**
 * Configuración de Playwright para CDS ZERO
 * 
 * Estructura de tests:
 * - tests/e2e/*.spec.js - Tests E2E
 * - tests/e2e/helpers/*.js - Helpers reutilizables
 * 
 * Para correr:
 * - npm run test:e2e        (todos los tests)
 * - npm run test:e2e:ui     (modo UI)
 * - npx playwright test auth.spec.js  (solo auth)
 */

export default defineConfig({
  testDir: './tests/e2e',
  
  // Tiempo de espera por test
  timeout: 30 * 1000,
  
  // Workers: 1 para evitar conflictos de autenticación
  workers: 1,
  
  // Paralelismo: false para tests E2E con estado compartido
  fullyParallel: false,
  
  // Reintentos en CI
  retries: process.env.CI ? 2 : 0,
  
  // Reporter
  reporter: [
    ['list'],
    ['html', { open: 'never' }],
  ],
  
  use: {
    // URL base
    baseURL: 'http://localhost:5174',
    
    // Navegador
    ...devices['Desktop Chrome'],
    
    // Configuración de viewport
    viewport: { width: 1280, height: 720 },
    
    // Trace y screenshots
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    
    // Acción por defecto
    actionTimeout: 5000,
    navigationTimeout: 10000,
  },

  projects: [
    {
      name: 'setup',
      testMatch: /.*\.setup\.js/,
    },
    {
      name: 'e2e',
      dependencies: ['setup'],
      testMatch: /.*\.spec\.js/,
      testIgnore: /.*\.setup\.js/,
    },
  ],

  // Web server: levantar el frontend
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5174',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
    env: {
      VITE_API_URL: process.env.VITE_API_URL || 'http://localhost:8000/api/v1',
      VITE_TURNSTILE_DISABLE: 'true',
    },
  },
})
