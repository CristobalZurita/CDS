/**
 * Setup de autenticación para tests E2E
 * Este archivo corre antes de los otros tests para crear los estados de auth
 */

import { test as setup } from '@playwright/test'
import { setupAuth } from './helpers/auth.js'

// Configurar usuarios de test
// NOTA: Estos usuarios deben existir en la base de datos
const USERS = {
  admin: {
    email: process.env.TEST_ADMIN_EMAIL || 'admin@example.com',
    password: process.env.TEST_ADMIN_PASSWORD || 'admin123'
  },
  client: {
    email: process.env.TEST_CLIENT_EMAIL || 'client@example.com',
    password: process.env.TEST_CLIENT_PASSWORD || 'client123'
  }
}

setup('authenticate as admin', async ({ page }) => {
  console.log('Setting up admin auth...')
  await setupAuth(page, 'admin', USERS.admin)
  console.log('Admin auth saved')
})

setup('authenticate as client', async ({ page }) => {
  console.log('Setting up client auth...')
  await setupAuth(page, 'client', USERS.client)
  console.log('Client auth saved')
})
