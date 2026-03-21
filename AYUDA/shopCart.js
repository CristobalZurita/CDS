/**
 * stores/shopCart.js
 * Reemplaza el shopCart.js existente.
 * Pinia store — carrito persistente con localStorage.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useShopCartStore = defineStore('shopCart', () => {
  // ── State ────────────────────────────────────────────────
  const items    = ref(_load())
  const isOpen   = ref(false)
  const lastAdded = ref(null)   // para animación de feedback

  // ── Getters ──────────────────────────────────────────────
  const count = computed(() =>
    items.value.reduce((s, i) => s + i.qty, 0)
  )

  const subtotal = computed(() =>
    items.value.reduce((s, i) => s + i.price * i.qty, 0)
  )

  const isEmpty = computed(() => items.value.length === 0)

  const itemMap = computed(() =>
    Object.fromEntries(items.value.map(i => [i.id, i]))
  )

  // ── Actions ──────────────────────────────────────────────
  function addItem(product, qty = 1) {
    const existing = items.value.find(i => i.id === product.id)
    if (existing) {
      existing.qty = Math.min(existing.qty + qty, product.stock ?? 999)
    } else {
      items.value.push({
        id:         product.id,
        sku:        product.sku,
        name:       product.name,
        price:      product.price,
        image_url:  product.image_url ?? null,
        stock:      product.stock ?? 999,
        qty,
      })
    }
    lastAdded.value = product.id
    setTimeout(() => { lastAdded.value = null }, 1200)
    _persist()
    isOpen.value = true
  }

  function removeItem(productId) {
    items.value = items.value.filter(i => i.id !== productId)
    _persist()
  }

  function setQty(productId, qty) {
    const item = items.value.find(i => i.id === productId)
    if (!item) return
    if (qty <= 0) return removeItem(productId)
    item.qty = Math.min(qty, item.stock)
    _persist()
  }

  function increment(productId) {
    const item = items.value.find(i => i.id === productId)
    if (item && item.qty < item.stock) {
      item.qty++
      _persist()
    }
  }

  function decrement(productId) {
    const item = items.value.find(i => i.id === productId)
    if (!item) return
    if (item.qty <= 1) return removeItem(productId)
    item.qty--
    _persist()
  }

  function clear() {
    items.value = []
    _persist()
  }

  function openCart()  { isOpen.value = true  }
  function closeCart() { isOpen.value = false }
  function toggleCart() { isOpen.value = !isOpen.value }

  function getQty(productId) {
    return itemMap.value[productId]?.qty ?? 0
  }

  // ── Private ──────────────────────────────────────────────
  function _persist() {
    try {
      localStorage.setItem('cds_cart', JSON.stringify(items.value))
    } catch { /* quota exceeded — silencioso */ }
  }

  function _load() {
    try {
      return JSON.parse(localStorage.getItem('cds_cart') ?? '[]')
    } catch {
      return []
    }
  }

  return {
    items, isOpen, lastAdded,
    count, subtotal, isEmpty, itemMap,
    addItem, removeItem, setQty, increment, decrement,
    clear, openCart, closeCart, toggleCart, getQty,
  }
})
