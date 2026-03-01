import { Buffer } from 'node:buffer'
import { test, expect } from '@playwright/test'
import { loginFromUi, resolveAuthState } from './helpers/auth'
import { waitForAppToSettle } from './helpers/page'

const invalidTokenImage = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn2jVQAAAAASUVORK5CYII=',
  'base64'
)

test('invalid credentials show a visible login error', async ({ page }) => {
  await page.goto('/login')
  await waitForAppToSettle(page)

  await loginFromUi(page, 'e2e.client@example.com', 'wrongpass')

  await expect(page.getByTestId('login-error')).toContainText('Email o contraseña incorrectos')
})

test('unknown routes redirect back to home', async ({ page }) => {
  await page.goto('/ruta-que-no-existe')
  await waitForAppToSettle(page)

  await expect.poll(async () => page.evaluate(() => window.location.pathname)).toBe('/')
})

test('invalid photo upload tokens surface a user-facing error', async ({ page }) => {
  await page.goto('/photo-upload/token-invalido')
  await waitForAppToSettle(page)

  await page.getByTestId('photo-upload-file').setInputFiles({
    name: 'invalid-token.png',
    mimeType: 'image/png',
    buffer: invalidTokenImage,
  })
  await page.getByTestId('photo-upload-caption').fill('Foto de prueba con token inválido')
  await page.getByTestId('photo-upload-submit').click()

  await expect(page.getByTestId('photo-upload-status')).toContainText('No se pudo enviar la foto.')
})

test.describe('authenticated client guards', () => {
  test.use({ storageState: resolveAuthState('client') })

  test('client users are redirected away from admin routes', async ({ page }) => {
    await page.goto('/admin')
    await waitForAppToSettle(page)

    await expect.poll(async () => page.evaluate(() => window.location.pathname)).toBe('/')
  })

  test('client users are redirected away from guest-only login route', async ({ page }) => {
    await page.goto('/login')
    await waitForAppToSettle(page)

    await expect.poll(async () => page.evaluate(() => window.location.pathname)).toBe('/dashboard')
  })
})
