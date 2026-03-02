import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import InventoryForm from '../InventoryForm.vue'

const postMock = vi.fn()

vi.mock('@/services/api', () => ({
  api: {
    post: postMock,
  },
}))

vi.mock('@/services/toastService', () => ({
  showError: vi.fn(),
  showSuccess: vi.fn(),
}))

describe('InventoryForm.vue', () => {
  beforeEach(() => {
    postMock.mockReset()
  })

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
    expect(wrapper.get('[data-testid="inventory-name"]').element.value).toBe(item.name)
    expect(wrapper.get('[data-testid="inventory-sku"]').element.value).toBe(item.sku)
    expect(Number(wrapper.get('[data-testid="inventory-stock"]').element.value)).toBe(item.stock)
    expect(Number(wrapper.get('[data-testid="inventory-min-stock"]').element.value)).toBe(item.min_stock)
    expect(Number(wrapper.get('[data-testid="inventory-price"]').element.value)).toBe(item.price)
    expect(wrapper.get('[data-testid="inventory-enabled"]').element.checked).toBe(true)
    expect(wrapper.get('[data-testid="inventory-store-visible"]').element.checked).toBe(true)
    expect(wrapper.get('[data-testid="inventory-image-url"]').element.value).toBe(item.image_url)

    await wrapper.get('[data-testid="inventory-form"]').trigger('submit')
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
    await wrapper.get('[data-testid="inventory-cancel"]').trigger('click')
    expect(wrapper.emitted('cancel')).toBeTruthy()
  })

  it('uploads selected image and assigns returned public path', async () => {
    postMock.mockResolvedValue({
      data: {
        public_path: '/images/INVENTARIO/test.webp',
      },
    })

    const wrapper = mountForm()
    const file = new File(['webp'], 'test.webp', { type: 'image/webp' })
    const fileInput = wrapper.get('[data-testid="inventory-image-file"]')
    await fileInput.trigger('change', {
      target: {
        files: [file],
      },
    })

    await wrapper.get('[data-testid="inventory-image-upload"]').trigger('click')

    expect(postMock).toHaveBeenCalledTimes(1)
    expect(postMock.mock.calls[0][0]).toBe('/uploads/images?destination=inventario')
    expect(wrapper.get('[data-testid="inventory-image-url"]').element.value).toBe('/images/INVENTARIO/test.webp')
  })
})
