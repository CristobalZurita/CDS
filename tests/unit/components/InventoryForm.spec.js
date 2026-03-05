import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import InventoryForm from '../../../src/vue/components/admin/InventoryForm.vue'

describe('InventoryForm', () => {
  function mountWithPinia(options = {}) {
    const pinia = createPinia()
    setActivePinia(pinia)
    return mount(InventoryForm, {
      global: { plugins: [pinia] },
      ...options
    })
  }

  it('emits save with form payload when submitted (new item)', async () => {
    const wrapper = mountWithPinia()
    const inputs = wrapper.findAll('input')
    // inputs order: name, category, sku, stock_unit, stock, price, image_url
    await inputs[0].setValue('Nuevo')
    await inputs[4].setValue(3)
    await wrapper.find('form').trigger('submit.prevent')
    const ev = wrapper.emitted().save
    expect(ev).toBeTruthy()
    expect(ev[0][0].name).toBe('Nuevo')
    expect(ev[0][0].stock).toBe(3)
  })

  it('prefills fields when item prop is provided and emits id on save', async () => {
    const item = { id: 5, name: 'Exist', sku: 'X5', stock: 10 }
    const wrapper = mountWithPinia({ props: { item } })
    const inputs = wrapper.findAll('input')
    expect(inputs[0].element.value).toBe('Exist')
    await wrapper.find('form').trigger('submit.prevent')
    const ev = wrapper.emitted().save
    expect(ev[0][0].id).toBe(5)
  })
})
