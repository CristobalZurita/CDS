import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { expect, type Page } from '@playwright/test'

const _currentDir = path.dirname(fileURLToPath(import.meta.url))
const authDir = process.env.PLAYWRIGHT_AUTH_DIR || path.resolve('/tmp', 'cds_playwright_auth')

export function resolveAuthState(profile: 'admin' | 'client') {
  return path.resolve(authDir, `${profile}.json`)
}

export async function loginFromUi(page: Page, email: string, password: string) {
  await expect(page.getByTestId('turnstile-bypass')).toBeVisible()
  await page.getByTestId('login-email').fill(email)
  await page.getByTestId('login-password').fill(password)
  await page.getByTestId('login-submit').click()
}
