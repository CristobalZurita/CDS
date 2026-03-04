import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const useCalculatorMock = vi.hoisted(() => vi.fn())

vi.mock('@/composables/useCalculator', () => ({
  useCalculator: useCalculatorMock,
}))

import Timer555View from '@/modules/timer555/Timer555View.vue'

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

function getModeTab(wrapper: ReturnType<typeof mount>, label: 'Astable' | 'Monostable') {
  const tab = wrapper.findAll('.panel-tab').find((btn) => btn.text().includes(label))
  if (!tab) {
    throw new Error(`Mode tab not found: ${label}`)
  }
  return tab
}

function mountView(initialResult: unknown = null) {
  const result = ref(initialResult)
  const calculate = vi.fn()
  useCalculatorMock.mockReturnValueOnce({
    result,
    calculate,
  })

  const wrapper = mount(Timer555View, {
    global: {
      stubs,
    },
  })

  return { wrapper, result, calculate }
}

describe('Timer555View', () => {
  beforeEach(() => {
    useCalculatorMock.mockReset()
    vi.clearAllMocks()
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

  it('renders in astable mode by default with placeholder outputs', () => {
    const { wrapper } = mountView()

    expect(wrapper.findAll('input[type="number"]')).toHaveLength(4)
    expect(wrapper.findAll('select')).toHaveLength(3)
    expect(wrapper.text()).toContain('R1')
    expect(wrapper.text()).toContain('R2')
    expect(wrapper.findAll('.value-row strong')[0].text()).toBe('---')
  })

  it('submits monostable input mapped to the domain contract', async () => {
    const { wrapper, calculate } = mountView()

    await getModeTab(wrapper, 'Monostable').trigger('click')

    const numberInputs = wrapper.findAll('input[type="number"]')
    const selects = wrapper.findAll('select')

    await numberInputs[0].setValue('2')
    await numberInputs[1].setValue('3')
    await numberInputs[2].setValue('12')
    await selects[0].setValue('mohm')
    await selects[1].setValue('nf')
    await wrapper.get('form').trigger('submit.prevent')

    expect(calculate).toHaveBeenCalledTimes(1)

    const payload = calculate.mock.calls[0][0]
    expect(payload.mode).toBe('monostable')
    expect(payload.R_ohm).toBe(2_000_000)
    expect(payload.C_farad).toBeCloseTo(3e-9, 15)
    expect(payload.Vcc_volt).toBe(12)
  })

  it('submits astable input, then reset restores defaults and clears result state', async () => {
    const { wrapper, result, calculate } = mountView({
      state: 'OK',
      value: {
        frequency_hz: 12,
        t_high_s: 0.1,
        t_low_s: 0.2,
        duty_cycle: 0.333,
        period_s: 0.3,
      },
    })

    const numberInputs = wrapper.findAll('input[type="number"]')
    const selects = wrapper.findAll('select')

    await numberInputs[0].setValue('1')
    await numberInputs[1].setValue('2')
    await numberInputs[2].setValue('4')
    await numberInputs[3].setValue('9')
    await selects[0].setValue('mohm')
    await selects[1].setValue('kohm')
    await selects[2].setValue('nf')

    await wrapper.get('form').trigger('submit.prevent')
    expect(calculate).toHaveBeenCalledTimes(1)

    const firstPayload = calculate.mock.calls[0][0]
    expect(firstPayload.mode).toBe('astable_standard')
    expect(firstPayload.R1_ohm).toBe(1_000_000)
    expect(firstPayload.R2_ohm).toBe(2_000)
    expect(firstPayload.C_farad).toBe(4e-9)
    expect(firstPayload.Vcc_volt).toBe(9)

    await wrapper.get('.btn-secondary-action').trigger('click')

    expect(result.value).toBeNull()
    expect(numberInputs[0].element.value).toBe('1')
    expect(numberInputs[1].element.value).toBe('330')
    expect(numberInputs[2].element.value).toBe('2.2')
    expect(numberInputs[3].element.value).toBe('5')
    expect(selects[0].element.value).toBe('kohm')
    expect(selects[1].element.value).toBe('kohm')
    expect(selects[2].element.value).toBe('uf')

    await wrapper.get('form').trigger('submit.prevent')
    expect(calculate).toHaveBeenCalledTimes(2)

    const secondPayload = calculate.mock.calls[1][0]
    expect(secondPayload).toMatchObject({
      mode: 'astable_standard',
      R1_ohm: 1000,
      R2_ohm: 330000,
      Vcc_volt: 5,
    })
    expect(secondPayload.C_farad).toBeCloseTo(2.2e-6, 12)
  })

  it('renders formatted output and hides astable-only rows in monostable mode', async () => {
    const { wrapper } = mountView({
      state: 'OK',
      value: {
        frequency_hz: 10,
        t_high_s: 0.2,
        t_low_s: 0.1,
        duty_cycle: 0.666,
        period_s: 0.3,
      },
    })

    expect(wrapper.text()).toContain('10.000 Hz')
    expect(wrapper.text()).toContain('200.000 ms')
    expect(wrapper.text()).toContain('100.000 ms')
    expect(wrapper.text()).toContain('66.60 %')
    expect(wrapper.text()).toContain('300.000 ms')

    await getModeTab(wrapper, 'Monostable').trigger('click')
    expect(wrapper.text()).not.toContain('Tiempo bajo')
    expect(wrapper.text()).not.toContain('Ciclo')
  })
})
