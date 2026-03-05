import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  put: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

import RepairCostSummary from '@/vue/components/admin/repair/RepairCostSummary.vue'
import RepairStatusChanger from '@/vue/components/admin/repair/RepairStatusChanger.vue'

describe('repair controls components', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.put.mockResolvedValue({ data: { id: 5 } })
  })

  it('renders cost summary and saves labor/other cost edits', async () => {
    const wrapper = mount(RepairCostSummary, {
      props: {
        repairId: 5,
        materialsCost: 700,
        componentsCount: 2,
        isReadOnly: false,
        repair: {
          labor_cost: 1000,
          other_costs: 500,
          other_costs_notes: 'Flete',
          quoted_price: 3000,
        },
      },
    })

    expect(wrapper.text()).toContain('Resumen de Costos')
    expect(wrapper.text()).toContain('2 items')
    expect(wrapper.text()).toContain('Costo Total')
    expect(wrapper.text()).toContain('Margen')

    const editButtons = wrapper.findAll('button.edit-btn')
    expect(editButtons).toHaveLength(2)

    await editButtons[0].trigger('click')
    expect(wrapper.text()).toContain('Editar Mano de Obra')

    const laborInput = wrapper.find('input[type="number"]')
    await laborInput.setValue('1500')
    const saveButtons = wrapper.findAll('button.btn.btn-primary')
    await saveButtons[0].trigger('click')
    await flushPromises()

    expect(apiMock.put).toHaveBeenCalledWith('/repairs/5', {
      labor_cost: 1500,
    })
    expect(wrapper.emitted('updated')).toBeTruthy()

    await editButtons[1].trigger('click')
    expect(wrapper.text()).toContain('Editar Otros Gastos')

    const numberInputs = wrapper.findAll('input[type="number"]')
    await numberInputs[numberInputs.length - 1].setValue('900')
    await wrapper.find('textarea').setValue('Insumos extra')
    const primaryButtons = wrapper.findAll('button.btn.btn-primary')
    await primaryButtons[primaryButtons.length - 1].trigger('click')
    await flushPromises()

    expect(apiMock.put).toHaveBeenCalledWith('/repairs/5', {
      other_costs: 900,
      other_costs_notes: 'Insumos extra',
    })
  })

  it('shows negative margin warning when quoted price is below total cost', () => {
    const wrapper = mount(RepairCostSummary, {
      props: {
        repairId: 12,
        materialsCost: 1500,
        componentsCount: 1,
        isReadOnly: true,
        repair: {
          labor_cost: 4000,
          other_costs: 500,
          quoted_price: 3000,
        },
      },
    })

    expect(wrapper.text()).toContain('El costo real supera el precio cotizado')
  })

  it('changes status through confirmation modal and emits statusChanged payload', async () => {
    apiMock.put.mockResolvedValueOnce({
      data: { id: 9, status_id: 6 },
    })

    const wrapper = mount(RepairStatusChanger, {
      props: {
        repairId: 9,
        currentStatusId: 5,
        statuses: [],
      },
    })

    expect(wrapper.get('[data-testid="repair-current-status"]').text()).toContain('En trabajo')
    expect(wrapper.text()).toContain('60%')

    await wrapper.get('[data-testid="repair-transition-6"]').trigger('click')
    expect(wrapper.text()).toContain('Confirmar cambio de estado')

    await wrapper.get('textarea').setValue('Avanza a listo')
    await wrapper.get('[data-testid="repair-status-confirm"]').trigger('click')
    await flushPromises()

    expect(apiMock.put).toHaveBeenCalledWith('/repairs/9', {
      status_id: 6,
      status_notes: 'Avanza a listo',
    })
    expect(wrapper.emitted('statusChanged')?.[0]?.[0]).toEqual({
      newStatusId: 6,
      repair: { id: 9, status_id: 6 },
    })
  })

  it('renders terminal notice for archived status', () => {
    const wrapper = mount(RepairStatusChanger, {
      props: {
        repairId: 11,
        currentStatusId: 9,
        statuses: [],
      },
    })

    expect(wrapper.text()).toContain('Estado terminal - No se permiten más cambios')
    expect(wrapper.find('[data-testid^="repair-transition-"]').exists()).toBe(false)
  })
})
