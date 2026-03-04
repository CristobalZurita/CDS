import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import SmdResistorView from '@/modules/smdResistor/SmdResistorView.vue'

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

const buildCanvasContext = () => ({
  clearRect: vi.fn(),
  fillRect: vi.fn(),
  beginPath: vi.fn(),
  moveTo: vi.fn(),
  lineTo: vi.fn(),
  stroke: vi.fn(),
  fill: vi.fn(),
  arc: vi.fn(),
  arcTo: vi.fn(),
  closePath: vi.fn(),
  fillText: vi.fn(),
  lineWidth: 0,
  strokeStyle: '',
  fillStyle: '',
  font: '',
})

function mountView() {
  return mount(SmdResistorView, {
    global: {
      stubs,
    },
  })
}

describe('SmdResistorView', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    const ctx = buildCanvasContext()
    Object.defineProperty(HTMLCanvasElement.prototype, 'getContext', {
      configurable: true,
      value: vi.fn(() => ctx),
    })
  })

  afterEach(() => {
    vi.clearAllTimers()
    vi.useRealTimers()
  })

  it('renders default CD40106 values and computed frequency output', () => {
    const wrapper = mountView()
    const rows = wrapper.findAll('.value-row strong')

    expect(wrapper.text()).toContain('CD40106')
    expect(rows[0].text()).toBe('83.33 Hz')
    expect(rows[1].text()).toBe('12.00 ms')
  })

  it('updates computed output and restores defaults when reset is clicked', async () => {
    const wrapper = mountView()
    const numberInputs = wrapper.findAll('input[type="number"]')
    const selects = wrapper.findAll('select')

    await numberInputs[0].setValue('0')
    expect(wrapper.findAll('.value-row strong')[0].text()).toBe('---')
    expect(wrapper.findAll('.value-row strong')[1].text()).toBe('---')

    await numberInputs[0].setValue('22')
    await numberInputs[1].setValue('10')
    await numberInputs[2].setValue('12')
    await selects[0].setValue('mohm')
    await selects[1].setValue('nf')

    await wrapper.get('.btn-secondary-action').trigger('click')

    expect(numberInputs[0].element.value).toBe('100')
    expect(numberInputs[1].element.value).toBe('0.1')
    expect(numberInputs[2].element.value).toBe('9')
    expect(selects[0].element.value).toBe('kohm')
    expect(selects[1].element.value).toBe('uf')
  })

  it('restarts the blink loop when the form is submitted', async () => {
    const setTimeoutSpy = vi.spyOn(window, 'setTimeout')
    const wrapper = mountView()
    const baselineCalls = setTimeoutSpy.mock.calls.length

    await wrapper.get('form').trigger('submit.prevent')

    expect(setTimeoutSpy.mock.calls.length).toBeGreaterThan(baselineCalls)
  })
})
