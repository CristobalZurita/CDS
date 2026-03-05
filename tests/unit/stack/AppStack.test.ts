import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AnalyticsEvents } from '@/analytics/events'

const authStoreMock = vi.hoisted(() => ({}))
const initAnalyticsMock = vi.hoisted(() => vi.fn())
const trackMock = vi.hoisted(() => vi.fn())
const setToastComponentMock = vi.hoisted(() => vi.fn())

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
}))

vi.mock('@/analytics', () => ({
  initAnalytics: initAnalyticsMock,
  track: trackMock,
}))

vi.mock('@/services/toastService', () => ({
  setToastComponent: setToastComponentMock,
}))

import App from '@/vue/stack/App.vue'

describe('App stack root', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('wires toast registration and analytics tracking on mount', async () => {
    const wrapper = mount(App, {
      global: {
        stubs: {
          RouterView: {
            template: '<div data-testid="router-view-stub" />',
          },
          ToastNotification: {
            template: '<div data-testid="toast-stub" />',
          },
          StoreCartWidget: {
            template: '<div data-testid="cart-widget-stub" />',
          },
        },
      },
    })

    await flushPromises()

    expect(setToastComponentMock).toHaveBeenCalled()
    expect(initAnalyticsMock).toHaveBeenCalled()
    expect(trackMock).toHaveBeenCalledWith(
      AnalyticsEvents.PAGE_VIEW,
      expect.objectContaining({
        page: window.location.pathname,
      })
    )
  })
})
