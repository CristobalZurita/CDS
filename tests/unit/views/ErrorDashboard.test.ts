import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'

const buildLoggingRequestHeadersMock = vi.hoisted(() => vi.fn(() => ({ 'x-test': '1' })))
const loggerMock = vi.hoisted(() => ({
  error: vi.fn(),
  info: vi.fn(),
}))

vi.mock('@/services/logging', () => ({
  buildLoggingRequestHeaders: buildLoggingRequestHeadersMock,
  logger: loggerMock,
}))

import ErrorDashboard from '@/views/admin/ErrorDashboard.vue'

describe('ErrorDashboard view', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  it('loads stats and logs on mount and allows local filtering', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString()

      if (url.includes('/api/logs/stats')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            totalLogs: 5,
            errorCount: 2,
            criticalCount: 1,
            avgDurationMs: 123.4,
            slowOperations: [],
          }),
        } as Response)
      }

      if (url.includes('/api/logs')) {
        return Promise.resolve({
          ok: true,
          json: async () => ([
            {
              id: 'log-1',
              level: 'ERROR',
              message: 'Backend timeout',
              context: { route: '/inventory' },
              timestamp: '2026-03-04T00:00:00.000Z',
            },
          ]),
        } as Response)
      }

      return Promise.resolve({
        ok: false,
        json: async () => ({}),
      } as Response)
    })
    vi.stubGlobal('fetch', fetchMock)

    const wrapper = mount(ErrorDashboard)
    await flushPromises()

    expect(buildLoggingRequestHeadersMock).toHaveBeenCalled()
    expect(fetchMock).toHaveBeenCalled()
    expect(wrapper.text()).toContain('Error Monitoring Dashboard')
    expect(wrapper.text()).toContain('Total Logs')
    expect(wrapper.text()).toContain('5')
    expect(wrapper.text()).toContain('Backend timeout')

    const levelSelect = wrapper.find('select')
    await levelSelect.setValue('ERROR')
    await flushPromises()
    expect(wrapper.text()).toContain('ERROR')

    wrapper.unmount()
    vi.useRealTimers()
  })
})
