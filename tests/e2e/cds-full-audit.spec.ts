import fs from 'node:fs'
import path from 'node:path'
import { test, expect, Page } from '@playwright/test'

const BASE = 'http://localhost:5173'
const API = 'http://localhost:8000'

// Credentials from PHASE 0 seed scripts only
const ADMIN = { email: 'admin@example.com', password: 'admin12' }
const _CLIENT = { email: 'test@example.com', password: 'test12' }

type RouteCase = {
  key: string
  path: string
  auth: boolean
  admin: boolean
  dynamic?: 'repairId' | 'signatureToken' | 'photoToken' | 'catchall'
}

const PUBLIC_ROUTES = [
  '/',
  '/license',
  '/policy',
  '/terminos',
  '/privacidad',
  '/cotizador-ia',
  '/calculadoras',
  '/login',
  '/register',
  '/password-reset',
  '/calc/555',
  '/calc/resistor-color',
  '/calc/smd-capacitor',
  '/calc/smd-resistor',
  '/calc/ohms-law',
  '/calc/temperature',
  '/calc/number-system',
  '/calc/length',
  '/calc/awg',
  '/signature/:token',
  '/photo-upload/:token',
  '/:pathMatch(.*)*'
]

const _AUTH_REQUIRED_ROUTES = [
  '/agendar',
  '/dashboard',
  '/repairs',
  '/repairs/:id',
  '/profile',
  '/admin',
  '/admin/inventory',
  '/admin/inventory/unified',
  '/admin/clients',
  '/admin/repairs',
  '/admin/repairs/:id',
  '/admin/categories',
  '/admin/contact',
  '/admin/newsletter',
  '/admin/appointments',
  '/admin/tickets',
  '/admin/purchase-requests',
  '/admin/archive',
  '/admin/manuals'
]

const _ADMIN_ONLY_ROUTES = [
  '/admin',
  '/admin/inventory',
  '/admin/inventory/unified',
  '/admin/clients',
  '/admin/repairs',
  '/admin/repairs/:id',
  '/admin/categories',
  '/admin/contact',
  '/admin/newsletter',
  '/admin/appointments',
  '/admin/tickets',
  '/admin/purchase-requests',
  '/admin/archive',
  '/admin/manuals'
]

const _NESTED_ROUTES = [
  {
    parent: '/',
    children: ['', 'license', 'policy', 'terminos', 'privacidad', 'agendar', 'cotizador-ia', 'calculadoras']
  },
  {
    parent: '/admin',
    children: ['', 'inventory', 'inventory/unified', 'clients', 'repairs', 'repairs/:id', 'categories', 'contact', 'newsletter', 'appointments', 'tickets', 'purchase-requests', 'archive', 'manuals']
  }
]

