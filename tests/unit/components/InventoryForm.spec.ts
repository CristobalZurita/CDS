import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'
import InventoryForm from '../../../src/vue/components/admin/InventoryForm.vue'

const { postMock } = vi.hoisted(() => ({
  postMock: vi.fn(),
}))

const { getMock, putMock, deleteRequestMock, handleApiErrorMock } = vi.hoisted(() => ({
  getMock: vi.fn(),
  putMock: vi.fn(),
  deleteRequestMock: vi.fn(),
  handleApiErrorMock: vi.fn((error) => ({
    message: error?.message ?? 'Unknown error',
  })),
}))

vi.mock('@/services/api', () => ({
  get: getMock,
  post: postMock,
  put: putMock,
  deleteRequest: deleteRequestMock,
  handleApiError: handleApiErrorMock,
  api: {
    get: getMock,
    post: postMock,
    put: putMock,
    delete: deleteRequestMock,
  },
}))

vi.mock('@/services/toastService', () => ({
  showError: vi.fn(),
  showSuccess: vi.fn(),
}))

describe('InventoryForm', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    postMock.mockReset()
    getMock.mockReset()
    putMock.mockReset()
    deleteRequestMock.mockReset()
    handleApiErrorMock.mockClear()
    getMock.mockResolvedValue({
      data: {
        data: [],
      },
    })
  })

  it('emits save with form payload when submitted (new item)', async () => {
    const wrapper = mount(InventoryForm, {
      global: {
        plugins: [createPinia()],
      },
    })
    await wrapper.get('[data-testid="inventory-name"]').setValue('Nuevo')
    await wrapper.get('[data-testid="inventory-stock"]').setValue(3)
    await wrapper.get('[data-testid="inventory-form"]').trigger('submit.prevent')
    const ev = wrapper.emitted().save
    expect(ev).toBeTruthy()
    expect(ev[0][0].name).toBe('Nuevo')
    expect(ev[0][0].stock).toBe(3)
  })

  it('prefills fields when item prop is provided and emits id on save', async () => {
    const item = { id: 5, name: 'Exist', sku: 'X5', stock: 10 }
    const wrapper = mount(InventoryForm, {
      props: { item },
      global: {
        plugins: [createPinia()],
      },
    })
    await nextTick()
    expect(wrapper.get('[data-testid="inventory-name"]').element.value).toBe('Exist')
    await wrapper.get('[data-testid="inventory-form"]').trigger('submit.prevent')
    const ev = wrapper.emitted().save
    expect(ev[0][0].id).toBe(5)
  })

  it('uploads inventory image and assigns public path', async () => {
    postMock.mockResolvedValue({
      data: {
        public_path: '/images/INVENTARIO/test.webp',
      },
    })
    const wrapper = mount(InventoryForm, {
      global: {
        plugins: [createPinia()],
      },
    })

    const file = new File(['webp'], 'test.webp', { type: 'image/webp' })
    const fileInput = wrapper.get('[data-testid="inventory-image-file"]')
    Object.defineProperty(fileInput.element, 'files', {
      value: [file],
      configurable: true,
    })
    await fileInput.trigger('change')
    await wrapper.get('[data-testid="inventory-image-upload"]').trigger('click')
    await Promise.resolve()
    await nextTick()

    expect(postMock).toHaveBeenCalledTimes(1)
    expect(postMock.mock.calls[0][0]).toBe('/uploads/images?destination=inventario')
    expect(wrapper.get('[data-testid="inventory-image-url"]').element.value).toBe('/images/INVENTARIO/test.webp')
  })
})
