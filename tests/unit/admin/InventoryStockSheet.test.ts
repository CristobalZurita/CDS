import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import InventoryStockSheet from '@/vue/components/admin/InventoryStockSheet.vue'

describe('InventoryStockSheet', () => {
  const items = [
    { id: 1, name: 'Resistencia 10K', sku: 'RES-10K', category: 'Resistencias', stock: 0, min_stock: 0, price: 1000, enabled: true, store_visible: false },
    { id: 2, name: 'Jack 6.3', sku: 'JACK-63', category: 'Conectores', stock: 0, min_stock: 0, price: 1000, enabled: true, store_visible: false },
  ]

  it('applies bulk values and emits save-many for selected rows', async () => {
    const wrapper = mount(InventoryStockSheet, {
      props: { items },
    })

    await wrapper.get('[data-testid="inventory-sheet-select-visible"]').trigger('click')
    await wrapper.get('[data-testid="inventory-sheet-bulk-stock"]').setValue('5')
    await wrapper.get('[data-testid="inventory-sheet-bulk-min-stock"]').setValue('1')
    await wrapper.get('[data-testid="inventory-sheet-bulk-price"]').setValue('2500')
    await wrapper.get('[data-testid="inventory-sheet-bulk-enabled"]').setValue('true')
    await wrapper.get('[data-testid="inventory-sheet-bulk-store-visible"]').setValue('true')
    await wrapper.get('[data-testid="inventory-sheet-apply-bulk"]').trigger('click')
    await wrapper.get('[data-testid="inventory-sheet-save-selected"]').trigger('click')

    const emitted = wrapper.emitted('save-many')
    expect(emitted).toBeTruthy()
    expect(emitted[0][0]).toEqual([
      { id: 1, stock: 5, min_stock: 1, price: 2500, enabled: true, store_visible: true },
      { id: 2, stock: 5, min_stock: 1, price: 2500, enabled: true, store_visible: true },
    ])
  })
})
