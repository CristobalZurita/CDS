import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  delete: vi.fn(),
}))

const routerPush = vi.hoisted(() => vi.fn())

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

vi.mock('vue-router', () => ({
  useRoute: () => ({ query: {} }),
  useRouter: () => ({ push: routerPush }),
}))

import QuotesAdminPage from '@/vue/content/pages/admin/QuotesAdminPage.vue'

const adminLayoutStub = {
  template: '<div><slot /></div>',
}

function boardPayload(status = 'pending') {
  return {
    data: {
      counts: { draft_pending: 1, waiting_response: 0, closed: 0, total: 1 },
      metrics: { pending: 1, sent: 0, approved: 0, denied: 0, canceled: 0, expired_open: 0, expiring_3d: 0, open_total: 1 },
      board: {
        draft_pending: status === 'pending' ? [{ id: 7, quote_number: 'COT-1', status, client_name: 'E2E Client', estimated_total: 1200, problem_description: 'Fuente' }] : [],
        waiting_response: status === 'sent' ? [{ id: 7, quote_number: 'COT-1', status, client_name: 'E2E Client', estimated_total: 1200, problem_description: 'Fuente' }] : [],
        closed: status === 'approved' ? [{ id: 7, quote_number: 'COT-1', status, client_id: 3, client_name: 'E2E Client', estimated_total: 1200, problem_description: 'Fuente' }] : [],
      },
    },
  }
}

describe('QuotesAdminPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(window, 'confirm').mockReturnValue(true)
  })

  it('loads the board and sends a pending quote', async () => {
    apiMock.get.mockResolvedValueOnce(boardPayload('pending'))
    apiMock.post.mockResolvedValueOnce({})
    apiMock.get.mockResolvedValueOnce(boardPayload('sent'))

    const wrapper = mount(QuotesAdminPage, {
      global: {
        stubs: {
          AdminLayout: adminLayoutStub,
        },
      },
    })

    await flushPromises()
    expect(wrapper.text()).toContain('COT-1')

    await wrapper.get('[data-testid="quote-send"]').trigger('click')
    await flushPromises()

    expect(apiMock.post).toHaveBeenCalledWith('/diagnostic/quotes/7/send', {
      send_whatsapp: true,
      message: null,
    })
    expect(apiMock.get).toHaveBeenCalledTimes(2)
  })

  it('creates a repair from an approved quote and redirects', async () => {
    apiMock.get.mockResolvedValueOnce(boardPayload('approved'))
    apiMock.post.mockResolvedValueOnce({ data: { id: 55 } })
    apiMock.get.mockResolvedValueOnce(boardPayload('approved'))

    const wrapper = mount(QuotesAdminPage, {
      global: {
        stubs: {
          AdminLayout: adminLayoutStub,
        },
      },
    })

    await flushPromises()
    await wrapper.get('[data-testid="quote-create-repair"]').trigger('click')
    await flushPromises()

    expect(apiMock.post).toHaveBeenCalledWith('/repairs', expect.objectContaining({
      client_id: 3,
      quote_id: 7,
      total_cost: 1200,
    }))
    expect(routerPush).toHaveBeenCalledWith('/admin/repairs/55')
  })
})
