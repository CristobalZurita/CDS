import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'

import HomeView from '@/views/HomeView.vue'

describe('HomeView', () => {
  it('renders base copy and home link', () => {
    const wrapper = mount(HomeView, {
      global: {
        stubs: {
          'router-link': {
            template: '<a><slot /></a>',
          },
        },
      },
    })

    expect(wrapper.text()).toContain('Cirujano de Sintetizadores')
    expect(wrapper.text()).toContain('contenedor base para vistas nuevas')
    expect(wrapper.text()).toContain('Ir al Inicio')
  })
})
