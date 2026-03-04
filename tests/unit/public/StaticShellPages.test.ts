import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import CalculatorsPage from '@/vue/content/pages/CalculatorsPage.vue'
import HomePage from '@/vue/content/pages/HomePage.vue'
import LicensePage from '@/vue/content/pages/LicensePage.vue'
import PolicyPage from '@/vue/content/pages/PolicyPage.vue'

const PageWrapperStub = {
  props: ['id', 'noPadding', 'readable', 'sections'],
  template: `
    <div
      data-testid="page-wrapper"
      :data-id="id"
      :data-no-padding="String(noPadding)"
      :data-readable="String(Boolean(readable))"
    >
      <span
        v-for="section in sections"
        :key="section.id"
        class="page-section"
        :data-section-id="section.id"
        :data-section-name="section.name ?? ''"
        :data-section-icon="section.faIcon"
      />
    </div>
  `,
}

const mountPage = (component: object) =>
  mount(component, {
    global: {
      stubs: {
        PageWrapper: PageWrapperStub,
      },
    },
  })

const sectionIds = (wrapper: ReturnType<typeof mountPage>) =>
  wrapper.findAll('.page-section').map((node) => node.attributes('data-section-id'))

describe('public wrapper pages', () => {
  it('wires the home page sections in the expected order', () => {
    const wrapper = mountPage(HomePage)
    const pageWrapper = wrapper.get('[data-testid="page-wrapper"]')

    expect(pageWrapper.attributes('data-id')).toBe('foxy-home-page')
    expect(pageWrapper.attributes('data-no-padding')).toBe('true')
    expect(sectionIds(wrapper)).toEqual([
      'hero',
      'about',
      'services',
      'diagnostic',
      'featured',
      'faq',
      'reviews',
      'contact',
    ])
  })

  it('keeps the policy page mapped to the policy section', () => {
    const wrapper = mountPage(PolicyPage)
    const pageWrapper = wrapper.get('[data-testid="page-wrapper"]')

    expect(pageWrapper.attributes('data-id')).toBe('foxy-policy-page')
    expect(pageWrapper.attributes('data-no-padding')).toBe('false')
    expect(sectionIds(wrapper)).toEqual(['policy'])
  })

  it('keeps the license page mapped to the license section', () => {
    const wrapper = mountPage(LicensePage)

    expect(wrapper.get('[data-testid="page-wrapper"]').attributes('data-id')).toBe('foxy-license-page')
    expect(sectionIds(wrapper)).toEqual(['license'])
  })

  it('keeps the calculators page metadata on the existing section info object', () => {
    const wrapper = mountPage(CalculatorsPage)
    const section = wrapper.get('.page-section')

    expect(wrapper.get('[data-testid="page-wrapper"]').attributes('data-id')).toBe('foxy-calculators-page')
    expect(section.attributes('data-section-id')).toBe('calculators')
    expect(section.attributes('data-section-name')).toBe('Calculadoras')
    expect(section.attributes('data-section-icon')).toBe('pi pi-calculator')
  })
})
