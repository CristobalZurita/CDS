import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const routeState = vi.hoisted(() => ({ query: {} }))
const routerReplace = vi.hoisted(() => vi.fn())
const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeState,
  useRouter: () => ({
    replace: routerReplace,
  }),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

import ClientsPage from '@/vue/content/pages/admin/ClientsPage.vue'
import PurchaseRequestsPage from '@/vue/content/pages/admin/PurchaseRequestsPage.vue'

const stubs = {
  AdminLayout: {
    props: ['title', 'context'],
    template: `
      <section>
        <h1 data-testid="layout-title">{{ title }}</h1>
        <div data-testid="layout-context">{{ context?.clientName || '' }}</div>
        <slot />
      </section>
    `,
  },
  ClientList: {
    props: ['clients'],
    template: `
      <div data-testid="client-list-stub">
        <span data-testid="client-list-count">{{ clients.length }}</span>
        <button
          data-testid="client-list-select"
          @click="$emit('select', clients[0])"
        >
          select
        </button>
      </div>
    `,
  },
  ClientDetail: {
    props: ['client'],
    template: '<div data-testid="client-detail-stub">{{ client?.name || "sin-cliente" }}</div>',
  },
  UnifiedIntakeForm: {
    template: '<button data-testid="intake-complete" @click="$emit(\'completed\', { client_id: 1 })">complete</button>',
  },
  WizardPurchaseRequest: {
    template: '<button data-testid="purchase-wizard-complete" @click="$emit(\'completed\')">complete</button>',
  },
}

describe('admin clients and purchase pages', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    routeState.query = {}
  })

  it('loads clients, applies route selection, filters, selects and completes intake', async () => {
    routeState.query = { client_id: '2' }
    apiMock.get.mockResolvedValue({
      data: [
        { id: 1, name: 'Ana', email: 'ana@test.com', phone: '111', client_code: 'C-001' },
        { id: 2, name: 'Bruno', email: 'bruno@test.com', phone: '222', client_code: 'C-002' },
      ],
    })

    const wrapper = mount(ClientsPage, {
      global: { stubs },
    })
    await flushPromises()

    expect(apiMock.get).toHaveBeenCalledWith('/clients')
    expect(wrapper.get('[data-testid="client-detail-stub"]').text()).toContain('Bruno')
    expect(wrapper.get('[data-testid="layout-context"]').text()).toContain('Bruno')

    await wrapper.get('[data-testid="clients-search"]').setValue('ana')
    expect(wrapper.get('[data-testid="client-list-count"]').text()).toBe('1')

    await wrapper.get('[data-testid="client-list-select"]').trigger('click')
    expect(wrapper.get('[data-testid="client-detail-stub"]').text()).toContain('Ana')

    await wrapper.get('[data-testid="clients-intake-toggle"]').trigger('click')
    expect(wrapper.find('[data-testid="clients-intake"]').exists()).toBe(false)

    await wrapper.get('[data-testid="clients-intake-toggle"]').trigger('click')
    expect(wrapper.find('[data-testid="clients-intake"]').exists()).toBe(true)

    await wrapper.get('[data-testid="intake-complete"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-testid="clients-intake"]').exists()).toBe(false)
    expect(apiMock.get).toHaveBeenCalledTimes(2)
  })

  it('loads purchase requests with OT filter and executes payment/status/delete flows', async () => {
    routeState.query = { repair_id: '12' }
    apiMock.get.mockResolvedValue({
      data: {
        requests: [
          {
            id: 55,
            client_name: 'Cliente 55',
            repair_code: 'OT-55',
            status: 'draft',
            items_count: 2,
            total_items_amount: 10000,
            requested_amount: 12000,
            items: [{ id: 1 }, { id: 2 }],
            latest_payment: null,
          },
        ],
      },
    })
    apiMock.post.mockResolvedValue({ data: { ok: true } })
    apiMock.patch.mockResolvedValue({ data: { ok: true } })
    apiMock.delete.mockResolvedValue({ data: { ok: true } })
    vi.spyOn(window, 'confirm').mockReturnValue(true)

    const wrapper = mount(PurchaseRequestsPage, {
      global: { stubs },
    })
    await flushPromises()

    expect(apiMock.get).toHaveBeenCalledWith('/purchase-requests/board', {
      params: { repair_id: 12 },
    })
    expect(wrapper.findAll('[data-testid="purchase-request-row"]')).toHaveLength(1)

    await wrapper.get('[data-testid="purchase-request-request-payment"]').trigger('click')
    await flushPromises()
    expect(apiMock.post).toHaveBeenCalledWith(
      '/purchase-requests/55/request-payment',
      expect.objectContaining({
        amount: 12000,
      })
    )

    await wrapper.get('[data-testid="purchase-request-confirm-payment"]').trigger('click')
    await flushPromises()
    expect(apiMock.post).toHaveBeenCalledWith(
      '/purchase-requests/55/confirm-payment',
      expect.objectContaining({
        admin_notes: 'Pago validado por administración',
      })
    )

    await wrapper.get('[data-testid="purchase-request-status-select"]').setValue('approved')
    await flushPromises()
    expect(apiMock.patch).toHaveBeenCalledWith('/purchase-requests/55', { status: 'approved' })

    await wrapper.get('[data-testid="purchase-request-delete"]').trigger('click')
    await flushPromises()
    expect(apiMock.delete).toHaveBeenCalledWith('/purchase-requests/55')

    await wrapper.get('[data-testid="purchase-requests-clear-filter"]').trigger('click')
    expect(routerReplace).toHaveBeenCalledWith({
      name: 'admin-purchase-requests',
      query: {},
    })
  })
})