const ALL_43_ROUTE_ENTRIES: RouteCase[] = [
  { key: 'root-parent', path: '/', auth: false, admin: false },
  { key: 'root-home-child', path: '/', auth: false, admin: false },
  { key: 'root-license', path: '/license', auth: false, admin: false },
  { key: 'root-policy', path: '/policy', auth: false, admin: false },
  { key: 'root-terminos', path: '/terminos', auth: false, admin: false },
  { key: 'root-privacidad', path: '/privacidad', auth: false, admin: false },
  { key: 'root-agendar', path: '/agendar', auth: true, admin: false },
  { key: 'root-cotizador', path: '/cotizador-ia', auth: false, admin: false },
  { key: 'root-calculadoras', path: '/calculadoras', auth: false, admin: false },
  { key: 'login', path: '/login', auth: false, admin: false },
  { key: 'register', path: '/register', auth: false, admin: false },
  { key: 'password-reset', path: '/password-reset', auth: false, admin: false },
  { key: 'dashboard', path: '/dashboard', auth: true, admin: false },
  { key: 'repairs', path: '/repairs', auth: true, admin: false },
  { key: 'repair-detail', path: '/repairs/:id', auth: true, admin: false, dynamic: 'repairId' },
  { key: 'profile', path: '/profile', auth: true, admin: false },
  { key: 'admin-parent', path: '/admin', auth: true, admin: true },
  { key: 'admin-dashboard-child', path: '/admin', auth: true, admin: true },
  { key: 'admin-inventory', path: '/admin/inventory', auth: true, admin: true },
  { key: 'admin-inventory-unified', path: '/admin/inventory/unified', auth: true, admin: true },
  { key: 'admin-clients', path: '/admin/clients', auth: true, admin: true },
  { key: 'admin-repairs', path: '/admin/repairs', auth: true, admin: true },
  { key: 'admin-repair-detail', path: '/admin/repairs/:id', auth: true, admin: true, dynamic: 'repairId' },
  { key: 'admin-categories', path: '/admin/categories', auth: true, admin: true },
  { key: 'admin-contact', path: '/admin/contact', auth: true, admin: true },
  { key: 'admin-newsletter', path: '/admin/newsletter', auth: true, admin: true },
  { key: 'admin-appointments', path: '/admin/appointments', auth: true, admin: true },
  { key: 'admin-tickets', path: '/admin/tickets', auth: true, admin: true },
  { key: 'admin-purchase', path: '/admin/purchase-requests', auth: true, admin: true },
  { key: 'admin-archive', path: '/admin/archive', auth: true, admin: true },
  { key: 'admin-manuals-redirect', path: '/admin/manuals', auth: true, admin: true },
  { key: 'signature', path: '/signature/:token', auth: false, admin: false, dynamic: 'signatureToken' },
  { key: 'photo-upload', path: '/photo-upload/:token', auth: false, admin: false, dynamic: 'photoToken' },
  { key: 'calc-555', path: '/calc/555', auth: false, admin: false },
  { key: 'calc-resistor', path: '/calc/resistor-color', auth: false, admin: false },
  { key: 'calc-smd-capacitor', path: '/calc/smd-capacitor', auth: false, admin: false },
  { key: 'calc-smd-resistor', path: '/calc/smd-resistor', auth: false, admin: false },
  { key: 'calc-ohms', path: '/calc/ohms-law', auth: false, admin: false },
  { key: 'calc-temp', path: '/calc/temperature', auth: false, admin: false },
  { key: 'calc-number', path: '/calc/number-system', auth: false, admin: false },
  { key: 'calc-length', path: '/calc/length', auth: false, admin: false },
  { key: 'calc-awg', path: '/calc/awg', auth: false, admin: false },
  { key: 'catchall', path: '/__cds_route_not_found__', auth: false, admin: false, dynamic: 'catchall' }
]

const PHASE0_OPENAPI_MAP_PATH = path.resolve(process.cwd(), 'reports/PHASE0_OPENAPI_MAP.json')
const PHASE0_OPENAPI_MAP = JSON.parse(fs.readFileSync(PHASE0_OPENAPI_MAP_PATH, 'utf-8')) as {
  methods: Record<string, string[]>
  protected_get: string[]
}

const GET_ENDPOINTS: string[] = PHASE0_OPENAPI_MAP.methods.GET || []
const PROTECTED_GET_ENDPOINTS: string[] = PHASE0_OPENAPI_MAP.protected_get || []

const STATIC_GET_ENDPOINTS = GET_ENDPOINTS.filter((ep) => !ep.includes('{'))
const STATIC_PROTECTED_GET_ENDPOINTS = PROTECTED_GET_ENDPOINTS.filter((ep) => !ep.includes('{'))

async function apiLogin(request: Page['request'], user: typeof ADMIN) {
  const res = await request.post(`${API}/api/v1/auth/login`, {
    data: { email: user.email, password: user.password }
  })
  expect(res.status(), `api login failed for ${user.email}`).toBe(200)
  const body = await res.json()
  return {
    accessToken: body.access_token as string,
    refreshToken: body.refresh_token as string
  }
}

