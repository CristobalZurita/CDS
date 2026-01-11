import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useInventoryStore } from '../../../src/stores/inventory.js'

describe('inventory store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  afterEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
  })

  it('fetchItems sets items and updates loading', async () => {
    const fakeItems = [{ id: 1, name: 'A' }]
    global.fetch = vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve(fakeItems) }))

    const store = useInventoryStore()
    await store.fetchItems(1, 20)

    expect(store.items).toEqual(fakeItems)
    expect(store.loading).toBe(false)
  })

  it('createItem normalizes quantity -> stock and sends POST body', async () => {
    // Mock POST response then list refresh
    global.fetch = vi.fn((url, opts) => {
      if (url.endsWith('/api/v1/items') && opts && opts.method === 'POST') {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ id: 123, ...JSON.parse(opts.body) }) })
      }
      if (url.startsWith('/api/v1/items')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve([{ id: 1, name: 'X' }]) })
      }
      return Promise.resolve({ ok: false, status: 404, text: () => Promise.resolve('not found') })
    })

    const store = useInventoryStore()
    const created = await store.createItem({ name: 'X', quantity: 5 })

    // verify created response contains stock
    expect(created.stock).toBe(5)

    // inspect fetch calls to see the body sent
    const postCall = global.fetch.mock.calls.find((c) => c[1] && c[1].method === 'POST')
    const sentBody = JSON.parse(postCall[1].body)
    expect(sentBody.stock).toBe(5)
    expect(sentBody.quantity).toBeUndefined()
  })

  it('updateItem normalizes quantity -> stock and sends PUT', async () => {
    global.fetch = vi.fn((url, opts) => {
      if (url.endsWith('/api/v1/items/42') && opts && opts.method === 'PUT') {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ id: 42, ...JSON.parse(opts.body) }) })
      }
      if (url.startsWith('/api/v1/items')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve([{ id: 1 }]) })
      }
      return Promise.resolve({ ok: false, status: 404, text: () => Promise.resolve('not found') })
    })

    const store = useInventoryStore()
    const updated = await store.updateItem(42, { name: 'Y', quantity: 7 })
    expect(updated.stock).toBe(7)
    const putCall = global.fetch.mock.calls.find((c) => c[1] && c[1].method === 'PUT')
    const sent = JSON.parse(putCall[1].body)
    expect(sent.stock).toBe(7)
    expect(sent.quantity).toBeUndefined()
  })

  it('deleteItem calls DELETE and refreshes list', async () => {
    let deleted = false
    global.fetch = vi.fn((url, opts) => {
      if (url.endsWith('/api/v1/items/99') && opts && opts.method === 'DELETE') {
        deleted = true
        return Promise.resolve({ ok: true, text: () => Promise.resolve('') })
      }
      if (url.startsWith('/api/v1/items')) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve([{ id: 1 }]) })
      }
      return Promise.resolve({ ok: false, status: 404, text: () => Promise.resolve('not found') })
    })

    const store = useInventoryStore()
    const ok = await store.deleteItem(99)
    expect(ok).toBe(true)
    expect(deleted).toBe(true)
  })
})
