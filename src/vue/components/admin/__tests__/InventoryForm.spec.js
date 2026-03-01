import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import InventoryForm from '../InventoryForm.vue'

describe('InventoryForm.vue', () => {
  const mountForm = (options = {}) => {
    setActivePinia(createPinia())
    return mount(InventoryForm, {
      global: {
        plugins: [createPinia()],
      },
      ...options,
    })
  }

  it('renders initial item props and emits save with payload', async () => {
    const item = {
      id: 5,
      name: 'Potenciómetro',
      category: 'Control',
      sku: 'POT-01',
      stock_unit: 'pcs',
      stock: 12,
      min_stock: 3,
      price: 4.5,
      image_url: 'http://img',
      enabled: true,
      store_visible: true,
    }
    const wrapper = mountForm({ props: { item } })
    const inputs = wrapper.findAll('input')
    // ordering in template: name, sku, stock_unit, stock, min_stock, price, enabled, store_visible, image_url
    expect(inputs[0].element.value).toBe(item.name)
    expect(inputs[1].element.value).toBe(item.sku)
    expect(inputs[2].element.value).toBe(item.stock_unit)
    expect(Number(inputs[3].element.value)).toBe(item.stock)
    expect(Number(inputs[4].element.value)).toBe(item.min_stock)
    expect(Number(inputs[5].element.value)).toBe(item.price)
    expect(inputs[6].element.checked).toBe(true)
    expect(inputs[7].element.checked).toBe(true)
    expect(inputs[8].element.value).toBe(item.image_url)

    await wrapper.get('form').trigger('submit')
    const ev = wrapper.emitted('save')
    expect(ev).toBeTruthy()
    const payload = ev[0][0]
    expect(payload.name).toBe(item.name)
    expect(payload.id).toBe(item.id)
    expect(payload.min_quantity).toBe(item.min_stock)
    expect(payload.store_visible).toBe(true)
  })

  it('emits cancel when cancel button is clicked', async () => {
    const wrapper = mountForm()
    const buttons = wrapper.findAll('button')
    // Cancel is the first button
    await buttons[0].trigger('click')
    expect(wrapper.emitted('cancel')).toBeTruthy()
  })
})
