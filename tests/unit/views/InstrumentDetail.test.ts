import { defineComponent, nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'

import InstrumentDetail from '@/views/InstrumentDetail.vue'

const InstrumentCarouselStub = defineComponent({
  name: 'InstrumentCarousel',
  emits: ['photo-changed'],
  template: '<div data-testid="instrument-carousel-stub"></div>',
})

describe('InstrumentDetail view', () => {
  it('renders instrument info and reacts to carousel photo change events', async () => {
    vi.spyOn(console, 'log').mockImplementation(() => undefined)

    const wrapper = mount(InstrumentDetail, {
      props: {
        instrument: {
          id: 'juno',
          marca: 'Roland',
          modelo: 'Juno-106',
          foto_principal: 'principal.jpg',
          fotos_adicionales: ['a.jpg', 'b.jpg'],
          tipos: ['Synth'],
          agregado_en: '2026-03-01T12:00:00Z',
        },
      },
      global: {
        stubs: {
          InstrumentCarousel: InstrumentCarouselStub,
        },
      },
    })

    expect(wrapper.text()).toContain('Roland Juno-106')
    expect(wrapper.text()).toContain('Total de fotos:')
    expect(wrapper.text()).toContain('3')
    expect(wrapper.text()).toContain('Foto actual: principal.jpg')

    wrapper.getComponent(InstrumentCarouselStub).vm.$emit('photo-changed', 'b.jpg')
    await nextTick()

    expect(wrapper.text()).toContain('Foto actual: b.jpg')
  })
})
