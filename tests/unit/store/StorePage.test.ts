import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const routerPush = vi.hoisted(() => vi.fn())
const authStoreMock = vi.hoisted(() => ({
  isAdmin: false,
  isAuthenticated: false,
}))
const shopCartMock = vi.hoisted(() => ({
  items: [],
  totals: {
    itemsCount: 0,
    productsSubtotal: 0,
    shippingPrice: 0,
    grandTotal: 0,
    hasQuotedAmount: false,
  },
  currentShipping: { key: 'pickup', name: 'Retiro en taller', price: 0 },
  selectedShippingKey: 'pickup',
  shippingOptions: [
    { key: 'pickup', name: 'Retiro en taller', price: 0 },
    { key: 'manual', name: 'Despacho coordinado manualmente', price: 0 },
  ],
  submitting: false,
  hydrate: vi.fn(),
  setShippingKey: vi.fn(),
  syncCatalog: vi.fn(),
  canAddProduct: vi.fn(),
  addProduct: vi.fn(),
  removeItem: vi.fn(),
  changeQty: vi.fn(),
  submitRequest: vi.fn(),
}))
const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
}))
const toastMock = vi.hoisted(() => ({
  showError: vi.fn(),
  showInfo: vi.fn(),
  showSuccess: vi.fn(),
  showWarning: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: routerPush }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
}))

vi.mock('@/stores/shopCart', () => ({
  useShopCartStore: () => shopCartMock,
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

vi.mock('@/services/toastService', () => toastMock)

import StorePage from '@/vue/content/pages/StorePage.vue'

const catalogRows = [
  {
    id: 10,
    name: 'Capacitor 100uF',
    sku: 'CAP-100UF',
    price: 890,
    category: 'Capacitores',
    family: 'Capacitores',
    description: 'Electrolitico',
    sellable_stock: 3,
    available_stock: 5,
    min_stock: 2,
    store_visible: true,
    enabled: true,
    is_low_stock: false,
  },
]

describe('StorePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    authStoreMock.isAdmin = false
    authStoreMock.isAuthenticated = false
    shopCartMock.items = []
    shopCartMock.totals = {
      itemsCount: 1,
      productsSubtotal: 890,
      shippingPrice: 0,
      grandTotal: 890,
      hasQuotedAmount: true,
    }
    shopCartMock.currentShipping = { key: 'pickup', name: 'Retiro en taller', price: 0 }
    shopCartMock.selectedShippingKey = 'pickup'
    shopCartMock.submitting = false
    shopCartMock.hydrate.mockImplementation(() => {})
    shopCartMock.syncCatalog.mockImplementation(() => {})
    shopCartMock.canAddProduct.mockReturnValue(true)
    shopCartMock.addProduct.mockReturnValue(true)
    shopCartMock.removeItem.mockImplementation(() => {})
    shopCartMock.changeQty.mockImplementation(() => {})
    shopCartMock.submitRequest.mockResolvedValue({ id: 91 })
    apiMock.get.mockResolvedValue({ data: catalogRows })
  })

  it('loads the public catalog and adds an item to the cart', async () => {
    const wrapper = mount(StorePage)
    await flushPromises()

    expect(shopCartMock.hydrate).toHaveBeenCalled()
    expect(apiMock.get).toHaveBeenCalledWith('/inventory/public/', {
      params: {
        limit: 500,
        enabled_only: true,
        in_stock_only: false,
      },
    })
    expect(shopCartMock.syncCatalog).toHaveBeenCalledWith(catalogRows)

    await wrapper.get('[data-testid="store-add-to-cart"]').trigger('click')

    expect(shopCartMock.addProduct).toHaveBeenCalledWith(expect.objectContaining({ id: 10 }))
    expect(toastMock.showSuccess).toHaveBeenCalledWith('Capacitor 100uF agregado al carrito.')
  })

  it('redirects unauthenticated users to login when they try to checkout', async () => {
    shopCartMock.items = [{ id: 10, qty: 1, name: 'Capacitor 100uF', sku: 'CAP-100UF', price: 890 }]

    const wrapper = mount(StorePage)
    await flushPromises()
    await wrapper.get('[data-testid="store-checkout"]').trigger('click')

    expect(toastMock.showInfo).toHaveBeenCalledWith('Inicia sesión para convertir esta lista en una solicitud real.')
    expect(routerPush).toHaveBeenCalledWith({ name: 'login', query: { redirect: '/tienda' } })
  })

  it('submits a real purchase request for authenticated clients', async () => {
    authStoreMock.isAuthenticated = true
    shopCartMock.items = [{ id: 10, qty: 1, name: 'Capacitor 100uF', sku: 'CAP-100UF', price: 890 }]

    const wrapper = mount(StorePage)
    await flushPromises()
    await wrapper.get('[data-testid="store-checkout"]').trigger('click')
    await flushPromises()

    expect(shopCartMock.submitRequest).toHaveBeenCalled()
    expect(toastMock.showSuccess).toHaveBeenCalledWith('Solicitud #91 enviada correctamente.')
    expect(routerPush).toHaveBeenCalledWith('/ot-payments')
  })
})
