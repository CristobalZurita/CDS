import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

import AppointmentsPage from '@/vue/content/pages/admin/AppointmentsPage.vue'

const adminLayoutStub = {
  template: '<div><slot /></div>',
}

const appointments = [
  {
    id: 1,
    nombre: 'Cita Uno',
    email: 'uno@example.com',
    telefono: '+56911111111',
    fecha: '2030-01-01T12:00:00',
    mensaje: 'Primera',
    estado: 'pendiente',
  },
  {
    id: 2,
    nombre: 'Cita Dos',
    email: 'dos@example.com',
    telefono: '+56922222222',
    fecha: '2030-01-02T12:00:00',
    mensaje: 'Segunda',
    estado: 'confirmado',
  },
]

describe('AppointmentsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.get.mockResolvedValue({ data: appointments })
    apiMock.patch.mockResolvedValue({})
    apiMock.delete.mockResolvedValue({})
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    vi.spyOn(window, 'alert').mockImplementation(() => {})
  })

  it('loads, filters and updates appointments', async () => {
    const wrapper = mount(AppointmentsPage, {
      global: {
        stubs: {
          AdminLayout: adminLayoutStub,
        },
      },
    })

    await flushPromises()
    expect(wrapper.findAll('[data-testid="appointment-row"]')).toHaveLength(2)

    await wrapper.get('[data-testid="appointments-filter-pending"]').trigger('click')
    expect(wrapper.findAll('[data-testid="appointment-row"]')).toHaveLength(1)

    await wrapper.get('[data-testid="appointment-confirm"]').trigger('click')
    await flushPromises()

    expect(apiMock.patch).toHaveBeenCalledWith('/appointments/1', { estado: 'confirmado' })
  })

  it('deletes an appointment after confirmation', async () => {
    const wrapper = mount(AppointmentsPage, {
      global: {
        stubs: {
          AdminLayout: adminLayoutStub,
        },
      },
    })

    await flushPromises()
    await wrapper.get('[data-testid="appointment-delete"]').trigger('click')
    await flushPromises()

    expect(apiMock.delete).toHaveBeenCalledWith('/appointments/1')
  })
})
