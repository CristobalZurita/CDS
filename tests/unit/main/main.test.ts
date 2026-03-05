import { afterEach, describe, expect, it, vi } from 'vitest'
import { AnalyticsEvents } from '@/analytics/events'

describe('main bootstrap', () => {
  afterEach(() => {
    vi.unstubAllEnvs()
    vi.restoreAllMocks()
  })

  it('initializes app, analytics, service worker flows and number-input wheel handler', async () => {
    vi.resetModules()

    const appUse = vi.fn().mockReturnThis()
    const appMount = vi.fn()
    const createAppMock = vi.fn(() => ({
      use: appUse,
      mount: appMount,
    }))
    const createPiniaMock = vi.fn(() => 'pinia-instance')
    const afterEachHandlerRef: { current: null | ((to: any) => void) } = { current: null }
    const routerMock = {
      afterEach: vi.fn((handler: (to: any) => void) => {
        afterEachHandlerRef.current = handler
      }),
    }
    const authStoreMock = {
      checkAuth: vi.fn(),
    }
    const initAnalyticsMock = vi.fn()
    const trackMock = vi.fn()

    vi.doMock('vue', () => ({
      createApp: createAppMock,
    }))
    vi.doMock('pinia', () => ({
      createPinia: createPiniaMock,
    }))
    vi.doMock('/src/vue/stack/App.vue', () => ({
      default: { name: 'AppRoot' },
    }))
    vi.doMock('@/router', () => ({
      default: routerMock,
    }))
    vi.doMock('@/stores/auth', () => ({
      useAuthStore: () => authStoreMock,
    }))
    vi.doMock('@/analytics', () => ({
      initAnalytics: initAnalyticsMock,
      track: trackMock,
    }))

    const registerMock = vi.fn().mockResolvedValue({})
    const unregisterMock = vi.fn().mockResolvedValue(true)
    const getRegistrationsMock = vi.fn().mockResolvedValue([{ unregister: unregisterMock }])
    Object.defineProperty(navigator, 'serviceWorker', {
      configurable: true,
      value: {
        register: registerMock,
        getRegistrations: getRegistrationsMock,
      },
    })

    const cachesDeleteMock = vi.fn().mockResolvedValue(true)
    const cachesKeysMock = vi.fn().mockResolvedValue(['cds-main-cache', 'other-cache'])
    Object.defineProperty(window, 'caches', {
      configurable: true,
      value: {
        keys: cachesKeysMock,
        delete: cachesDeleteMock,
      },
    })

    const env = import.meta.env as any
    env.PROD = true
    env.DEV = true
    vi.stubEnv('VITE_GA_ID', 'G-TEST-123')
    ;(window as any).__gaLoaded = false
    ;(window as any).dataLayer = []
    ;(window as any).gtag = undefined

    await import('@/main.js')

    expect(createAppMock).toHaveBeenCalled()
    expect(createPiniaMock).toHaveBeenCalled()
    expect(appUse).toHaveBeenCalledWith('pinia-instance')
    expect(appUse).toHaveBeenCalledWith(routerMock)
    expect(appMount).toHaveBeenCalledWith('#app')
    expect(authStoreMock.checkAuth).toHaveBeenCalled()
    expect(initAnalyticsMock).toHaveBeenCalled()

    expect(routerMock.afterEach).toHaveBeenCalled()
    expect(afterEachHandlerRef.current).toBeTypeOf('function')
    afterEachHandlerRef.current?.({ fullPath: '/admin/stats', name: 'admin-stats' })
    expect(trackMock).toHaveBeenCalledWith(
      AnalyticsEvents.PAGE_VIEW,
      expect.objectContaining({
        path: '/admin/stats',
        name: 'admin-stats',
      })
    )

    window.dispatchEvent(new Event('load'))
    await Promise.resolve()
    await Promise.resolve()

    expect(registerMock).toHaveBeenCalledWith('/sw.js')
    expect(getRegistrationsMock).toHaveBeenCalled()
    expect(unregisterMock).toHaveBeenCalled()
    expect(cachesKeysMock).toHaveBeenCalled()
    expect(cachesDeleteMock).toHaveBeenCalledWith('cds-main-cache')

    const numberInput = document.createElement('input')
    numberInput.type = 'number'
    const focusMock = vi.fn()
    const stepUpMock = vi.fn()
    const stepDownMock = vi.fn()
    Object.defineProperty(numberInput, 'focus', { value: focusMock })
    Object.defineProperty(numberInput, 'stepUp', { value: stepUpMock })
    Object.defineProperty(numberInput, 'stepDown', { value: stepDownMock })
    document.body.appendChild(numberInput)

    const wheelUp = new WheelEvent('wheel', { deltaY: -1, bubbles: true, cancelable: true })
    numberInput.dispatchEvent(wheelUp)
    expect(focusMock).toHaveBeenCalled()
    expect(stepUpMock).toHaveBeenCalled()

    const wheelDown = new WheelEvent('wheel', { deltaY: 1, bubbles: true, cancelable: true })
    numberInput.dispatchEvent(wheelDown)
    expect(stepDownMock).toHaveBeenCalled()
  })
})
