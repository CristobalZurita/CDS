import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import InventoryCard from '../../../src/components/prototypes/InventoryCard.vue'

describe('InventoryCard', () => {
  it('emits request-edit and request-delete with the item', async () => {
    const item = { id: 2, name: 'Item', sku: '10', stock: 2, price: 12.5 }
    const wrapper = mount(InventoryCard, { props: { item } })

    await wrapper.find('button.btn-primary').trigger('click')
    expect(wrapper.emitted()['request-edit']).toBeTruthy()
    expect(wrapper.emitted()['request-edit'][0]).toEqual([item])

    await wrapper.find('button.btn-danger').trigger('click')
    expect(wrapper.emitted()['request-delete']).toBeTruthy()
    expect(wrapper.emitted()['request-delete'][0]).toEqual([item])
  })

  it('shows - when price not present', () => {
    const item = { id: 1, name: 'NoPrice' }
    const wrapper = mount(InventoryCard, { props: { item } })
    expect(wrapper.html()).toContain('$-')
  })
})
