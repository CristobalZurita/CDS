import { test, expect, type Page } from '@playwright/test'
import { resolveAuthState } from './helpers/auth'
import { expectNoBrowserErrors, trackBrowserErrors, waitForAppToSettle } from './helpers/page'

type Scope = 'public' | 'client' | 'admin'

type ActionAudit = {
  route: string
  actions: Array<{
    name: string
    run: (page: Page) => Promise<void>
  }>
}

const linkSeeds: Record<Scope, string[]> = {
  public: ['/', '/login', '/cotizador-ia', '/calculadoras'],
  client: ['/dashboard', '/repairs', '/profile'],
  admin: ['/admin', '/admin/inventory', '/admin/repairs', '/admin/categories', '/admin/clients'],
}

const skippedPrefixes: Record<Scope, string[]> = {
  public: ['/admin', '/dashboard', '/repairs', '/profile', '/ot-payments', '/agendar'],
  client: ['/admin'],
  admin: [],
}

const adminActionAudits: ActionAudit[] = [
  {
    route: '/admin',
    actions: [
      {
        name: 'refresh users',
        run: async (page) => {
          await page.getByTestId('users-refresh').click()
        },
      },
      {
        name: 'open user form',
        run: async (page) => {
          await page.getByTestId('users-new').click()
          await expect(page.getByTestId('user-form')).toBeVisible()
        },
      },
      {
        name: 'close user form',
        run: async (page) => {
          await page.getByTestId('users-new').click()
          await expect(page.getByTestId('user-form')).toHaveCount(0)
        },
      },
    ],
  },
  {
    route: '/admin/clients',
    actions: [
      {
        name: 'refresh clients',
        run: async (page) => {
          await page.getByTestId('clients-refresh').click()
        },
      },
      {
        name: 'search clients',
        run: async (page) => {
          await page.getByTestId('clients-search').fill('E2E')
        },
      },
      {
        name: 'close intake form',
        run: async (page) => {
          await page.getByTestId('clients-intake-toggle').click()
          await expect(page.getByTestId('clients-intake')).toHaveCount(0)
        },
      },
      {
        name: 'open intake form',
        run: async (page) => {
          await page.getByTestId('clients-intake-toggle').click()
          await expect(page.getByTestId('clients-intake')).toBeVisible()
        },
      },
    ],
  },
  {
    route: '/admin/categories',
    actions: [
      {
        name: 'refresh categories',
        run: async (page) => {
          await page.getByTestId('categories-refresh').click()
        },
      },
      {
        name: 'open category form',
        run: async (page) => {
          await page.getByTestId('categories-new').click()
          await expect(page.getByTestId('category-form')).toBeVisible()
        },
      },
      {
        name: 'close category form',
        run: async (page) => {
          await page.getByTestId('categories-new').click()
          await expect(page.getByTestId('category-form')).toHaveCount(0)
        },
      },
    ],
  },
  {
    route: '/admin/inventory/unified',
    actions: [
      {
        name: 'filter unified inventory',
        run: async (page) => {
          await page.getByTestId('inventory-unified-filter').fill('res')
        },
      },
      {
        name: 'search unified inventory',
        run: async (page) => {
          await page.getByTestId('inventory-unified-search').click()
        },
      },
    ],
  },
  {
    route: '/admin/inventory',
    actions: [
      {
        name: 'switch inventory manage view',
        run: async (page) => {
          await page.getByTestId('inventory-view-manage').click()
          await expect(page.getByTestId('inventory-refresh')).toBeVisible()
        },
      },
      {
        name: 'open inventory form',
        run: async (page) => {
          await page.getByTestId('inventory-new').click()
          await expect(page.getByTestId('inventory-form')).toBeVisible()
        },
      },
      {
        name: 'close inventory form',
        run: async (page) => {
          await page.getByTestId('inventory-cancel').click()
          await expect(page.getByTestId('inventory-form')).toHaveCount(0)
        },
      },
      {
        name: 'switch inventory sheet view',
        run: async (page) => {
          await page.getByTestId('inventory-view-sheet').click()
          await expect(page.getByTestId('inventory-new')).toBeVisible()
        },
      },
      {
        name: 'switch inventory states view',
        run: async (page) => {
          await page.getByTestId('inventory-view-states').click()
          await expect(page.getByTestId('inventory-new')).toBeVisible()
        },
      },
      {
        name: 'refresh inventory',
        run: async (page) => {
          await page.getByTestId('inventory-refresh').click()
        },
      },
    ],
  },
  {
    route: '/admin/quotes',
    actions: [
      {
        name: 'search quotes',
        run: async (page) => {
          await page.getByTestId('quotes-search').fill('COT')
        },
      },
      {
        name: 'filter quotes by status',
        run: async (page) => {
          await page.getByTestId('quotes-status-filter').selectOption('pending')
          await expect(page.getByTestId('quotes-board')).toBeVisible()
        },
      },
      {
        name: 'refresh quotes',
        run: async (page) => {
          await page.getByTestId('quotes-refresh').click()
          await expect(page.getByTestId('quotes-summary')).toBeVisible()
        },
      },
    ],
  },
  {
    route: '/admin/repairs',
    actions: [
      {
        name: 'refresh repairs',
        run: async (page) => {
          await page.getByTestId('repairs-refresh').click()
        },
      },
      {
        name: 'open repair form',
        run: async (page) => {
          await page.getByTestId('repairs-new').click()
          await expect(page.getByTestId('repair-form')).toBeVisible()
        },
      },
      {
        name: 'close repair form',
        run: async (page) => {
          await page.getByTestId('repairs-new').click()
          await expect(page.getByTestId('repair-form')).toHaveCount(0)
        },
      },
    ],
  },
  {
    route: '/admin/appointments',
    actions: [
      {
        name: 'filter appointments pending',
        run: async (page) => {
          await page.getByTestId('appointments-filter-pending').click()
        },
      },
      {
        name: 'filter appointments confirmed',
        run: async (page) => {
          await page.getByTestId('appointments-filter-confirmed').click()
        },
      },
      {
        name: 'restore appointments all',
        run: async (page) => {
          await page.getByTestId('appointments-filter-all').click()
        },
      },
      {
        name: 'refresh appointments',
        run: async (page) => {
          await page.getByTestId('appointments-refresh').click()
        },
      },
    ],
  },
  {
    route: '/admin/contact',
    actions: [
      {
        name: 'refresh contact messages',
        run: async (page) => {
          await page.getByTestId('contact-refresh').click()
        },
      },
    ],
  },
  {
    route: '/admin/newsletter',
    actions: [
      {
        name: 'refresh newsletter subscriptions',
        run: async (page) => {
          await page.getByTestId('newsletter-refresh').click()
        },
      },
    ],
  },
  {
    route: '/admin/tickets',
    actions: [
      {
        name: 'refresh tickets',
        run: async (page) => {
          await page.getByTestId('tickets-refresh').click()
        },
      },
      {
        name: 'open ticket wizard',
        run: async (page) => {
          await page.getByTestId('tickets-new').click()
          await expect(page.getByTestId('tickets-wizard')).toBeVisible()
        },
      },
      {
        name: 'close ticket wizard',
        run: async (page) => {
          await page.getByTestId('tickets-new').click()
          await expect(page.getByTestId('tickets-wizard')).toHaveCount(0)
        },
      },
    ],
  },
  {
    route: '/admin/purchase-requests',
    actions: [
      {
        name: 'refresh purchase requests',
        run: async (page) => {
          await page.getByTestId('purchase-requests-refresh').click()
        },
      },
      {
        name: 'open purchase request wizard',
        run: async (page) => {
          await page.getByTestId('purchase-requests-new').click()
          await expect(page.getByTestId('purchase-requests-wizard')).toBeVisible()
        },
      },
      {
        name: 'close purchase request wizard',
        run: async (page) => {
          await page.getByTestId('purchase-requests-new').click()
          await expect(page.getByTestId('purchase-requests-wizard')).toHaveCount(0)
        },
      },
    ],
  },
  {
    route: '/admin/manuals',
    actions: [
      {
        name: 'refresh manuals',
        run: async (page) => {
          await page.getByTestId('manuals-refresh').click()
        },
      },
      {
        name: 'open manuals wizard',
        run: async (page) => {
          await page.getByTestId('manuals-new').click()
          await expect(page.getByTestId('manuals-wizard')).toBeVisible()
        },
      },
      {
        name: 'close manuals wizard',
        run: async (page) => {
          await page.getByTestId('manuals-new').click()
          await expect(page.getByTestId('manuals-wizard')).toHaveCount(0)
        },
      },
    ],
  },
  {
    route: '/admin/stats',
    actions: [
      {
        name: 'stats shell renders',
        run: async (page) => {
          await expect(page.getByTestId('admin-shell')).toBeVisible()
        },
      },
    ],
  },
  {
    route: '/admin/archive',
    actions: [
      {
        name: 'search archive',
        run: async (page) => {
          await page.getByTestId('archive-search').fill('OT')
        },
      },
      {
        name: 'refresh archive',
        run: async (page) => {
          await page.getByTestId('archive-refresh').click()
          await expect(page.getByTestId('archive-table')).toBeVisible()
        },
      },
    ],
  },
]

