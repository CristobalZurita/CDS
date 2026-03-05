import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const routerPush = vi.hoisted(() => vi.fn())
const routeState = vi.hoisted(() => ({ query: {} as Record<string, string> }))
const authStoreMock = vi.hoisted(() => ({
  login: vi.fn(),
  verifyTwoFactor: vi.fn(),
  error: '',
  isAdmin: false,
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeState,
  useRouter: () => ({ push: routerPush }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
}))

import LoginForm from '@/vue/components/auth/LoginForm.vue'

const turnstileStub = {
  template: '<button data-testid="turnstile-stub" @click="$emit(\'verify\', \'turnstile-token\')">captcha</button>',
}

function mountComponent() {
  return mount(LoginForm, {
    global: {
      stubs: {
        TurnstileWidget: turnstileStub,
      },
    },
  })
}

describe('LoginForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    routeState.query = {}
    authStoreMock.login.mockResolvedValue({})
    authStoreMock.verifyTwoFactor.mockResolvedValue({})
    authStoreMock.error = ''
    authStoreMock.isAdmin = false
  })

  it('requires captcha before submitting credentials', async () => {
    const wrapper = mountComponent()

    await wrapper.get('[data-testid="login-email"]').setValue('user@example.com')
    await wrapper.get('[data-testid="login-password"]').setValue('secret12')
    await wrapper.get('[data-testid="login-submit"]').trigger('submit')

    expect(authStoreMock.login).not.toHaveBeenCalled()
    expect(wrapper.get('[data-testid="login-error"]').text()).toContain('Captcha requerido')
  })

  it('logs in an admin user and redirects to admin dashboard', async () => {
    authStoreMock.isAdmin = true
    const wrapper = mountComponent()

    await wrapper.get('[data-testid="login-email"]').setValue('admin@example.com')
    await wrapper.get('[data-testid="login-password"]').setValue('admin12')
    await wrapper.get('[data-testid="turnstile-stub"]').trigger('click')
    await wrapper.get('[data-testid="login-submit"]').trigger('submit')
    await flushPromises()

    expect(authStoreMock.login).toHaveBeenCalledWith('admin@example.com', 'admin12', 'turnstile-token')
    expect(routerPush).toHaveBeenCalledWith('/admin')
  })

  it('completes the 2FA flow and honors redirect query', async () => {
    routeState.query = { redirect: '/admin/stats' }
    authStoreMock.login.mockResolvedValue({
      requires_2fa: true,
      challenge_id: 'challenge-123',
    })

    const wrapper = mountComponent()

    await wrapper.get('[data-testid="login-email"]').setValue('user@example.com')
    await wrapper.get('[data-testid="login-password"]').setValue('secret12')
    await wrapper.get('[data-testid="turnstile-stub"]').trigger('click')
    await wrapper.get('[data-testid="login-submit"]').trigger('submit')
    await flushPromises()

    const codeInput = wrapper.get('#twoFactor')
    await codeInput.setValue('123456')
    await wrapper.get('[data-testid="login-submit"]').trigger('submit')
    await flushPromises()

    expect(authStoreMock.verifyTwoFactor).toHaveBeenCalledWith('challenge-123', '123456')
    expect(routerPush).toHaveBeenCalledWith('/admin/stats')
  })

  it('surfaces auth store errors when login fails', async () => {
    authStoreMock.error = 'Credenciales inválidas'
    authStoreMock.login.mockRejectedValue(new Error('boom'))

    const wrapper = mountComponent()

    await wrapper.get('[data-testid="login-email"]').setValue('user@example.com')
    await wrapper.get('[data-testid="login-password"]').setValue('secret12')
    await wrapper.get('[data-testid="turnstile-stub"]').trigger('click')
    await wrapper.get('[data-testid="login-submit"]').trigger('submit')
    await flushPromises()

    expect(wrapper.get('[data-testid="login-error"]').text()).toContain('Credenciales inválidas')
  })
})
