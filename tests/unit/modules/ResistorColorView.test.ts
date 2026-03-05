import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const useCalculatorMock = vi.hoisted(() => vi.fn())

vi.mock('@/composables/useCalculator', () => ({
  useCalculator: useCalculatorMock,
}))

import ResistorColorView from '@/modules/resistorColor/ResistorColorView.vue'

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

function getBandTab(wrapper: ReturnType<typeof mount>, bands: 4 | 5 | 6) {
  const tab = wrapper.findAll('.panel-tab').find((btn) => btn.text().includes(`${bands} bandas`))
  if (!tab) {
    throw new Error(`Band tab not found: ${bands}`)
  }
  return tab
}

function mountView(options: {
  thtResultValue?: unknown
  smdResultValue?: unknown
} = {}) {
  const thtResult = ref(options.thtResultValue ?? null)
  const smdResult = ref(options.smdResultValue ?? null)
  const thtCalculate = vi.fn()
  const smdCalculate = vi.fn()

  useCalculatorMock
    .mockReturnValueOnce({
      result: thtResult,
      calculate: thtCalculate,
    })
    .mockReturnValueOnce({
      result: smdResult,
      calculate: smdCalculate,
    })

  const wrapper = mount(ResistorColorView, {
    global: {
      stubs,
    },
  })

  return {
    wrapper,
    thtResult,
    smdResult,
    thtCalculate,
    smdCalculate,
  }
}

describe('ResistorColorView', () => {
  beforeEach(() => {
    useCalculatorMock.mockReset()
    vi.clearAllMocks()
  })

  it('renders default 4-band form with placeholders', () => {
    const { wrapper } = mountView()

    expect(wrapper.text()).toContain('Calculadora')
    expect(wrapper.findAll('.panel-tab')).toHaveLength(3)
    expect(wrapper.findAll('form')[0].findAll('select')).toHaveLength(4)
    expect(wrapper.findAll('form')[0].text()).not.toContain('3ra banda')
    expect(wrapper.findAll('form')[0].text()).not.toContain('Tempco')
    expect(wrapper.findAll('.value-main')[0].text()).toBe('---')
  })

  it('changes conditional fields when switching to 5 and 6 bands', async () => {
    const { wrapper } = mountView()

    await getBandTab(wrapper, 5).trigger('click')
    expect(wrapper.findAll('form')[0].findAll('select')).toHaveLength(5)
    expect(wrapper.findAll('form')[0].text()).toContain('3ra banda')

    await getBandTab(wrapper, 6).trigger('click')
    expect(wrapper.findAll('form')[0].findAll('select')).toHaveLength(6)
    expect(wrapper.findAll('form')[0].text()).toContain('Tempco')
  })

  it('submits THT calculation using the selected preset', async () => {
    const { wrapper, thtCalculate } = mountView()

    await getBandTab(wrapper, 6).trigger('click')
    await wrapper.findAll('form')[0].trigger('submit.prevent')

    expect(thtCalculate).toHaveBeenCalledTimes(1)
    expect(thtCalculate.mock.calls[0][0]).toMatchObject({
      bands: 6,
      colors: ['brown', 'black', 'black', 'red', 'brown', 'brown'],
    })
  })

  it('formats and renders THT/SMD output values when calculations are OK', () => {
    const { wrapper } = mountView({
      thtResultValue: {
        state: 'OK',
        value: {
          resistance_ohm: 1000,
          tolerance_percent: 5,
          min_ohm: 950,
          max_ohm: 1050,
          tempco_ppm: 50,
        },
      },
      smdResultValue: {
        state: 'OK',
        value: {
          resistance_ohm: 4700,
        },
      },
    })

    expect(wrapper.text()).toContain('1.00 kΩ')
    expect(wrapper.text()).toContain('Rango: 950.00 Ω — 1.05 kΩ')
    expect(wrapper.text()).toContain('Tempco: 50 ppm')
    expect(wrapper.findAll('.value-main')[1].text()).toBe('4.70 kΩ')
  })

  it('resets THT state to default preset and clears previous result', async () => {
    const { wrapper, thtResult, thtCalculate } = mountView({
      thtResultValue: {
        state: 'OK',
        value: {
          resistance_ohm: 2200,
          tolerance_percent: 5,
          min_ohm: 2090,
          max_ohm: 2310,
        },
      },
    })

    await getBandTab(wrapper, 6).trigger('click')
    await wrapper.findAll('form')[0].find('.btn-secondary-action').trigger('click')

    expect(thtResult.value).toBeNull()
    expect(wrapper.findAll('form')[0].findAll('select')).toHaveLength(4)

    await wrapper.findAll('form')[0].trigger('submit.prevent')
    expect(thtCalculate.mock.calls[0][0]).toMatchObject({
      bands: 4,
      colors: ['brown', 'black', 'red', 'gold'],
    })
  })

  it('submits and resets the SMD flow with trimmed code and default type', async () => {
    const { wrapper, smdResult, smdCalculate } = mountView()
    const smdForm = wrapper.findAll('form')[1]

    await smdForm.get('input').setValue(' 103 ')
    await smdForm.get('select').setValue('EIA4')
    await smdForm.trigger('submit.prevent')

    expect(smdCalculate).toHaveBeenCalledTimes(1)
    expect(smdCalculate.mock.calls[0][0]).toMatchObject({
      code: '103',
      type: 'EIA4',
    })

    smdResult.value = {
      state: 'OK',
      value: { resistance_ohm: 1000 },
    }

    await smdForm.find('.btn-secondary-action').trigger('click')

    expect(smdResult.value).toBeNull()

    await smdForm.trigger('submit.prevent')
    expect(smdCalculate).toHaveBeenCalledTimes(2)
    expect(smdCalculate.mock.calls[1][0]).toMatchObject({
      code: '',
      type: 'EIA3',
    })
  })
})
