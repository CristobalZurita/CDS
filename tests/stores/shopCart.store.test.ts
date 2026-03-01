import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useShopCartStore } from '@/stores/shopCart'

const { postMock } = vi.hoisted(() => ({
  postMock: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  api: {
    post: postMock,
  },
}))

describe('shop cart store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    postMock.mockReset()
    window.localStorage.clear()
  })

  it('syncs a persisted cart snapshot against the live catalog', () => {
    const store = useShopCartStore()
    store.replaceItems([{ id: 12, qty: 3 }])

    store.syncCatalog([
      {
        id: 12,
        name: 'Resistencia 10K',
        sku: 'RES-10K',
        price: 120,
        sellable_stock: 2,
        available_stock: 6,
        min_stock: 4,
        store_visible: true,
        enabled: true,
      },
    ])

    expect(store.items).toHaveLength(1)
    expect(store.items[0].qty).toBe(2)
    expect(store.items[0].sku).toBe('RES-10K')
  })

  it('creates a real purchase request payload and clears the cart after submit', async () => {
    const store = useShopCartStore()
    store.hydrate()

    store.addProduct({
      id: 50,
      name: 'Capacitor 100uF',
      sku: 'CAP-100UF',
      price: 890,
      sellable_stock: 8,
      available_stock: 10,
      min_stock: 2,
      store_visible: true,
      enabled: true,
    })
    store.setShippingKey('manual')

    postMock.mockResolvedValue({
      data: {
        request: { id: 77 },
      },
    })

    const request = await store.submitRequest('Cliente necesita envío')

    expect(postMock).toHaveBeenCalledWith('/client/store/purchase-requests', {
      shipping_key: 'manual',
      shipping_label: 'Despacho coordinado manualmente',
      shipping_price: 0,
      notes: 'Cliente necesita envío',
      items: [
        {
          product_id: 50,
          sku: 'CAP-100UF',
          name: 'Capacitor 100uF',
          quantity: 1,
          unit_price: 890,
        },
      ],
    })
    expect(request?.id).toBe(77)
    expect(store.items).toHaveLength(0)
  })
})
