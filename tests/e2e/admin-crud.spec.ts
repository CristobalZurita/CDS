import { test, expect } from '@playwright/test'
import { resolveAuthState } from './helpers/auth'
import { expectNoBrowserErrors, trackBrowserErrors, waitForAppToSettle } from './helpers/page'

test.describe('admin CRUD flows', () => {
  test.use({ storageState: resolveAuthState('admin') })

  test('users CRUD works from admin UI', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const slug = Date.now().toString(36)
    const createdEmail = `user.${slug}@example.com`
    const updatedEmail = `user.${slug}.updated@example.com`
    const createdName = `Usuario E2E ${slug}`
    const updatedName = `Usuario E2E ${slug} Editado`

    page.on('dialog', (dialog) => dialog.accept())

    await page.goto('/admin')
    await waitForAppToSettle(page)

    await page.getByTestId('users-new').click()
    await page.getByTestId('user-email').fill(createdEmail)
    await page.getByTestId('user-full-name').fill(createdName)
    await page.getByTestId('user-username').fill(`user_${slug}`)
    await page.getByTestId('user-role').selectOption('technician')
    await page.getByTestId('user-password').fill('secret123456')
    await page.getByTestId('user-save').click()

    const createdRow = page.getByTestId('user-row').filter({ hasText: createdEmail })
    await expect(createdRow).toBeVisible()
    await expect(createdRow).toContainText('technician')

    await createdRow.getByTestId('user-edit').click()
    await page.getByTestId('user-email').fill(updatedEmail)
    await page.getByTestId('user-full-name').fill(updatedName)
    await page.getByTestId('user-role').selectOption('admin')
    await page.getByTestId('user-save').click()

    const updatedRow = page.getByTestId('user-row').filter({ hasText: updatedEmail })
    await expect(updatedRow).toBeVisible()
    await expect(updatedRow).toContainText(updatedName)
    await expect(updatedRow).toContainText('admin')

    await updatedRow.getByTestId('user-delete').click()
    await expect(page.getByTestId('user-row').filter({ hasText: updatedEmail })).toHaveCount(0)
    await expectNoBrowserErrors(tracker)
  })

  test('categories CRUD works from admin UI', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const slug = Date.now().toString(36)
    const createdName = `Categoria E2E ${slug}`
    const updatedName = `Categoria E2E ${slug} Editada`

    page.on('dialog', (dialog) => dialog.accept())

    await page.goto('/admin/categories')
    await waitForAppToSettle(page)

    await page.getByTestId('categories-new').click()
    await page.getByTestId('category-name').fill(createdName)
    await page.getByTestId('category-description').fill('Creada por Playwright')
    await page.getByTestId('category-save').click()

    const createdRow = page.getByTestId('category-row').filter({ hasText: createdName })
    await expect(createdRow).toBeVisible()

    await createdRow.getByTestId('category-edit').click()
    await page.getByTestId('category-name').fill(updatedName)
    await page.getByTestId('category-description').fill('Actualizada por Playwright')
    await page.getByTestId('category-save').click()

    const updatedRow = page.getByTestId('category-row').filter({ hasText: updatedName })
    await expect(updatedRow).toBeVisible()
    await expect(updatedRow).toContainText('Actualizada por Playwright')

    await updatedRow.getByTestId('category-delete').click()
    await expect(page.getByTestId('category-row').filter({ hasText: updatedName })).toHaveCount(0)
    await expectNoBrowserErrors(tracker)
  })

  test('inventory CRUD works from admin UI', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const slug = Date.now().toString(36)
    const createdName = `Item E2E ${slug}`
    const updatedName = `Item E2E ${slug} Editado`
    const createdSku = `E2E-${slug}-A`
    const updatedSku = `E2E-${slug}-B`

    page.on('dialog', (dialog) => dialog.accept())

    await page.goto('/admin/inventory')
    await waitForAppToSettle(page)

    await page.getByTestId('inventory-view-manage').click()
    await page.getByTestId('inventory-new').click()

    await page.getByTestId('inventory-name').fill(createdName)
    await page.getByTestId('inventory-sku').fill(createdSku)
    await page.getByTestId('inventory-stock').fill('7')
    await page.getByTestId('inventory-price').fill('9900')
    await page.getByTestId('inventory-category').selectOption({ index: 1 })
    await page.getByTestId('inventory-save').click()

    const createdRow = page.getByTestId('inventory-row').filter({ hasText: createdName })
    await expect(createdRow).toBeVisible()

    await createdRow.getByTestId('inventory-edit').click()
    await expect(page.getByTestId('inventory-form-title')).toContainText('Editar item')
    await page.getByTestId('inventory-name').fill(updatedName)
    await page.getByTestId('inventory-sku').fill(updatedSku)
    await page.getByTestId('inventory-stock').fill('11')
    await page.getByTestId('inventory-price').fill('12900')
    await page.getByTestId('inventory-save').click()

    const updatedRow = page.getByTestId('inventory-row').filter({ hasText: updatedName })
    await expect(updatedRow).toBeVisible()

    await updatedRow.getByTestId('inventory-delete').click()
    await expect(page.getByTestId('inventory-row').filter({ hasText: updatedName })).toHaveCount(0)
    await expectNoBrowserErrors(tracker)
  })

  test('repairs CRUD works from admin UI', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const slug = Date.now().toString(36)
    const modelName = `Sintetizador E2E ${slug}`

    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)

    await page.getByTestId('repairs-new').click()
    const clientValue = await page
      .getByTestId('repair-client')
      .locator('option')
      .filter({ hasText: 'E2E Client' })
      .first()
      .getAttribute('value')

    if (!clientValue) {
      throw new Error('No se encontro el cliente E2E en el selector de reparaciones')
    }

    await page.getByTestId('repair-client').selectOption(clientValue)
    await page.getByTestId('repair-model').fill(modelName)
    await page.getByTestId('repair-problem').fill('No enciende correctamente en prueba E2E')
    await page.getByTestId('repair-paid-amount').fill('25000')
    await page.getByTestId('repair-payment-method').selectOption('transfer')
    await page.getByTestId('repair-save').click()

    const createdRow = page.getByTestId('repair-row').filter({ hasText: modelName })
    await expect(createdRow).toBeVisible()

    await createdRow.getByTestId('repair-edit').click()
    await expect(page).toHaveURL(/\/admin\/repairs\/\d+$/)
    await waitForAppToSettle(page)
    await expect(page.getByTestId('repair-current-status')).toContainText('Ingreso')

    await page.getByTestId('repair-transition-2').click()
    await page.getByTestId('repair-status-confirm').click()
    await expect(page.getByTestId('repair-current-status')).toContainText('Diagnóstico')

    page.on('dialog', (dialog) => dialog.accept())
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    const updatedRow = page.getByTestId('repair-row').filter({ hasText: modelName })
    await expect(updatedRow).toBeVisible()
    await updatedRow.getByTestId('repair-delete').click()
    await expect(page.getByTestId('repair-row').filter({ hasText: modelName })).toHaveCount(0)
    await expectNoBrowserErrors(tracker)
  })
})
