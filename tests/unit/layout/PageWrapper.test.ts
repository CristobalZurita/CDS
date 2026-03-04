import { mount } from '@vue/test-utils'
import { markRaw, shallowRef } from 'vue'
import { describe, expect, it } from 'vitest'

import SectionInfo from '@/models/SectionInfo.js'
import PageWrapper from '@/vue/components/layout/PageWrapper.vue'

const AlphaSection = {
  template: '<section data-testid="section-alpha">Alpha</section>',
}

const BetaSection = {
  template: '<section data-testid="section-beta">Beta</section>',
}

describe('PageWrapper', () => {
  it('renders the provided sections and updates the injected section registry', () => {
    const currentPageSections = shallowRef([])
    const sections = [
      new SectionInfo('alpha', markRaw(AlphaSection), 'Alpha', 'pi pi-star'),
      new SectionInfo('beta', markRaw(BetaSection), 'Beta', 'pi pi-bolt'),
    ]

    const wrapper = mount(PageWrapper, {
      props: {
        id: 'test-page-wrapper',
        noPadding: true,
        readable: true,
        sections,
      },
      global: {
        provide: {
          currentPageSections,
        },
      },
    })

    expect(wrapper.attributes('id')).toBe('test-page-wrapper')
    expect(wrapper.classes()).toContain('foxy-page-wrapper-no-padding')
    expect(wrapper.find('.foxy-page-inner').classes()).toContain('readable')
    expect(wrapper.find('[data-testid="section-alpha"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="section-beta"]').exists()).toBe(true)
    expect(currentPageSections.value).toStrictEqual(sections)
  })
})
