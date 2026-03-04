import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import WorkshopFooter from '@/vue/components/footer/WorkshopFooter.vue'

describe('WorkshopFooter', () => {
  it('renders the shared workshop footer content and legal links', () => {
    const wrapper = mount(WorkshopFooter, {
      global: {
        stubs: {
          SocialLinks: {
            template: '<div data-testid="social-links-stub" />',
          },
        },
      },
    })

    expect(wrapper.text()).toContain('Sobre el taller')
    expect(wrapper.text()).toContain('Redes y presencia')
    expect(wrapper.text()).toContain('Información de contacto')
    expect(wrapper.text()).toContain('Repositorio del proyecto')
    expect(wrapper.text()).toContain('Todos los derechos reservados')
    expect(wrapper.find('[data-testid="social-links-stub"]').exists()).toBe(true)

    const links = wrapper.findAll('a')
    expect(links.some((link) => link.attributes('href') === 'tel:+56982957538')).toBe(true)
    expect(links.some((link) => link.attributes('href') === 'mailto:contacto@cirujanodesintetizadores.com')).toBe(true)
    expect(links.some((link) => link.attributes('href') === 'https://github.com/CristobalZurita/cirujano-front')).toBe(true)
    expect(wrapper.html()).toContain('/privacidad')
    expect(wrapper.html()).toContain('/terminos')
  })
})
