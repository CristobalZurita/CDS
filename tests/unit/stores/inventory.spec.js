import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { api } from '../../../src/services/api.js'
import { useInventoryStore } from '../../../src/stores/inventory.js'

vi.mock('../../../src/services/api.js', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

describe('inventory store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    api.get.mockReset()
    api.post.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
  })

  it('fetchItems sets items and updates loading', async () => {
    const fakeItems = [{ id: 1, name: 'A' }]
    api.get.mockResolvedValue({ data: fakeItems })

    const store = useInventoryStore()
    await store.fetchItems(1, 20)

    expect(store.items).toEqual(fakeItems)
    expect(store.loading).toBe(false)
  })

  it('createItem normalizes quantity -> stock and sends POST body', async () => {
    api.post.mockResolvedValue({ data: { id: 123, name: 'X', stock: 5 } })
    api.get.mockResolvedValue({ data: [{ id: 1, name: 'X' }] })

    const store = useInventoryStore()
    const created = await store.createItem({ name: 'X', quantity: 5 })

    expect(created.stock).toBe(5)

    expect(api.post).toHaveBeenCalledTimes(1)
    expect(api.post).toHaveBeenCalledWith('/inventory', { name: 'X', stock: 5 })
  })

  it('updateItem normalizes quantity -> stock and sends PUT', async () => {
    api.put.mockResolvedValue({ data: { id: 42, name: 'Y', stock: 7 } })
    api.get.mockResolvedValue({ data: [{ id: 1, name: 'Y' }] })

    const store = useInventoryStore()
    const updated = await store.updateItem(42, { name: 'Y', quantity: 7 })
    expect(updated.stock).toBe(7)
    expect(api.put).toHaveBeenCalledTimes(1)
    expect(api.put).toHaveBeenCalledWith('/inventory/42', { name: 'Y', stock: 7 })
  })

  it('deleteItem calls DELETE and refreshes list', async () => {
    api.delete.mockResolvedValue({ data: {} })
    api.get.mockResolvedValue({ data: [{ id: 1 }] })

    const store = useInventoryStore()
    const ok = await store.deleteItem(99)
    expect(ok).toBe(true)
    expect(api.delete).toHaveBeenCalledWith('/inventory/99')
  })
})
