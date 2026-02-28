import fs from 'node:fs'
import path from 'node:path'
import { test, expect } from '@playwright/test'
import { loginFromUi, resolveAuthState } from './helpers/auth'

const authDir = path.dirname(resolveAuthState('admin'))

test.beforeAll(() => {
  fs.mkdirSync(authDir, { recursive: true })
})

test('save client auth state', async ({ page }) => {
  await page.goto('/login')
  await loginFromUi(page, 'e2e.client@example.com', 'client12')
  await expect(page).toHaveURL(/\/dashboard$/)
  await page.context().storageState({ path: resolveAuthState('client') })
})

test('save admin auth state', async ({ page }) => {
  await page.goto('/admin')
  await expect(page).toHaveURL(/\/login\?redirect=(%2F|\/)admin$/)
  await loginFromUi(page, 'e2e.admin@example.com', 'admin12')
  await expect(page).toHaveURL(/\/admin$/)
  await page.context().storageState({ path: resolveAuthState('admin') })
})
