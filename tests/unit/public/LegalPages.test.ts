import { mount } from '@vue/test-utils'
import { describe, beforeEach, expect, it, vi } from 'vitest'

const pushMock = vi.hoisted(() => vi.fn())

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: pushMock,
  }),
}))

import PrivacyPage from '@/vue/content/pages/PrivacyPage.vue'
import TermsPage from '@/vue/content/pages/TermsPage.vue'

const RouterLinkStub = {
  props: ['to'],
  template: '<a :data-to="to"><slot /></a>',
}

describe('legal public pages', () => {
  beforeEach(() => {
    pushMock.mockReset()
  })

  it('requires acceptance before moving from terms to privacy', async () => {
    const wrapper = mount(TermsPage, {
      global: {
        stubs: {
          'router-link': RouterLinkStub,
        },
      },
    })

    const button = wrapper.get('button.btn-next')
    expect(wrapper.text()).toContain('Términos y Condiciones')
    expect(button.attributes('disabled')).toBeDefined()

    await button.trigger('click')
    expect(pushMock).not.toHaveBeenCalled()

    await wrapper.get('input.checkbox-input').setValue(true)
    expect(button.attributes('disabled')).toBeUndefined()

    await button.trigger('click')
    expect(pushMock).toHaveBeenCalledWith('/privacidad')
  })

  it('renders the privacy page links that already exist in the template', () => {
    const wrapper = mount(PrivacyPage, {
      global: {
        stubs: {
          'router-link': RouterLinkStub,
        },
      },
    })

    const links = wrapper.findAll('a[data-to]')

    expect(wrapper.text()).toContain('Política de Privacidad')
    expect(links).toHaveLength(2)
    expect(links[0].attributes('data-to')).toBe('/terminos')
    expect(links[1].attributes('data-to')).toBe('/')
  })
})
