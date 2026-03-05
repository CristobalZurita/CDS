import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const routerPush = vi.hoisted(() => vi.fn())
const authStoreMock = vi.hoisted(() => ({
  register: vi.fn(),
  error: '',
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: routerPush,
  }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
}))

import RegisterForm from '@/vue/components/auth/RegisterForm.vue'
import RegisterPage from '@/vue/content/pages/RegisterPage.vue'
import PasswordResetPage from '@/vue/content/pages/PasswordResetPage.vue'
import AccountDelete from '@/vue/components/auth/AccountDelete.vue'

const sharedStubs = {
  TurnstileWidget: {
    template: '<button data-testid="turnstile-stub" @click="$emit(\'verify\', \'captcha-token\')">captcha</button>',
  },
  RouterLink: {
    template: '<a><slot /></a>',
  },
}

describe('register and password pages', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    authStoreMock.error = ''
    authStoreMock.register.mockResolvedValue({ ok: true })
  })

  it('validates captcha and toggles password in RegisterForm', async () => {
    const wrapper = mount(RegisterForm, {
      global: {
        stubs: sharedStubs,
      },
    })

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('registro@test.cl')
    await inputs[1].setValue('usuario_test')
    await inputs[2].setValue('Usuario Test')
    await inputs[3].setValue('912345678')
    await inputs[4].setValue('password123')

    expect(inputs[4].attributes('type')).toBe('password')
    await wrapper.get('.toggle-password').trigger('click')
    expect(wrapper.findAll('input')[4].attributes('type')).toBe('text')

    await wrapper.find('form').trigger('submit')
    expect(authStoreMock.register).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('Captcha requerido')
  })

  it('submits RegisterForm and redirects to login', async () => {
    const wrapper = mount(RegisterForm, {
      global: {
        stubs: sharedStubs,
      },
    })

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('ok@test.cl')
    await inputs[1].setValue('ok_user')
    await inputs[2].setValue('OK User')
    await inputs[4].setValue('password123')
    await wrapper.get('[data-testid="turnstile-stub"]').trigger('click')

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(authStoreMock.register).toHaveBeenCalledWith(
      expect.objectContaining({
        email: 'ok@test.cl',
        username: 'ok_user',
        full_name: 'OK User',
        password: 'password123',
        turnstile_token: 'captcha-token',
      })
    )
    expect(routerPush).toHaveBeenCalledWith('/login')
  })

  it('shows auth errors in RegisterForm when register fails', async () => {
    authStoreMock.error = 'El usuario ya existe'
    authStoreMock.register.mockRejectedValue(new Error('register failed'))

    const wrapper = mount(RegisterForm, {
      global: {
        stubs: sharedStubs,
      },
    })

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('error@test.cl')
    await inputs[1].setValue('error_user')
    await inputs[2].setValue('Error User')
    await inputs[4].setValue('password123')
    await wrapper.get('[data-testid="turnstile-stub"]').trigger('click')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('El usuario ya existe')
  })

  it('registers from RegisterPage wrapper and keeps page shell visible', async () => {
    const wrapper = mount(RegisterPage, {
      global: {
        stubs: sharedStubs,
      },
    })

    expect(wrapper.text()).toContain('Crear cuenta')

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('page@test.cl')
    await inputs[1].setValue('page_user')
    await inputs[2].setValue('Page User')
    await inputs[4].setValue('password123')
    await wrapper.get('[data-testid="turnstile-stub"]').trigger('click')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(authStoreMock.register).toHaveBeenCalledWith(
      expect.objectContaining({
        email: 'page@test.cl',
        username: 'page_user',
        full_name: 'Page User',
      })
    )
    expect(routerPush).toHaveBeenCalledWith('/login')
  })

  it('renders PasswordResetPage shell and account delete emit', async () => {
    const resetWrapper = mount(PasswordResetPage, {
      global: {
        stubs: {
          ...sharedStubs,
          PasswordReset: {
            template: '<div data-testid="password-reset-stub">password-reset</div>',
          },
        },
      },
    })

    expect(resetWrapper.text()).toContain('Recuperar contraseña')
    expect(resetWrapper.find('[data-testid="password-reset-stub"]').exists()).toBe(true)

    const deleteWrapper = mount(AccountDelete)
    await deleteWrapper.get('button').trigger('click')
    expect(deleteWrapper.emitted('confirm')).toBeTruthy()
  })
})
