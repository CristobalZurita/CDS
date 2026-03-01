import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig, devices } from '@playwright/test'

const currentDir = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = currentDir
const frontendPort = process.env.PLAYWRIGHT_FRONTEND_PORT || '5174'
const apiPort = process.env.PLAYWRIGHT_API_PORT || '8001'
const baseURL = process.env.PLAYWRIGHT_BASE_URL || `http://127.0.0.1:${frontendPort}`
const apiBaseURL = process.env.PLAYWRIGHT_API_URL || `http://127.0.0.1:${apiPort}/api/v1`
const webServerEnv = { ...process.env }

delete webServerEnv.NO_COLOR
delete webServerEnv.FORCE_COLOR

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 60_000,
  fullyParallel: false,
  workers: 1,
  expect: {
    timeout: 10_000,
  },
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: 'list',
  use: {
    baseURL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'setup',
      testMatch: /auth\.setup\.ts/,
      use: {
        ...devices['Desktop Chrome'],
      },
    },
    {
      name: 'chromium',
      dependencies: ['setup'],
      testIgnore: /auth\.setup\.ts/,
      use: {
        ...devices['Desktop Chrome'],
      },
    },
  ],
  webServer: [
    {
      command: `${path.join(repoRoot, 'backend', '.venv', 'bin', 'python')} ${path.join(repoRoot, 'scripts', 'e2e', 'start_backend.py')}`,
      url: `http://127.0.0.1:${apiPort}/health`,
      cwd: repoRoot,
      reuseExistingServer: false,
      timeout: 120_000,
      env: {
        ...webServerEnv,
        PLAYWRIGHT_API_PORT: apiPort,
        PLAYWRIGHT_FRONTEND_PORT: frontendPort,
      },
    },
    {
      command: `env -u NO_COLOR -u FORCE_COLOR npm run dev -- --host 127.0.0.1 --port ${frontendPort} --strictPort`,
      url: baseURL,
      cwd: repoRoot,
      reuseExistingServer: false,
      timeout: 120_000,
      env: {
        ...webServerEnv,
        VITE_API_URL: apiBaseURL,
        VITE_TURNSTILE_DISABLE: 'true',
        PLAYWRIGHT_BASE_URL: baseURL,
        PLAYWRIGHT_API_URL: apiBaseURL,
      },
    },
  ],
})
