import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  put: vi.fn(),
}))

const toastMock = vi.hoisted(() => ({
  showSuccess: vi.fn(),
  showError: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

vi.mock('@/services/toastService', () => toastMock)

import ProfilePage from '@/vue/content/pages/ProfilePage.vue'

const baseProfile = {
  data: {
    email: 'client@example.com',
    full_name: 'Cliente Demo',
    phone: '+56911111111',
    address: 'Av. Original 123',
    member_since: '2025-01-10T00:00:00Z',
    stats: {
      total_repairs: 4,
      total_spent: 125000,
    },
  },
}

describe('ProfilePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.get.mockResolvedValue(baseProfile)
    apiMock.put.mockResolvedValue({
      data: {
        ...baseProfile.data,
        phone: '+56922222222',
        address: 'Nueva Dirección 456',
      },
    })
  })

  it('loads profile data and saves profile edits', async () => {
    const wrapper = mount(ProfilePage)
    await flushPromises()

    expect(apiMock.get).toHaveBeenCalledWith('/client/profile')
    expect(wrapper.text()).toContain('Cliente Demo')
    expect(wrapper.text()).toContain('Av. Original 123')

    await wrapper.get('[data-testid="profile-edit-toggle"]').trigger('click')
    await wrapper.get('[data-testid="profile-phone-input"]').setValue('+56922222222')
    await wrapper.get('[data-testid="profile-address-input"]').setValue('Nueva Dirección 456')
    await wrapper.get('[data-testid="profile-save"]').trigger('click')
    await flushPromises()

    expect(apiMock.put).toHaveBeenCalledWith('/client/profile', {
      email: 'client@example.com',
      full_name: 'Cliente Demo',
      phone: '+56922222222',
      address: 'Nueva Dirección 456',
    })
    expect(toastMock.showSuccess).toHaveBeenCalledWith('Perfil actualizado exitosamente')
    expect(wrapper.text()).toContain('Nueva Dirección 456')
  })

  it('handles preference save, password change and account delete actions', async () => {
    const wrapper = mount(ProfilePage)
    await flushPromises()

    await wrapper.get('[data-testid="profile-preferences-save"]').trigger('click')
    expect(toastMock.showSuccess).toHaveBeenCalledWith('Preferencias guardadas')

    await wrapper.get('[data-testid="profile-open-password-modal"]').trigger('click')
    await wrapper.get('[data-testid="profile-password-current"]').setValue('actual')
    await wrapper.get('[data-testid="profile-password-new"]').setValue('nueva123')
    await wrapper.get('[data-testid="profile-password-confirm"]').setValue('otra123')
    await wrapper.get('[data-testid="profile-password-save"]').trigger('click')
    expect(toastMock.showError).toHaveBeenCalledWith('Las contraseñas no coinciden')

    await wrapper.get('[data-testid="profile-password-confirm"]').setValue('nueva123')
    await wrapper.get('[data-testid="profile-password-save"]').trigger('click')
    expect(toastMock.showSuccess).toHaveBeenCalledWith('Contraseña cambiada exitosamente')

    await wrapper.get('[data-testid="profile-open-delete-modal"]').trigger('click')
    await wrapper.get('[data-testid="profile-delete-confirm"]').trigger('click')
    expect(toastMock.showSuccess).toHaveBeenCalledWith('Cuenta eliminada (demo)')
  })
})
