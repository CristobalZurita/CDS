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
})
