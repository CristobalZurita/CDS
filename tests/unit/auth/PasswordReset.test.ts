import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const routeState = vi.hoisted(() => ({
  query: {} as Record<string, string>,
}))

const apiMock = vi.hoisted(() => ({
  post: vi.fn(),
}))

const toastMock = vi.hoisted(() => ({
  showSuccess: vi.fn(),
  showError: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeState,
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

vi.mock('@/services/toastService', () => toastMock)

import PasswordReset from '@/vue/components/auth/PasswordReset.vue'

describe('PasswordReset', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    routeState.query = {}
  })

  it('requests a reset token and switches to reset mode when the backend returns one', async () => {
    apiMock.post.mockResolvedValueOnce({
      data: {
        message: 'Correo enviado',
        reset_token: 'reset-token-123',
      },
    })

    const wrapper = mount(PasswordReset)
    await wrapper.get('[data-testid="password-reset-email"]').setValue('user@example.com')
    await wrapper.get('[data-testid="password-reset-request-submit"]').trigger('submit')
    await flushPromises()

    expect(apiMock.post).toHaveBeenCalledWith('/auth/forgot-password', { email: 'user@example.com' })
    expect(toastMock.showSuccess).toHaveBeenCalledWith('Correo enviado')
    expect(wrapper.get('[data-testid="password-reset-token"]').element).toBeTruthy()
  })

  it('shows validation error when passwords do not match', async () => {
    const wrapper = mount(PasswordReset)
    await wrapper.get('[data-testid="password-reset-mode-reset"]').trigger('click')
    await wrapper.get('[data-testid="password-reset-token"]').setValue('token')
    await wrapper.get('[data-testid="password-reset-new"]').setValue('clave1234')
    await wrapper.get('[data-testid="password-reset-confirm"]').setValue('otra1234')
    await wrapper.get('[data-testid="password-reset-confirm-submit"]').trigger('submit')

    expect(toastMock.showError).toHaveBeenCalledWith('Las contraseñas no coinciden')
    expect(apiMock.post).not.toHaveBeenCalled()
  })

  it('uses the token from query and submits the password reset confirmation', async () => {
    routeState.query = { token: 'query-token-xyz' }
    apiMock.post.mockResolvedValueOnce({
      data: {
        message: 'Contraseña actualizada',
      },
    })

    const wrapper = mount(PasswordReset)
    await flushPromises()

    await wrapper.get('[data-testid="password-reset-new"]').setValue('clave1234')
    await wrapper.get('[data-testid="password-reset-confirm"]').setValue('clave1234')
    await wrapper.get('[data-testid="password-reset-confirm-submit"]').trigger('submit')
    await flushPromises()

    expect(apiMock.post).toHaveBeenCalledWith('/auth/reset-password', {
      token: 'query-token-xyz',
      new_password: 'clave1234',
    })
    expect(toastMock.showSuccess).toHaveBeenCalledWith('Contraseña actualizada')
  })
})
