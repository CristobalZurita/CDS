import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

import { useInventoryStore } from '@stores/inventory'

describe('inventory store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('starts with the current runtime state shape', () => {
    const store = useInventoryStore()

    expect(store.items).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.page).toBe(1)
    expect(store.limit).toBe(20)
    expect(store.catalogStatus).toBeNull()
    expect(store.syncingCatalog).toBe(false)
    expect(store.importing).toBe(false)
    expect(store.lastRunId).toBeNull()
    expect(store.runStatus).toBeNull()
  })

  it('fetches inventory items and tracks paging parameters', async () => {
    apiMock.get.mockResolvedValueOnce({
      data: [{ id: 1, name: 'Capacitor' }],
    })

    const store = useInventoryStore()
    await store.fetchItems(3, 50, 'cap', 9)

    expect(apiMock.get).toHaveBeenCalledWith('/inventory/?limit=50&page=3&search=cap&category_id=9')
    expect(store.items).toEqual([{ id: 1, name: 'Capacitor' }])
    expect(store.page).toBe(3)
    expect(store.limit).toBe(50)
    expect(store.loading).toBe(false)
  })

  it('stores catalog status inside the inventory store', async () => {
    apiMock.get.mockResolvedValueOnce({
      data: {
        files_count: 10,
        pending_images_count: 2,
      },
    })

    const store = useInventoryStore()
    const status = await store.fetchCatalogStatus()

    expect(apiMock.get).toHaveBeenCalledWith('/inventory/store-catalog/status')
    expect(status).toEqual({
      files_count: 10,
      pending_images_count: 2,
    })
    expect(store.catalogStatus).toEqual(status)
  })

  it('clears items when fetch fails', async () => {
    apiMock.get.mockRejectedValueOnce(new Error('boom'))

    const store = useInventoryStore()
    store.items = [{ id: 1 }]

    await store.fetchItems()

    expect(store.items).toEqual([])
    expect(store.loading).toBe(false)
  })

  it('normalizes quantity to stock on create and prepends the item', async () => {
    apiMock.post.mockResolvedValueOnce({
      data: { id: 2, name: 'Resistor', stock: 12 },
    })

    const store = useInventoryStore()
    store.items = [{ id: 1, name: 'Capacitor', stock: 5 }]

    const created = await store.createItem({
      name: 'Resistor',
      quantity: 12,
      min_stock: 2,
    })

    expect(apiMock.post).toHaveBeenCalledWith('/inventory/', {
      name: 'Resistor',
      min_stock: 2,
      stock: 12,
    })
    expect(created).toEqual({ id: 2, name: 'Resistor', stock: 12 })
    expect(store.items.map((item) => item.id)).toEqual([2, 1])
  })

  it('merges updated inventory items', async () => {
    apiMock.put.mockResolvedValueOnce({
      data: { id: 5, stock: 7, name: 'Fuse' },
    })

    const store = useInventoryStore()
    store.items = [{ id: 5, stock: 2, name: 'Fuse', category: 'power' }]

    const updated = await store.updateItem(5, {
      quantity: 7,
      category: 'power',
    })

    expect(apiMock.put).toHaveBeenCalledWith('/inventory/5', {
      category: 'power',
      stock: 7,
    })
    expect(updated).toEqual({ id: 5, stock: 7, name: 'Fuse' })
    expect(store.items).toEqual([{ id: 5, stock: 7, name: 'Fuse', category: 'power' }])
  })

  it('returns false when delete fails and keeps the item list', async () => {
    apiMock.delete.mockRejectedValueOnce(new Error('cannot delete'))

    const store = useInventoryStore()
    store.items = [{ id: 9, name: 'IC' }]

    await expect(store.deleteItem(9)).resolves.toBe(false)
    expect(store.items).toEqual([{ id: 9, name: 'IC' }])
  })

  it('removes inventory items on delete success', async () => {
    apiMock.delete.mockResolvedValueOnce({})

    const store = useInventoryStore()
    store.items = [{ id: 1 }, { id: 2 }]

    await expect(store.deleteItem(1)).resolves.toBe(true)
    expect(store.items).toEqual([{ id: 2 }])
  })

  it('syncs the store catalog and refreshes the current page', async () => {
    apiMock.post.mockResolvedValueOnce({
      data: {
        result: { matched: 4, created: 1 },
        status: { pending_images_count: 0 },
      },
    })
    apiMock.get.mockResolvedValueOnce({
      data: [{ id: 3, name: 'Potenciometro' }],
    })

    const store = useInventoryStore()
    const result = await store.syncCatalog()

    expect(apiMock.post).toHaveBeenCalledWith('/inventory/store-catalog/sync')
    expect(apiMock.get).toHaveBeenCalledWith('/inventory/?limit=20&page=1')
    expect(result).toEqual({
      result: { matched: 4, created: 1 },
      status: { pending_images_count: 0 },
    })
    expect(store.catalogStatus).toEqual({ pending_images_count: 0 })
    expect(store.items).toEqual([{ id: 3, name: 'Potenciometro' }])
    expect(store.syncingCatalog).toBe(false)
  })

  it('tracks import runs in the inventory store', async () => {
    apiMock.post.mockResolvedValueOnce({
      data: {
        run_id: 'run-123',
        status: 'started',
      },
    })

    const store = useInventoryStore()
    const result = await store.triggerImport()

    expect(apiMock.post).toHaveBeenCalledWith('/imports/run')
    expect(result).toEqual({
      run_id: 'run-123',
      status: 'started',
    })
    expect(store.lastRunId).toBe('run-123')
    expect(store.runStatus).toBe('started')
    expect(store.importing).toBe(false)
  })

  it('merges an item fetched by id into the loaded inventory', async () => {
    apiMock.get.mockResolvedValueOnce({
      data: { id: 9, name: 'VCA chip', stock: 2 },
    })

    const store = useInventoryStore()
    store.items = [{ id: 1, name: 'Capacitor' }]

    const item = await store.fetchItemById(9)

    expect(apiMock.get).toHaveBeenCalledWith('/inventory/9')
    expect(item).toEqual({ id: 9, name: 'VCA chip', stock: 2 })
    expect(store.items[0]).toEqual({ id: 9, name: 'VCA chip', stock: 2 })
  })
})
