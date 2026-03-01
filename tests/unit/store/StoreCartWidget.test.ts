import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const routerPush = vi.hoisted(() => vi.fn())
const routeState = vi.hoisted(() => ({
  path: '/dashboard',
  fullPath: '/dashboard',
}))
const authStoreMock = vi.hoisted(() => ({
  isAdmin: false,
  isAuthenticated: false,
  checkAuth: vi.fn(),
}))
const cartMock = vi.hoisted(() => ({
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
  ],
  submitting: false,
  hydrate: vi.fn(),
  canAddProduct: vi.fn(),
  changeQty: vi.fn(),
  removeItem: vi.fn(),
  setShippingKey: vi.fn(),
  submitRequest: vi.fn(),
}))
const toastMock = vi.hoisted(() => ({
  showError: vi.fn(),
  showInfo: vi.fn(),
  showSuccess: vi.fn(),
  showWarning: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeState,
  useRouter: () => ({ push: routerPush }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
}))

vi.mock('@/stores/shopCart', () => ({
  useShopCartStore: () => cartMock,
}))

vi.mock('@/services/toastService', () => toastMock)

import StoreCartWidget from '@/vue/components/widgets/StoreCartWidget.vue'

describe('StoreCartWidget', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    routeState.path = '/dashboard'
    routeState.fullPath = '/dashboard'
    authStoreMock.isAdmin = false
    authStoreMock.isAuthenticated = false
    authStoreMock.checkAuth.mockResolvedValue({})
    cartMock.items = [
      { id: 1, name: 'Resistencia 10K', sku: 'RES-10K', price: 120, qty: 1 },
    ]
    cartMock.totals = {
      itemsCount: 1,
      productsSubtotal: 120,
      shippingPrice: 0,
      grandTotal: 120,
      hasQuotedAmount: true,
    }
    cartMock.currentShipping = { key: 'pickup', name: 'Retiro en taller', price: 0 }
    cartMock.selectedShippingKey = 'pickup'
    cartMock.submitting = false
    cartMock.hydrate.mockImplementation(() => {})
    cartMock.canAddProduct.mockReturnValue(true)
    cartMock.changeQty.mockImplementation(() => {})
    cartMock.removeItem.mockImplementation(() => {})
    cartMock.setShippingKey.mockImplementation(() => {})
    cartMock.submitRequest.mockResolvedValue({ id: 18 })
    window.localStorage.getItem = vi.fn(() => null)
  })

  it('renders across the public site and redirects guests to login on checkout', async () => {
    const wrapper = mount(StoreCartWidget)
    await flushPromises()

    expect(wrapper.find('[data-testid="global-cart-trigger"]').exists()).toBe(true)

    await wrapper.get('[data-testid="global-cart-trigger"]').trigger('click')
    await wrapper.get('[data-testid="global-cart-checkout"]').trigger('click')

    expect(toastMock.showInfo).toHaveBeenCalledWith('Inicia sesión para convertir el carrito en una solicitud real.')
    expect(routerPush).toHaveBeenCalledWith({ name: 'login', query: { redirect: '/dashboard' } })
  })

  it('stays hidden inside admin routes', () => {
    routeState.path = '/admin/inventory'
    routeState.fullPath = '/admin/inventory'

    const wrapper = mount(StoreCartWidget)

    expect(wrapper.find('[data-testid="global-cart-trigger"]').exists()).toBe(false)
  })
})
