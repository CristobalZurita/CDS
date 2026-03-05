import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const useCalculatorMock = vi.hoisted(() => vi.fn())

vi.mock('@/composables/useCalculator', () => ({
  useCalculator: useCalculatorMock,
}))

import AwgView from '@/modules/awg/AwgView.vue'
import LengthView from '@/modules/length/LengthView.vue'
import NumberSystemView from '@/modules/numberSystem/NumberSystemView.vue'
import OhmsLawView from '@/modules/ohmsLaw/OhmsLawView.vue'
import TemperatureView from '@/modules/temperature/TemperatureView.vue'

const cases = [
  { name: 'AwgView', component: AwgView, heading: 'Awg Calculator' },
  { name: 'LengthView', component: LengthView, heading: 'Length Calculator' },
  { name: 'NumberSystemView', component: NumberSystemView, heading: 'NumberSystem Calculator' },
  { name: 'OhmsLawView', component: OhmsLawView, heading: 'OhmsLaw Calculator' },
  { name: 'TemperatureView', component: TemperatureView, heading: 'Temperature Calculator' },
] as const

describe('simple calculator wrapper modules', () => {
  beforeEach(() => {
    useCalculatorMock.mockReset()
  })

  it.each(cases)('renders the wrapper shell and delegates submit in $name', async ({ component, heading }) => {
    const calculate = vi.fn()
    useCalculatorMock.mockReturnValue({
      result: ref(null),
      calculate,
    })

    const wrapper = mount(component)

    expect(wrapper.get('h1').text()).toBe(heading)
    expect(wrapper.text()).toContain('Inputs definidos por contrato')
    expect(useCalculatorMock).toHaveBeenCalledTimes(1)

    await wrapper.get('form').trigger('submit.prevent')

    expect(calculate).toHaveBeenCalledTimes(1)
    expect(Object.keys(calculate.mock.calls[0][0] as Record<string, unknown>)).toEqual([])
  })

  it.each(cases)('renders calculator errors in $name', ({ component }) => {
    useCalculatorMock.mockReturnValue({
      result: ref({
        state: 'INVALID',
        errors: ['Entrada inválida'],
      }),
      calculate: vi.fn(),
    })

    const wrapper = mount(component)

    expect(wrapper.get('li').text()).toBe('Entrada inválida')
  })
})
