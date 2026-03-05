import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const routerPush = vi.hoisted(() => vi.fn())
const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
}))
const toastMock = vi.hoisted(() => ({
  showError: vi.fn(),
}))
const authStoreMock = vi.hoisted(() => ({
  user: { full_name: 'Cliente Premium' },
  logout: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: routerPush }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

vi.mock('@/services/toastService', () => toastMock)

import DashboardPage from '@/vue/content/pages/DashboardPage.vue'

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.get.mockResolvedValue({
      data: {
        stats: {
          pending_repairs: 1,
          active_repairs: 2,
          completed_repairs: 5,
          total_spent: 345000,
          pending_ot_payments: 1,
        },
        active_repairs: [
          {
            id: 21,
            instrument: 'Moog One',
            repair_code: 'CDS-021-OT-021',
            status: 'en_trabajo',
            fault: 'Pantalla inestable',
            date_in: '2026-02-03T00:00:00Z',
            progress: 70,
          },
        ],
        notifications: [
          {
            id: 1,
            type: 'warning',
            message: 'Falta validar un repuesto',
            date: new Date().toISOString(),
          },
        ],
      },
    })
  })

  it('loads dashboard data, dismisses notifications and navigates to repair details', async () => {
    const wrapper = mount(DashboardPage)
    await flushPromises()

    expect(apiMock.get).toHaveBeenCalledWith('/client/dashboard')
    expect(wrapper.text()).toContain('Bienvenido Cliente')
    expect(wrapper.text()).toContain('$345000')
    expect(wrapper.findAll('[data-testid="dashboard-repair-card"]')).toHaveLength(1)
    expect(wrapper.findAll('[data-testid="dashboard-notification"]')).toHaveLength(1)

    await wrapper.get('[data-testid="dashboard-repair-view"]').trigger('click')
    expect(routerPush).toHaveBeenCalledWith('/repairs/21')

    await wrapper.get('[data-testid="dashboard-notification-dismiss"]').trigger('click')
    expect(wrapper.get('[data-testid="dashboard-empty-notifications"]').text()).toContain('No hay notificaciones nuevas')

    await wrapper.get('[data-testid="dashboard-logout"]').trigger('click')
    expect(authStoreMock.logout).toHaveBeenCalledTimes(1)
  })

  it('renders empty states and shows a toast on dashboard load failures', async () => {
    apiMock.get.mockResolvedValueOnce({
      data: {
        stats: {
          pending_repairs: 0,
          active_repairs: 0,
          completed_repairs: 0,
          total_spent: 0,
          pending_ot_payments: 0,
        },
        active_repairs: [],
        notifications: [],
      },
    })

    const wrapper = mount(DashboardPage)
    await flushPromises()

    expect(wrapper.get('[data-testid="dashboard-empty-repairs"]').text()).toContain('No tienes reparaciones activas')
    expect(wrapper.get('[data-testid="dashboard-empty-notifications"]').text()).toContain('No hay notificaciones nuevas')

    apiMock.get.mockRejectedValueOnce({
      response: { data: { detail: 'Dashboard fuera de servicio' } },
    })

    mount(DashboardPage)
    await flushPromises()

    expect(toastMock.showError).toHaveBeenCalledWith('Dashboard fuera de servicio')
  })
})
