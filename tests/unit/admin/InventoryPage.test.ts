import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { reactive } from 'vue'

const routeState = vi.hoisted(() => ({
  query: {},
}))
const routerReplace = vi.hoisted(() => vi.fn())
const toastMock = vi.hoisted(() => ({
  showError: vi.fn(),
  showSuccess: vi.fn(),
}))
const storeState = vi.hoisted(() => ({
  current: null,
}))
const categoriesStoreState = vi.hoisted(() => ({
  current: null,
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeState,
  useRouter: () => ({ replace: routerReplace }),
}))

vi.mock('@/services/toastService', () => toastMock)

vi.mock('@/stores/inventory', () => ({
  useInventoryStore: () => storeState.current,
}))

vi.mock('@/stores/categories', () => ({
  useCategoriesStore: () => categoriesStoreState.current,
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
        <div data-testid="inventory-table-count">{{ items.length }}</div>
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
    storeState.current = reactive({
      items: [
        { id: 5, name: 'Resistencia 10K', sku: 'RES-10K', category: 'Resistencias', category_id: 9, store_visible: true, sellable_stock: 4, image_url: '/images/INVENTARIO/res.webp', is_low_stock: false, stock: 10, quantity_reserved: 2, quantity_in_work: 0, quantity_internal_use: 0, price: 1000 },
        { id: 7, name: 'Jack 6.3', sku: 'JACK-63', category: 'Conectores', category_id: 3, store_visible: false, sellable_stock: 0, image_url: '', is_low_stock: true, stock: 0, quantity_reserved: 0, quantity_in_work: 1, quantity_internal_use: 0, price: 1500 },
      ],
      loading: false,
      error: null,
      page: 1,
      limit: 50,
      catalogStatus: null,
      syncingCatalog: false,
      fetchItems: vi.fn().mockResolvedValue({}),
      deleteItem: vi.fn().mockResolvedValue(true),
      updateItem: vi.fn().mockResolvedValue({}),
      createItem: vi.fn().mockResolvedValue({}),
      fetchCatalogStatus: vi.fn().mockImplementation(async () => {
        storeState.current.catalogStatus = {
          files_count: 10,
          linked_products_count: 8,
          explicit_store_visible_count: 8,
          with_nonzero_stock_count: 2,
          sellable_now_count: 1,
          pending_images_count: 2,
          orphan_rows_count: 0,
          pending_images: ['nuevo_1.webp', 'nuevo_2.webp'],
          orphan_rows: [],
        }
        return storeState.current.catalogStatus
      }),
      syncCatalog: vi.fn().mockImplementation(async () => {
        storeState.current.catalogStatus = {
          files_count: 10,
          linked_products_count: 10,
          explicit_store_visible_count: 10,
          with_nonzero_stock_count: 2,
          sellable_now_count: 1,
          pending_images_count: 0,
          orphan_rows_count: 0,
          pending_images: [],
          orphan_rows: [],
        }
        await storeState.current.fetchItems(1, 50)
        return {
          result: { matched: 8, created: 2 },
          status: storeState.current.catalogStatus,
        }
      }),
      fetchItemById: vi.fn().mockResolvedValue({ id: 5, name: 'Resistencia 10K' }),
    })
    categoriesStoreState.current = reactive({
      categories: [
        { id: 3, name: 'Conectores' },
        { id: 9, name: 'Resistencias' },
      ],
      fetchCategories: vi.fn().mockResolvedValue({}),
    })
    vi.spyOn(window, 'confirm').mockReturnValue(true)
  })

  it('loads inventory and opens the create flow', async () => {
    const wrapper = mount(InventoryPage, {
      global: { stubs },
    })

    await flushPromises()
    expect(storeState.current.fetchItems).toHaveBeenCalledWith(1, 50)
    expect(storeState.current.fetchCatalogStatus).toHaveBeenCalled()
    expect(categoriesStoreState.current.fetchCategories).toHaveBeenCalled()
    expect(wrapper.find('[data-testid="inventory-stock-sheet"]').exists()).toBe(true)
    expect(wrapper.get('[data-testid="inventory-catalog-pending"]').text()).toBe('2')
    expect(wrapper.get('[data-testid="inventory-results-count"]').text()).toContain('2 de 2')
    expect(wrapper.get('[data-testid="inventory-scope-summary"]').text()).toContain('Interno sólo')
    expect(wrapper.get('[data-testid="inventory-scope-summary"]').text()).toContain('Reservados / OT')

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

    expect(storeState.current.deleteItem).toHaveBeenCalledWith(5)
    expect(toastMock.showSuccess).toHaveBeenCalledWith('Item eliminado correctamente.')
  })

  it('syncs store catalog from admin and refreshes status', async () => {
    const wrapper = mount(InventoryPage, {
      global: { stubs },
    })

    await flushPromises()
    await wrapper.get('[data-testid="inventory-sync-catalog"]').trigger('click')
    await flushPromises()

    expect(storeState.current.syncCatalog).toHaveBeenCalled()
    expect(storeState.current.fetchItems).toHaveBeenCalledTimes(2)
    expect(toastMock.showSuccess).toHaveBeenCalledWith('Catálogo sincronizado. 8 vinculados, 2 creados.')
    expect(wrapper.get('[data-testid="inventory-catalog-pending"]').text()).toBe('0')
  })

  it('filters loaded inventory items in admin', async () => {
    const wrapper = mount(InventoryPage, {
      global: { stubs },
    })

    await flushPromises()
    await wrapper.get('[data-testid="inventory-view-manage"]').trigger('click')
    expect(wrapper.get('[data-testid="inventory-table-count"]').text()).toBe('2')

    await wrapper.get('[data-testid="inventory-search-input"]').setValue('jack')
    await flushPromises()
    expect(wrapper.get('[data-testid="inventory-table-count"]').text()).toBe('1')

    await wrapper.get('[data-testid="inventory-filter-scope"]').setValue('published')
    await flushPromises()
    expect(wrapper.get('[data-testid="inventory-table-count"]').text()).toBe('0')

    await wrapper.get('[data-testid="inventory-clear-filters"]').trigger('click')
    await flushPromises()
    await wrapper.get('[data-testid="inventory-filter-scope"]').setValue('reserved')
    await flushPromises()
    expect(wrapper.get('[data-testid="inventory-table-count"]').text()).toBe('1')

    await wrapper.get('[data-testid="inventory-clear-filters"]').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-testid="inventory-table-count"]').text()).toBe('2')
  })
})
