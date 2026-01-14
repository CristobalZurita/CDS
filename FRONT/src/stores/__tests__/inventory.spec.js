import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useInventoryStore } from '../inventory'

describe('inventory store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    global.fetch = vi.fn()
    // simple localStorage mock
    global.localStorage = {
      _data: {},
      getItem(key) { return this._data[key] || null },
      setItem(key, v) { this._data[key] = String(v) },
      clear() { this._data = {} }
    }
  })

  it('fetchItems sets items on success', async () => {
    const items = [{ id: 1, name: 'A' }]
    fetch.mockResolvedValueOnce({ ok: true, json: async () => items })
    const store = useInventoryStore()
    await store.fetchItems()
    expect(store.items).toEqual(items)
    expect(store.loading).toBe(false)
  })

  it('fetchItems clears items on non-ok response', async () => {
    fetch.mockResolvedValueOnce({ ok: false, status: 500 })
    const store = useInventoryStore()
    // pre-populate
    store.items = [{ id: 99 }]
    await store.fetchItems()
    expect(store.items).toEqual([])
    expect(store.loading).toBe(false)
  })

  it('createItem normalizes quantity -> stock and calls fetchItems', async () => {
    // Sequence: POST /api/v1/items -> returns created, then fetchItems -> returns list
    const created = { id: 10, name: 'X', stock: 5 }
    fetch
      .mockResolvedValueOnce({ ok: true, json: async () => created })
      .mockResolvedValueOnce({ ok: true, json: async () => [created] })

    const store = useInventoryStore()
    const payload = { name: 'X', quantity: 5 }
    const res = await store.createItem(payload)
    expect(res).toEqual(created)
    // Inspect the POST call body to ensure normalization
    const postCall = fetch.mock.calls[0]
    const body = JSON.parse(postCall[1].body)
    expect(body.stock).toBe(5)
    expect(body.quantity).toBeUndefined()
    expect(store.items).toEqual([created])
  })

  it('updateItem normalizes quantity -> stock and refreshes list', async () => {
    const updated = { id: 11, name: 'Y', stock: 7 }
    fetch
      .mockResolvedValueOnce({ ok: true, json: async () => updated })
      .mockResolvedValueOnce({ ok: true, json: async () => [updated] })

    const store = useInventoryStore()
    const payload = { name: 'Y', quantity: 7 }
    const res = await store.updateItem(11, payload)
    expect(res).toEqual(updated)
    const putCall = fetch.mock.calls[0]
    const body = JSON.parse(putCall[1].body)
    expect(body.stock).toBe(7)
    expect(body.quantity).toBeUndefined()
    expect(store.items).toEqual([updated])
  })

  it('deleteItem returns true on success and refreshes', async () => {
    fetch
      .mockResolvedValueOnce({ ok: true, text: async () => '' })
      .mockResolvedValueOnce({ ok: true, json: async () => [] })

    const store = useInventoryStore()
    const res = await store.deleteItem(99)
    expect(res).toBe(true)
    expect(store.items).toEqual([])
  })
})