async function loginAs(page: Page, user: typeof ADMIN) {
  // Actual login route from router: /login (src/router/index.js:101)
  await page.goto(BASE + '/login')
  // Actual selectors from src/vue/components/auth/LoginForm.vue:7 and :22
  await page.fill('#email', user.email)
  await page.fill('#password', user.password)
  // Actual submit button in LoginForm.vue:55-62
  await page.click('button[type="submit"]')
  await page.waitForURL(/\/(admin|dashboard|login)(\?.*)?$/, { timeout: 10000 })
}

async function injectAuth(page: Page, user: typeof ADMIN) {
  const tokens = await apiLogin(page.request, user)
  await page.addInitScript((payload) => {
    localStorage.setItem('access_token', payload.accessToken)
    localStorage.setItem('refresh_token', payload.refreshToken)
  }, tokens)
}

async function getFirstRepairId(page: Page, token: string): Promise<number | null> {
  const res = await page.request.get(`${API}/api/v1/repairs/`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  if (res.status() >= 500) return null
  const data = await res.json().catch(() => [])
  if (!Array.isArray(data) || data.length === 0) return null
  const id = Number(data[0]?.id)
  return Number.isFinite(id) ? id : null
}

async function resolveRoutePath(page: Page, route: RouteCase, token?: string): Promise<string | null> {
  if (!route.dynamic || route.dynamic === 'catchall') return route.path

  if (!token) return null

  if (route.dynamic === 'repairId') {
    const repairId = await getFirstRepairId(page, token)
    if (!repairId) return null
    return route.path.replace(':id', String(repairId))
  }

  if (route.dynamic === 'signatureToken') {
    const repairId = await getFirstRepairId(page, token)
    if (!repairId) return null
    const res = await page.request.post(`${API}/api/v1/signatures/requests`, {
      headers: { Authorization: `Bearer ${token}` },
      data: { repair_id: repairId, request_type: 'ingreso', expires_minutes: 30 }
    })
    if (!res.ok()) return null
    const body = await res.json().catch(() => ({}))
    const signatureToken = body?.token
    if (!signatureToken) return null
    return route.path.replace(':token', String(signatureToken))
  }

  if (route.dynamic === 'photoToken') {
    const repairId = await getFirstRepairId(page, token)
    if (!repairId) return null
    const res = await page.request.post(`${API}/api/v1/photo-requests/`, {
      headers: { Authorization: `Bearer ${token}` },
      params: { repair_id: String(repairId), photo_type: 'client', expires_minutes: '60' }
    })
    if (!res.ok()) return null
    const body = await res.json().catch(() => ({}))
    const photoToken = body?.token
    if (!photoToken) return null
    return route.path.replace(':token', String(photoToken))
  }

  return null
}

// ─── BLOCK 1: PUBLIC ROUTES ───────────────────────────────────────────
test('public: HOME loads and renders', async ({ page }) => {
  const errors: string[] = []
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(msg.text())
  })
  await page.goto(BASE + '/')
  await expect(page.locator('#app')).not.toBeEmpty()
  expect(errors.filter((e) => !e.includes('favicon'))).toHaveLength(0)
})

for (const route of PUBLIC_ROUTES.filter((r) => !r.includes(':') && !r.includes('pathMatch'))) {
  test(`public: route ${route} responds`, async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', (err) => errors.push(err.message))
    await page.goto(BASE + route)
    await page.waitForLoadState('networkidle')
    await expect(page.locator('#app')).toBeVisible()
    expect(errors).toHaveLength(0)
  })
}

// ─── BLOCK 2: AUTH FLOW ───────────────────────────────────────────────
test('auth: admin can login', async ({ page }) => {
  await loginAs(page, ADMIN)
  await expect(page).toHaveURL(/\/(admin|dashboard)/)
})

