import { beforeEach, describe, expect, it, vi } from 'vitest'

const authStoreState = vi.hoisted(() => ({
  isAuthenticated: false,
  isAdmin: false,
  checkAuth: vi.fn(async () => undefined),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreState,
}))

async function loadRouter() {
  vi.resetModules()
  const module = await import('@/router/index')
  return module.default
}

describe('router guards', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    authStoreState.isAuthenticated = false
    authStoreState.isAdmin = false
    authStoreState.checkAuth.mockResolvedValue(undefined)
    window.history.pushState({}, '', '/')
  })

  it('redirects unauthenticated users to login with the original target in query', async () => {
    const router = await loadRouter()

    await router.push('/admin')

    expect(authStoreState.checkAuth).toHaveBeenCalled()
    expect(router.currentRoute.value.name).toBe('login')
    expect(router.currentRoute.value.query.redirect).toBe('/admin')
  })

  it('redirects authenticated non-admin users away from admin routes', async () => {
    authStoreState.isAuthenticated = true
    const router = await loadRouter()

    await router.push('/admin')

    expect(router.currentRoute.value.fullPath).toBe('/')
  })

  it('redirects authenticated users away from guest-only routes', async () => {
    authStoreState.isAuthenticated = true
    const router = await loadRouter()

    await router.push('/login')

    expect(router.currentRoute.value.fullPath).toBe('/dashboard')
  })

  it('redirects unknown routes to home', async () => {
    const router = await loadRouter()

    await router.push('/ruta-que-no-existe')

    expect(router.currentRoute.value.fullPath).toBe('/')
  })
})
