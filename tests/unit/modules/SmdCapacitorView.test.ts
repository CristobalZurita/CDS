import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'

import SmdCapacitorView from '@/modules/smdCapacitor/SmdCapacitorView.vue'

const stubs = {
  PageSection: { template: '<section v-bind="$attrs"><slot /></section>' },
  PageSectionHeader: {
    props: ['title', 'subtitle'],
    template: '<header><h1>{{ title }}</h1><p>{{ subtitle }}</p></header>',
  },
  PageSectionContent: { template: '<div><slot /></div>' },
  Link: { props: ['url'], template: '<a :href="url"><slot /></a>' },
  WorkshopFooter: { template: '<footer />' },
}

function mountView() {
  return mount(SmdCapacitorView, {
    global: {
      stubs,
    },
  })
}

describe('SmdCapacitorView', () => {
  beforeEach(() => {
    // Intentionally empty: explicit hook keeps test structure aligned with the other module suites.
  })

  it('renders with empty conversion inputs and placeholder decoded output', () => {
    const wrapper = mountView()

    const conversionInputs = wrapper.findAll('.form-grid-wide input')
    expect(conversionInputs).toHaveLength(4)
    expect(conversionInputs.every((input) => input.element.value === '')).toBe(true)

    const values = wrapper.findAll('.output-values strong').map((node) => node.text())
    expect(values).toEqual(['---', '---', '---', '---', '---'])
  })

  it('syncs capacitance unit conversion from pF and clears values on reset', async () => {
    const wrapper = mountView()
    const conversionInputs = wrapper.findAll('.form-grid-wide input')

    await conversionInputs[0].setValue('1000000')

    expect(conversionInputs[0].element.value).toBe('1000000')
    expect(conversionInputs[1].element.value).toBe('1000')
    expect(conversionInputs[2].element.value).toBe('1')
    expect(conversionInputs[3].element.value).toBe('0.000001')

    await wrapper.findAll('.btn-secondary-action')[0].trigger('click')

    expect(conversionInputs.every((input) => input.element.value === '')).toBe(true)
  })

  it('decodes capacitor code and optional labels, then resets code fields', async () => {
    const wrapper = mountView()
    const decodeForm = wrapper.get('form.panel-form')

    await decodeForm.get('input[type="text"]').setValue('104')
    await decodeForm.findAll('select')[0].setValue('J')
    await decodeForm.findAll('select')[1].setValue('1C')
    await decodeForm.trigger('submit.prevent')

    const values = wrapper.findAll('.output-values strong').map((node) => node.text())
    expect(values).toEqual(['100000 pF', '100.000 nF', '0.100000 µF', '±5%', '16 V'])

    await decodeForm.get('.btn-secondary-action').trigger('click')
    expect(wrapper.findAll('.output-values strong').map((node) => node.text())).toEqual([
      '---',
      '---',
      '---',
      '---',
      '---',
    ])
  })
})