test('auth: protected route redirects to login when not authenticated', async ({ page }) => {
  // First protected route in PHASE 0: /agendar
  await page.goto(BASE + '/agendar')
  await page.waitForURL('**/login**')
})

test('auth: admin can logout', async ({ page }) => {
  await injectAuth(page, ADMIN)
  await page.goto(BASE + '/admin')
  // Logout selector from src/vue/components/admin/layout/AdminTopbar.vue:30
  await page.click('.btn-logout')
  await page.waitForURL('**/login')
})

// ─── BLOCK 3: ALL 43 ROUTES ───────────────────────────────────────────
for (const route of ALL_43_ROUTE_ENTRIES) {
  test(`route: ${route.key} ${route.path} loads without crash`, async ({ page }) => {
    let accessToken: string | undefined
    if (route.auth) {
      const tokens = await apiLogin(page.request, ADMIN)
      accessToken = tokens.accessToken
      await page.addInitScript((payload) => {
        localStorage.setItem('access_token', payload.accessToken)
        localStorage.setItem('refresh_token', payload.refreshToken)
      }, tokens)
    }

    const resolved = await resolveRoutePath(page, route, accessToken)
    if (!resolved) {
      test.skip(true, `Route requires dynamic data not available: ${route.path}`)
      return
    }

    const errors: string[] = []
    page.on('pageerror', (err) => errors.push(err.message))

    await page.goto(BASE + resolved)
    await page.waitForLoadState('networkidle')
    expect(errors).toHaveLength(0)

    if (route.auth) {
      await expect(page).not.toHaveURL(/\/login/)
    }
  })
}

// ─── BLOCK 4: ALL BUTTONS ─────────────────────────────────────────────
const BUTTON_ROUTE_CASES: RouteCase[] = [
  { key: 'btn-login', path: '/login', auth: false, admin: false },
  { key: 'btn-register', path: '/register', auth: false, admin: false },
  { key: 'btn-dashboard', path: '/dashboard', auth: true, admin: false },
  { key: 'btn-repairs', path: '/repairs', auth: true, admin: false },
  { key: 'btn-profile', path: '/profile', auth: true, admin: false },
  { key: 'btn-agendar', path: '/agendar', auth: true, admin: false },
  { key: 'btn-admin-dashboard', path: '/admin', auth: true, admin: true },
  { key: 'btn-admin-inventory', path: '/admin/inventory', auth: true, admin: true },
  { key: 'btn-admin-clients', path: '/admin/clients', auth: true, admin: true },
  { key: 'btn-admin-repairs', path: '/admin/repairs', auth: true, admin: true },
  { key: 'btn-admin-appointments', path: '/admin/appointments', auth: true, admin: true },
  { key: 'btn-admin-archive', path: '/admin/archive', auth: true, admin: true },
  { key: 'btn-admin-tickets', path: '/admin/tickets', auth: true, admin: true },
  { key: 'btn-admin-purchase', path: '/admin/purchase-requests', auth: true, admin: true }
]

for (const route of BUTTON_ROUTE_CASES) {
  test(`button: ${route.path} click actions do not crash`, async ({ page }) => {
    if (route.auth) {
      await injectAuth(page, ADMIN)
    }
    await page.goto(BASE + route.path)
    await page.waitForLoadState('networkidle')

    const errors: string[] = []
    page.on('pageerror', (err) => errors.push(err.message))

    const buttons = page.locator('button:visible')
    const count = await buttons.count()
    const maxClicks = Math.min(count, 8)

    for (let i = 0; i < maxClicks; i++) {
      const btn = buttons.nth(i)
      const text = (await btn.innerText().catch(() => '')).trim()
      if (text.toLowerCase().includes('cerrar sesión')) continue
      await btn.click({ timeout: 3000 }).catch(() => null)
      await page.waitForTimeout(150)
    }

    expect(errors).toHaveLength(0)
  })
}

