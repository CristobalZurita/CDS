import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const routerPush = vi.hoisted(() => vi.fn())
const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
}))
const apiComposableMock = vi.hoisted(() => ({
  get: vi.fn(),
}))
const toastMock = vi.hoisted(() => ({
  showSuccess: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: routerPush,
  }),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

vi.mock('@/composables/useApi.js', () => ({
  useApi: () => apiComposableMock,
}))

vi.mock('@/services/toastService', () => toastMock)

import ArchivePage from '@/vue/content/pages/admin/ArchivePage.vue'
import CategoriesPage from '@/vue/content/pages/admin/CategoriesPage.vue'
import ContactMessagesPage from '@/vue/content/pages/admin/ContactMessagesPage.vue'
import NewsletterSubscriptionsPage from '@/vue/content/pages/admin/NewsletterSubscriptionsPage.vue'
import TicketsPage from '@/vue/content/pages/admin/TicketsPage.vue'
import WizardsPage from '@/vue/content/pages/admin/WizardsPage.vue'

const stubs = {
  AdminLayout: {
    props: ['title', 'subtitle'],
    template: `
      <section class="admin-layout-stub">
        <h1 data-testid="layout-title">{{ title }}</h1>
        <p data-testid="layout-subtitle">{{ subtitle }}</p>
        <slot />
      </section>
    `,
  },
  CategoryForm: {
    props: ['category'],
    template: `
      <div data-testid="category-form-stub">
        <span data-testid="category-form-id">{{ category?.id ?? 'new' }}</span>
        <button data-testid="category-form-saved" @click="$emit('saved')">saved</button>
      </div>
    `,
  },
  CategoryList: {
    template: `
      <div data-testid="category-list-stub">
        <button data-testid="category-edit" @click="$emit('edit', { id: 7, name: 'Filtros' })">edit</button>
      </div>
    `,
  },
  WizardTicket: {
    template: `
      <div data-testid="wizard-ticket-stub">
        <button data-testid="wizard-ticket-complete" @click="$emit('completed', { ticket_id: 50 })">complete</button>
      </div>
    `,
  },
  WizardClientIntake: {
    template: '<button data-testid="wizard-client-intake" @click="$emit(\'completed\', { client_id: 2, device_id: 9 })">client</button>',
  },
  WizardInventoryItem: {
    template: '<button data-testid="wizard-inventory-item" @click="$emit(\'completed\')">inventory</button>',
  },
  WizardMaterialsUsage: {
    template: '<div data-testid="wizard-materials-usage" />',
  },
  WizardPurchaseRequest: {
    template: '<button data-testid="wizard-purchase-request" @click="$emit(\'completed\', { repair_id: 88 })">purchase</button>',
  },
  WizardManualUpload: {
    template: '<button data-testid="wizard-manual-upload" @click="$emit(\'completed\')">manual</button>',
  },
  WizardSignatureRequest: {
    template: '<button data-testid="wizard-signature-request" @click="$emit(\'completed\')">signature</button>',
  },
}

describe('admin secondary pages', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads archive entries, filters, reactivates and opens repair detail', async () => {
    apiMock.get.mockResolvedValue({
      data: [
        {
          id: 1,
          repair_code: 'OT-001',
          client_name: 'Ana Test',
          device_model: 'Juno 106',
          status: 'archivado',
          archived_at: '2026-03-04T10:00:00Z',
        },
      ],
    })
    apiMock.post.mockResolvedValue({ data: { ok: true } })
    vi.spyOn(window, 'confirm').mockReturnValue(true)

    const wrapper = mount(ArchivePage, {
      global: { stubs },
    })
    await flushPromises()

    expect(apiMock.get).toHaveBeenCalledWith('/repairs/archived')
    expect(wrapper.text()).toContain('Ana Test')

    await wrapper.get('[data-testid="archive-search"]').setValue('no-existe')
    expect(wrapper.text()).toContain('Sin OT archivadas.')

    await wrapper.get('[data-testid="archive-search"]').setValue('')
    await wrapper.findAll('button').find((button) => button.text() === 'Reactivar')!.trigger('click')
    await flushPromises()

    expect(apiMock.post).toHaveBeenCalledWith('/repairs/1/reactivate')
    expect(apiMock.get).toHaveBeenCalledTimes(2)

    await wrapper.findAll('button').find((button) => button.text() === 'Ver')!.trigger('click')
    expect(routerPush).toHaveBeenCalledWith('/admin/repairs/1')
  })

  it('toggles category form and handles edit/saved flows', async () => {
    const wrapper = mount(CategoriesPage, {
      global: { stubs },
    })

    expect(wrapper.find('[data-testid="category-form-stub"]').exists()).toBe(false)

    await wrapper.get('[data-testid="categories-new"]').trigger('click')
    expect(wrapper.text()).toContain('Crear categoría')
    expect(wrapper.get('[data-testid="category-form-id"]').text()).toBe('new')

    await wrapper.get('[data-testid="categories-new"]').trigger('click')
    expect(wrapper.find('[data-testid="category-form-stub"]').exists()).toBe(false)

    await wrapper.get('[data-testid="category-edit"]').trigger('click')
    expect(wrapper.text()).toContain('Editar categoría')
    expect(wrapper.get('[data-testid="category-form-id"]').text()).toBe('7')

    await wrapper.get('[data-testid="category-form-saved"]').trigger('click')
    expect(wrapper.find('[data-testid="category-form-stub"]').exists()).toBe(false)
  })

  it('renders contact messages and newsletter subscriptions from API composable', async () => {
    apiComposableMock.get
      .mockResolvedValueOnce([
        {
          id: 10,
          name: 'Cliente Uno',
          email: 'cliente@uno.cl',
          subject: 'Consulta OT',
          message: 'Necesito estado',
          created_at: '2026-03-05T09:00:00Z',
        },
      ])
      .mockResolvedValueOnce([
        {
          id: 99,
          email: 'mail@news.cl',
          is_active: true,
          source_url: '/home',
          created_at: '2026-03-05T09:30:00Z',
        },
      ])

    const contact = mount(ContactMessagesPage, {
      global: { stubs },
    })
    await flushPromises()
    expect(apiComposableMock.get).toHaveBeenCalledWith('/contact/messages')
    expect(contact.get('[data-testid="contact-table"]').text()).toContain('Cliente Uno')

    const newsletter = mount(NewsletterSubscriptionsPage, {
      global: { stubs },
    })
    await flushPromises()
    expect(apiComposableMock.get).toHaveBeenCalledWith('/newsletter/subscriptions')
    expect(newsletter.get('[data-testid="newsletter-table"]').text()).toContain('Activa')
  })

  it('updates ticket status, deletes tickets and handles wizard completion', async () => {
    apiMock.get.mockResolvedValue({
      data: [
        {
          id: 5,
          subject: 'Ruido en salida',
          status: 'open',
          priority: 'high',
          messages: [{ id: 1 }, { id: 2 }],
        },
      ],
    })
    apiMock.patch.mockResolvedValue({ data: { ok: true } })
    apiMock.delete.mockResolvedValue({ data: { ok: true } })
    vi.spyOn(window, 'confirm').mockReturnValue(true)

    const wrapper = mount(TicketsPage, {
      global: { stubs },
    })
    await flushPromises()

    expect(apiMock.get).toHaveBeenCalledWith('/tickets/')
    expect(wrapper.get('[data-testid="ticket-message-count"]').text()).toBe('2')

    await wrapper.get('[data-testid="ticket-status-select"]').setValue('closed')
    await flushPromises()
    expect(apiMock.patch).toHaveBeenCalledWith('/tickets/5?status=closed')

    await wrapper.get('[data-testid="ticket-delete"]').trigger('click')
    await flushPromises()
    expect(apiMock.delete).toHaveBeenCalledWith('/tickets/5')

    await wrapper.get('[data-testid="tickets-new"]').trigger('click')
    expect(wrapper.find('[data-testid="tickets-wizard"]').exists()).toBe(true)
    await wrapper.get('[data-testid="wizard-ticket-complete"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-testid="tickets-wizard"]').exists()).toBe(false)
  })

  it('shows completion toast variants in WizardsPage', async () => {
    const wrapper = mount(WizardsPage, {
      global: { stubs },
    })

    await wrapper.get('[data-testid="wizard-purchase-request"]').trigger('click')
    expect(toastMock.showSuccess).toHaveBeenLastCalledWith('Wizard completado. OT 88 creada correctamente.')

    await wrapper.get('[data-testid="wizard-client-intake"]').trigger('click')
    expect(toastMock.showSuccess).toHaveBeenLastCalledWith('Wizard completado. Cliente e instrumento registrados.')

    await wrapper.get('[data-testid="wizard-manual-upload"]').trigger('click')
    expect(toastMock.showSuccess).toHaveBeenLastCalledWith('Wizard completado correctamente.')
  })
})
