import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import InventoryForm from '../InventoryForm.vue'

describe('InventoryForm.vue', () => {
  it('renders initial item props and emits save with payload', async () => {
    const item = {
      id: 5,
      name: 'Potenciómetro',
      category: 'Control',
      sku: 'POT-01',
      stock_unit: 'pcs',
      stock: 12,
      price: 4.5,
      image_url: 'http://img'
    }
    const wrapper = mount(InventoryForm, { props: { item } })
    const inputs = wrapper.findAll('input')
    // ordering in template: name, category, sku, stock_unit, stock, price, image_url
    expect(inputs[0].element.value).toBe(item.name)
    expect(inputs[1].element.value).toBe(item.category)
    expect(inputs[2].element.value).toBe(item.sku)
    expect(inputs[3].element.value).toBe(item.stock_unit)
    expect(Number(inputs[4].element.value)).toBe(item.stock)
    expect(Number(inputs[5].element.value)).toBe(item.price)
    expect(inputs[6].element.value).toBe(item.image_url)

    await wrapper.get('form').trigger('submit')
    const ev = wrapper.emitted('save')
    expect(ev).toBeTruthy()
    const payload = ev[0][0]
    expect(payload.name).toBe(item.name)
    expect(payload.id).toBe(item.id)
  })

  it('emits cancel when cancel button is clicked', async () => {
    const wrapper = mount(InventoryForm)
    const buttons = wrapper.findAll('button')
    // Cancel is the first button
    await buttons[0].trigger('click')
    expect(wrapper.emitted('cancel')).toBeTruthy()
  })
})