// ─── BLOCK 5: ALL LINKS ───────────────────────────────────────────────
test('links: no 404 links on home page', async ({ page }) => {
  await page.goto(BASE + '/')
  const links = await page.locator('a[href]').all()
  for (const link of links) {
    const href = await link.getAttribute('href')
    if (!href || href.startsWith('#') || href.startsWith('mailto')) continue
    if (href.startsWith('http')) continue

    const route = href.startsWith('/') ? href : `/${href}`
    const response = await page.goto(BASE + route)
    expect(response?.status(), `broken link: ${route}`).not.toBe(404)
    await page.goto(BASE + '/')
  }
})

// ─── BLOCK 6: FORMS ───────────────────────────────────────────────────
test('form: login validates captcha requirement on submit', async ({ page }) => {
  await page.goto(BASE + '/login')
  await page.fill('#email', ADMIN.email)
  await page.fill('#password', ADMIN.password)
  await page.click('button[type="submit"]')
  await expect(page.locator('.alert.alert-danger')).toBeVisible()
})

test('form: register validates captcha requirement on submit', async ({ page }) => {
  await page.goto(BASE + '/register')
  await page.fill('input[type="email"]', 'qa-register@example.com')
  await page.fill('input[type="text"]', 'qauser')
  await page.fill('input[required][type="password"]', 'password123')
  await page.click('button[type="submit"]')
  await expect(page.locator('.alert.alert-danger')).toBeVisible()
})

test('form: inventory validates empty submit', async ({ page }) => {
  await injectAuth(page, ADMIN)
  await page.goto(BASE + '/admin/inventory')
  await page.click('button:has-text("Nuevo item")')
  await page.click('.btn.btn-primary:has-text("Guardar")')
  const requiredName = page.locator('input.form-control[required]').first()
  await expect(requiredName).toBeVisible()
  const invalid = await requiredName.evaluate((el) => !(el as HTMLInputElement).checkValidity())
  expect(invalid).toBeTruthy()
})

test('form: inventory submits successfully with valid data', async ({ page }) => {
  await injectAuth(page, ADMIN)
  await page.goto(BASE + '/admin/inventory')
  await page.click('button:has-text("Nuevo item")')
  await page.fill('input.form-control[required]', `QA item ${Date.now()}`)
  await page.click('.btn.btn-primary:has-text("Guardar")')
  await page.waitForLoadState('networkidle')
  await expect(page.locator('text=Crear item')).toHaveCount(0)
})

// ─── BLOCK 7: API HEALTH ──────────────────────────────────────────────
test('api: all GET endpoints return 200/4xx but never 5xx when authenticated', async ({ page }) => {
  const tokens = await apiLogin(page.request, ADMIN)
  const endpoints = STATIC_GET_ENDPOINTS
  for (const ep of endpoints) {
    const res = await page.request.get(API + ep, {
      headers: { Authorization: `Bearer ${tokens.accessToken}` }
    })
    expect(res.status(), `endpoint ${ep} failed`).toBeLessThan(500)
  }
})

test('api: protected endpoints return 401 without token', async ({ page }) => {
  const protected_endpoints = STATIC_PROTECTED_GET_ENDPOINTS
  for (const ep of protected_endpoints) {
    const res = await page.request.get(API + ep)
    expect(res.status(), `${ep} should be 401`).toBe(401)
  }
})

// ─── BLOCK 8: BROKEN ASSETS ───────────────────────────────────────────
test('assets: no broken images or assets on any page', async ({ page }) => {
  const broken: string[] = []
  page.on('response', (res) => {
    if (res.status() === 404 && !res.url().includes('favicon')) {
      broken.push(res.url())
    }
  })

  const publicStaticRoutes = PUBLIC_ROUTES.filter((r) => !r.includes(':') && !r.includes('pathMatch'))
  for (const route of publicStaticRoutes) {
    await page.goto(BASE + route)
    await page.waitForLoadState('networkidle')
  }
  expect(broken, `broken assets: ${broken.join(', ')}`).toHaveLength(0)
})
