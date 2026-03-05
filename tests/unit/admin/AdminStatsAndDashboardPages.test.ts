import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

import StatsPage from '@/vue/content/pages/admin/StatsPage.vue'
import AdminDashboard from '@/vue/content/pages/admin/AdminDashboard.vue'
import RepairsAdminPage from '@/vue/content/pages/admin/RepairsAdminPage.vue'

const stubs = {
  AdminLayout: {
    props: ['title'],
    template: '<section><h1 data-testid="layout-title">{{ title }}</h1><slot /></section>',
  },
  StatsCards: {
    props: ['stats'],
    template: '<div data-testid="stats-cards">{{ JSON.stringify(stats) }}</div>',
  },
  KpiZones: {
    props: ['summary', 'dashboard', 'revenue', 'inventory', 'clients', 'warranty'],
    template: `
      <div data-testid="kpi-zones">
        {{ JSON.stringify(summary) }}
        {{ JSON.stringify(dashboard) }}
        {{ JSON.stringify(revenue) }}
        {{ JSON.stringify(inventory) }}
        {{ JSON.stringify(clients) }}
        {{ JSON.stringify(warranty) }}
      </div>
    `,
  },
  RepairsList: {
    template: '<div data-testid="repairs-list-stub" />',
  },
  UserList: {
    template: '<button data-testid="user-edit" @click="$emit(\'edit\', { id: 3, name: \'Admin 3\' })">edit</button>',
  },
  UserForm: {
    props: ['user'],
    template: `
      <div data-testid="user-form-stub">
        <span data-testid="user-form-id">{{ user?.id ?? 'new' }}</span>
        <button data-testid="user-form-saved" @click="$emit('saved')">save</button>
      </div>
    `,
  },
  RepairForm: {
    template: '<button data-testid="repair-form-saved" @click="$emit(\'saved\')">save</button>',
  },
}

describe('admin stats/dashboard pages', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads StatsPage datasets using safe fallback mapping', async () => {
    apiMock.get.mockImplementation(async (url: string) => ({ data: { route: url } }))

    const wrapper = mount(StatsPage, {
      global: { stubs },
    })
    await flushPromises()

    expect(apiMock.get).toHaveBeenCalledTimes(7)
    expect(apiMock.get).toHaveBeenCalledWith('/stats', { params: { extended: true } })
    expect(wrapper.get('[data-testid="stats-cards"]').text()).toContain('/stats')
    expect(wrapper.get('[data-testid="kpi-zones"]').text()).toContain('/analytics/warranties')
  })

  it('loads AdminDashboard metrics and handles user form flows', async () => {
    apiMock.get.mockImplementation(async (url: string) => ({ data: { source: url } }))

    const wrapper = mount(AdminDashboard, {
      global: { stubs },
    })
    await flushPromises()

    expect(apiMock.get).toHaveBeenCalledTimes(7)
    expect(wrapper.get('[data-testid="stats-cards"]').text()).toContain('/stats')
    expect(wrapper.find('[data-testid="user-form-stub"]').exists()).toBe(false)

    await wrapper.get('[data-testid="users-new"]').trigger('click')
    expect(wrapper.get('[data-testid="user-form-id"]').text()).toBe('new')

    await wrapper.get('[data-testid="user-form-saved"]').trigger('click')
    expect(wrapper.find('[data-testid="user-form-stub"]').exists()).toBe(false)

    await wrapper.get('[data-testid="user-edit"]').trigger('click')
    expect(wrapper.get('[data-testid="user-form-id"]').text()).toBe('3')
  })

  it('toggles RepairsAdminPage creation form and closes on save', async () => {
    const wrapper = mount(RepairsAdminPage, {
      global: { stubs },
    })

    expect(wrapper.find('[data-testid="repair-form-saved"]').exists()).toBe(false)

    await wrapper.get('[data-testid="repairs-new"]').trigger('click')
    expect(wrapper.find('[data-testid="repair-form-saved"]').exists()).toBe(true)

    await wrapper.get('[data-testid="repair-form-saved"]').trigger('click')
    expect(wrapper.find('[data-testid="repair-form-saved"]').exists()).toBe(false)
  })
})