function normalizePath(rawPath: string) {
  const url = new URL(rawPath, process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:5174')
  const normalized = url.pathname.replace(/\/+$/, '')
  return normalized || '/'
}

function shouldAuditPath(path: string, scope: Scope) {
  if (!path.startsWith('/')) return false
  if (path === '/logout') return false
  if (skippedPrefixes[scope].some((prefix) => path === prefix || path.startsWith(`${prefix}/`))) {
    return false
  }
  return true
}

async function collectVisibleInternalPaths(page: Page, scope: Scope) {
  const hrefs = await page.locator('a[href]').evaluateAll((anchors) =>
    anchors
      .map((anchor) => {
        const href = anchor.getAttribute('href')
        if (!href) return null

        const style = window.getComputedStyle(anchor)
        const rect = anchor.getBoundingClientRect()
        const visible =
          style.display !== 'none' &&
          style.visibility !== 'hidden' &&
          rect.width > 0 &&
          rect.height > 0

        if (!visible) return null

        if (
          href.startsWith('mailto:') ||
          href.startsWith('tel:') ||
          href.startsWith('javascript:') ||
          href.startsWith('#')
        ) {
          return null
        }

        try {
          const url = new URL(href, window.location.origin)
          if (url.origin !== window.location.origin) return null
          return url.pathname
        } catch {
          return null
        }
      })
      .filter(Boolean)
  )

  return [...new Set(hrefs.map((href) => normalizePath(String(href))).filter((href) => shouldAuditPath(href, scope)))]
}

async function auditDiscoveredLinks(page: Page, scope: Scope) {
  const discovered = new Set<string>()

  for (const seed of linkSeeds[scope]) {
    const tracker = trackBrowserErrors(page)
    await page.goto(seed)
    await waitForAppToSettle(page)
    await expect(page.locator('body')).toBeVisible()
    const paths = await collectVisibleInternalPaths(page, scope)
    paths.forEach((path) => discovered.add(path))
    await expectNoBrowserErrors(tracker)
  }

  for (const target of discovered) {
    const auditPage = await page.context().newPage()
    const tracker = trackBrowserErrors(auditPage)
    auditPage.on('dialog', (dialog) => dialog.accept())

    await auditPage.goto(target)
    await waitForAppToSettle(auditPage)

    await expect(auditPage.locator('body')).toBeVisible()
    await expect
      .poll(async () => normalizePath(await auditPage.evaluate(() => window.location.pathname)))
      .toBe(normalizePath(target))

    await expectNoBrowserErrors(tracker)
    await auditPage.close()
  }
}

async function runActionAudit(page: Page, audit: ActionAudit) {
  const tracker = trackBrowserErrors(page)
  page.on('dialog', (dialog) => dialog.accept())

  await page.goto(audit.route)
  await waitForAppToSettle(page)
  await expect(page.locator('body')).toBeVisible()

  for (const action of audit.actions) {
    await test.step(`${audit.route} :: ${action.name}`, async () => {
      await action.run(page)
      await page.waitForTimeout(350)
    })
  }

  await expectNoBrowserErrors(tracker)
}

test.describe('site audit link graph', () => {
  test('public visible internal links resolve cleanly', async ({ page }) => {
    await auditDiscoveredLinks(page, 'public')
  })

  test.describe('client scope', () => {
    test.use({ storageState: resolveAuthState('client') })

    test('client visible internal links resolve cleanly', async ({ page }) => {
      await auditDiscoveredLinks(page, 'client')
    })
  })

  test.describe('admin scope', () => {
    test.use({ storageState: resolveAuthState('admin') })

    test('admin visible internal links resolve cleanly', async ({ page }) => {
      await auditDiscoveredLinks(page, 'admin')
    })
  })
})

test.describe('site audit safe actions', () => {
  test.use({ storageState: resolveAuthState('admin') })

  for (const audit of adminActionAudits) {
    test(`admin actions work on ${audit.route}`, async ({ page }) => {
      await runActionAudit(page, audit)
    })
  }
})
