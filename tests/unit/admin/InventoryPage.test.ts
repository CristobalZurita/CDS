import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const routeState = vi.hoisted(() => ({
  query: {},
}))
const routerReplace = vi.hoisted(() => vi.fn())
const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
}))
const toastMock = vi.hoisted(() => ({
  showError: vi.fn(),
  showSuccess: vi.fn(),
}))
const storeMock = vi.hoisted(() => ({
  items: [],
  fetchItems: vi.fn(),
  deleteItem: vi.fn(),
  updateItem: vi.fn(),
  createItem: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeState,
  useRouter: () => ({ replace: routerReplace }),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

vi.mock('@/services/toastService', () => toastMock)

vi.mock('@/stores/inventory', () => ({
  useInventoryStore: () => storeMock,
}))

import InventoryPage from '@/vue/content/pages/admin/InventoryPage.vue'

const stubs = {
  AdminLayout: { template: '<div><slot /></div>' },
  InventoryAlerts: { template: '<div data-testid="inventory-alerts-stub" />' },
  InventoryStockSheet: { template: '<div data-testid="inventory-stock-sheet" />' },
  InventoryStockStates: { template: '<div data-testid="inventory-stock-states" />' },
  InventoryTable: {
    props: ['items'],
    template: `
      <div data-testid="inventory-table">
        <button data-testid="inventory-table-edit" @click="$emit('edit', items[0])">edit</button>
        <button data-testid="inventory-table-delete" @click="$emit('delete', items[0])">delete</button>
      </div>
    `,
  },
  InventoryForm: {
    props: ['item'],
    template: `
      <div data-testid="inventory-form">
        <button data-testid="inventory-form-save" @click="$emit('save', { id: item?.id, name: 'Guardado' })">save</button>
        <button data-testid="inventory-form-cancel" @click="$emit('cancel')">cancel</button>
      </div>
    `,
  },
}

describe('InventoryPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    routeState.query = {}
    storeMock.items = [{ id: 5, name: 'Resistencia 10K' }]
    storeMock.fetchItems.mockResolvedValue({})
    storeMock.deleteItem.mockResolvedValue(true)
    storeMock.updateItem.mockResolvedValue({})
    storeMock.createItem.mockResolvedValue({})
    apiMock.get.mockResolvedValue({ data: { id: 5, name: 'Resistencia 10K' } })
    vi.spyOn(window, 'confirm').mockReturnValue(true)
  })

  it('loads inventory and opens the create flow', async () => {
    const wrapper = mount(InventoryPage, {
      global: { stubs },
    })

    await flushPromises()
    expect(storeMock.fetchItems).toHaveBeenCalledWith(1, 50)
    expect(wrapper.find('[data-testid="inventory-stock-sheet"]').exists()).toBe(true)

    await wrapper.get('[data-testid="inventory-new"]').trigger('click')

    expect(routerReplace).toHaveBeenCalledWith({ query: { edit: 'new' } })
    expect(wrapper.find('[data-testid="inventory-form"]').exists()).toBe(true)
  })

  it('deletes items and reports success', async () => {
    const wrapper = mount(InventoryPage, {
      global: { stubs },
    })

    await flushPromises()
    await wrapper.get('[data-testid="inventory-view-manage"]').trigger('click')
    await wrapper.get('[data-testid="inventory-table-delete"]').trigger('click')
    await flushPromises()

    expect(storeMock.deleteItem).toHaveBeenCalledWith(5)
    expect(toastMock.showSuccess).toHaveBeenCalledWith('Item eliminado correctamente.')
  })
})
