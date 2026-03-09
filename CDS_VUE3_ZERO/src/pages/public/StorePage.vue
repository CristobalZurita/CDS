<template>
  <section class="store-page">
    <div class="store-shell">

      <header class="store-header">
        <div>
          <p class="eyebrow">Catálogo público</p>
          <h1>Tienda técnica de repuestos</h1>
          <p class="subtitle">
            Catálogo real con productos publicados desde inventario.
          </p>
        </div>
        <button class="btn-secondary" :disabled="loading" @click="loadCatalog">
          {{ loading ? 'Actualizando...' : 'Actualizar catálogo' }}
        </button>
      </header>

      <section class="store-toolbar">
        <label class="field">
          <span>Buscar</span>
          <input
            v-model.trim="searchTerm"
            type="text"
            placeholder="SKU, nombre o familia"
            data-testid="store-search-input"
          />
        </label>

        <label class="field">
          <span>Categoría</span>
          <select v-model="selectedCategory" data-testid="store-category-filter">
            <option value="">Todas</option>
            <option v-for="category in availableCategories" :key="category" :value="category">
              {{ category }}
            </option>
          </select>
        </label>

        <label class="field">
          <span>Disponibilidad</span>
          <select v-model="selectedAvailability" data-testid="store-availability-filter">
            <option value="all">Todo</option>
            <option value="sellable">Vendibles ahora</option>
            <option value="reserved">Reservados taller</option>
            <option value="out">Sin stock</option>
          </select>
        </label>

        <label class="field">
          <span>Despacho</span>
          <select v-model="selectedShippingKey" data-testid="store-shipping-select">
            <option v-for="option in shippingOptions" :key="option.key" :value="option.key">
              {{ option.name }}
            </option>
          </select>
        </label>
      </section>

      <div class="store-summary" data-testid="store-results-count">
        Mostrando {{ filteredProducts.length }} de {{ catalog.length }} productos.
      </div>

      <p v-if="error" class="store-error" data-testid="store-error">{{ error }}</p>

      <div class="store-layout">

        <!-- CATÁLOGO -->
        <section class="catalog-panel">
          <div v-if="loading" class="catalog-state" data-testid="store-loading">
            Cargando catálogo...
          </div>

          <div v-else-if="filteredProducts.length === 0" class="catalog-state" data-testid="store-empty">
            No hay productos disponibles para el filtro actual.
          </div>

          <div v-else class="products-grid">
            <article
              v-for="product in filteredProducts"
              :key="product.id"
              class="product-card"
              data-testid="store-product-card"
            >
              <div class="product-visual">
                <img
                  v-if="productImageSrc(product)"
                  :src="productImageSrc(product)"
                  :alt="product.name"
                  class="product-image"
                  loading="lazy"
                />
                <div v-else class="product-placeholder">
                  {{ String(product.sku || 'RP').slice(0, 3).toUpperCase() }}
                </div>

                <!-- Stock badges -->
                <span v-if="Number(product.available_stock || 0) <= 0" class="stock-badge stock-badge--warning">
                  Sin stock
                </span>
                <span v-else-if="Number(product.sellable_stock || 0) <= 0" class="stock-badge stock-badge--warning">
                  Reservado taller
                </span>
                <span v-else-if="product.is_low_stock" class="stock-badge stock-badge--info">
                  Últimas {{ product.sellable_stock }} {{ product.stock_unit || 'u' }}
                </span>
                <span v-else class="stock-badge">
                  {{ product.sellable_stock }} {{ product.stock_unit || 'u' }}
                </span>
              </div>

              <div class="product-body">
                <p class="product-family">{{ product.family || product.category || 'Repuesto' }}</p>
                <h2>{{ product.name }}</h2>
                <p class="product-sku">{{ product.sku }}</p>
                <p class="product-description">{{ describeProduct(product) }}</p>

                <div class="product-footer">
                  <div class="price-block">
                    <strong>{{ formatCurrency(product.price) }}</strong>
                    <small>{{ product.category || 'Sin categoría' }}</small>
                  </div>

                  <button
                    class="btn-add"
                    data-testid="store-add-to-cart"
                    :disabled="!canAddProduct(product)"
                    @click="addToCart(product)"
                  >
                    {{ addButtonLabel(product) }}
                  </button>
                </div>
              </div>
            </article>
          </div>
        </section>

        <!-- CARRITO SIDEBAR -->
        <aside class="cart-panel" data-testid="store-cart">
          <header class="cart-header">
            <div>
              <p class="eyebrow">Lista técnica</p>
              <h2>Resumen actual</h2>
            </div>
            <span class="cart-count">{{ totals.itemsCount }} items</span>
          </header>

          <div v-if="cartItems.length === 0" class="cart-empty" data-testid="store-cart-empty">
            La lista está vacía. Agrega repuestos del catálogo.
          </div>

          <div v-else class="cart-list">
            <article
              v-for="item in cartItems"
              :key="item.id"
              class="cart-item"
              data-testid="store-cart-item"
            >
              <div class="cart-item-copy">
                <strong>{{ item.name }}</strong>
                <span>{{ item.sku }}</span>
                <small>{{ formatLinePrice(item.price) }} c/u</small>
              </div>

              <div class="cart-item-actions">
                <button class="qty-btn" @click="changeQty(item.id, -1)">−</button>
                <span class="qty-value">{{ item.qty }}</span>
                <button
                  class="qty-btn"
                  :disabled="!canAddProduct(item)"
                  @click="changeQty(item.id, 1)"
                >+</button>
                <button class="remove-btn" @click="removeFromCart(item.id)">Quitar</button>
              </div>
            </article>
          </div>

          <div class="cart-summary">
            <div class="summary-row">
              <span>Subtotal</span>
              <strong>{{ formatSummaryAmount(totals.productsSubtotal) }}</strong>
            </div>
            <div class="summary-row">
              <span>Despacho</span>
              <strong>{{ currentShipping.name }}</strong>
            </div>
            <div class="summary-row">
              <span>Costo despacho</span>
              <strong>{{ formatCurrency(totals.shippingPrice) }}</strong>
            </div>
            <div class="summary-row summary-row--total">
              <span>Total</span>
              <strong>{{ formatSummaryAmount(totals.grandTotal) }}</strong>
            </div>
          </div>

          <button
            class="btn-checkout"
            data-testid="store-checkout"
            :disabled="cartItems.length === 0 || shopCart.submitting"
            @click="submitCheckout"
          >
            {{ checkoutLabel }}
          </button>

          <p class="cart-note">
            El carro global queda disponible al navegar por todo el sitio. Si inicias sesión como
            cliente, esta lista se convierte en una solicitud real.
          </p>
        </aside>

      </div>
    </div>
  </section>
</template>

<script setup>
import { useStorePage } from '@new/composables/useStorePage'

const {
  catalog,
  loading,
  error,
  searchTerm,
  selectedCategory,
  selectedAvailability,
  selectedShippingKey,
  shippingOptions,
  availableCategories,
  filteredProducts,
  cartItems,
  currentShipping,
  totals,
  checkoutLabel,
  shopCart,
  loadCatalog,
  formatCurrency,
  formatLinePrice,
  formatSummaryAmount,
  productImageSrc,
  describeProduct,
  canAddProduct,
  addButtonLabel,
  addToCart,
  removeFromCart,
  changeQty,
  submitCheckout,
} = useStorePage()
</script>

<style scoped>
.store-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(236, 107, 0, 0.12), transparent 30%),
    linear-gradient(180deg, #f8f9f6 0%, #ece9df 100%);
  padding: var(--cds-space-xl) var(--cds-space-md) var(--cds-space-2xl);
}

.store-shell {
  max-width: min(1440px, 98vw);
  margin: 0 auto;
  display: grid;
  gap: var(--cds-space-lg);
}

/* ─── HEADER ─── */
.store-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--cds-space-lg);
  padding: var(--cds-space-xl);
  border-radius: var(--cds-radius-lg);
  border: 1px solid var(--cds-border-soft);
  background: rgba(255, 255, 255, 0.88);
  box-shadow: var(--cds-shadow-md);
}

.eyebrow {
  margin: 0 0 var(--cds-space-2xs);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: var(--cds-font-bold);
  color: var(--cds-primary);
  font-size: 0.85rem;
}

.store-header h1 {
  margin: 0;
  font-size: clamp(2rem, 3.2vw, 3rem);
  line-height: 1.1;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.subtitle {
  margin: var(--cds-space-sm) 0 0;
  max-width: 62ch;
  color: var(--cds-text-muted);
  font-size: 1rem;
}

/* ─── TOOLBAR ─── */
.store-toolbar {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--cds-space-md);
  padding: var(--cds-space-lg);
  border-radius: var(--cds-radius-lg);
  border: 1px solid var(--cds-border-soft);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: var(--cds-shadow-sm);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--cds-space-2xs);
}

.field span {
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: var(--cds-font-bold);
  color: color-mix(in srgb, var(--cds-dark) 82%, white);
}

.field input,
.field select {
  min-height: 44px;
  padding: 0.65rem 0.8rem;
  border: 1px solid color-mix(in srgb, var(--cds-dark) 16%, white);
  border-radius: var(--cds-radius-sm);
  background: rgba(255, 255, 255, 0.96);
  font-size: var(--cds-text-base);
}

/* ─── SUMMARY + ERROR ─── */
.store-summary {
  padding: var(--cds-space-sm) var(--cds-space-md);
  border-radius: var(--cds-radius-md);
  border: 1px solid color-mix(in srgb, var(--cds-dark) 14%, white);
  background: rgba(255, 255, 255, 0.86);
  box-shadow: var(--cds-shadow-sm);
  font-size: 1rem;
}

.store-error {
  margin: 0;
  border: 1px solid #f4c7c3;
  background: #fef3f2;
  color: #b42318;
  border-radius: var(--cds-radius-sm);
  padding: var(--cds-space-sm);
}

/* ─── LAYOUT 2 COLUMNAS ─── */
.store-layout {
  display: grid;
  gap: var(--cds-space-md);
  grid-template-columns: minmax(0, 1.7fr) minmax(300px, 0.95fr);
  align-items: start;
}

/* ─── CATALOG ─── */
.catalog-state {
  min-height: 220px;
  display: grid;
  place-items: center;
  text-align: center;
  color: var(--cds-dark);
  opacity: 0.72;
}

.products-grid {
  display: grid;
  gap: var(--cds-space-md);
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
}

.product-card {
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: var(--cds-radius-lg);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.98);
  box-shadow: var(--cds-shadow-sm);
}

.product-visual {
  position: relative;
  min-height: 180px;
  display: grid;
  place-items: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background: linear-gradient(135deg, rgba(236, 107, 0, 0.10), #edf0e8);
}

.product-image {
  max-width: 100%;
  max-height: 180px;
  object-fit: contain;
}

.product-placeholder {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(236, 107, 0, 0.12);
  color: var(--cds-primary);
  font-weight: 800;
  letter-spacing: 0.08em;
  font-size: 1rem;
}

.stock-badge {
  position: absolute;
  top: 0.6rem;
  left: 0.6rem;
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0.15rem 0.6rem;
  border-radius: 999px;
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: 0.78rem;
  font-weight: 700;
}

.stock-badge--warning {
  background: #e0a800;
  color: var(--cds-dark);
}

.stock-badge--info {
  background: #3b82f6;
  color: var(--cds-white);
}

.product-body {
  padding: var(--cds-space-md);
  display: flex;
  flex-direction: column;
  gap: var(--cds-space-xs);
  flex: 1;
}

.product-family {
  margin: 0;
  color: var(--cds-primary);
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.product-body h2 {
  margin: 0;
  font-size: 1rem;
  line-height: 1.3;
  color: var(--cds-dark);
}

.product-sku {
  margin: 0;
  color: var(--cds-text-muted);
  font-size: 0.85rem;
}

.product-description {
  margin: 0;
  font-size: 0.9rem;
  color: var(--cds-text-muted);
  line-height: 1.5;
}

.product-footer {
  margin-top: auto;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--cds-space-sm);
  flex-wrap: wrap;
}

.price-block {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.price-block strong {
  font-size: var(--cds-text-lg);
  font-weight: 700;
  color: var(--cds-dark);
}

.price-block small {
  font-size: 0.8rem;
  color: var(--cds-text-muted);
}

.btn-add {
  min-height: 38px;
  padding: 0.45rem 0.85rem;
  border-radius: var(--cds-radius-sm);
  border: none;
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s, transform 0.15s;
}

.btn-add:hover:not(:disabled) {
  background: color-mix(in srgb, var(--cds-primary) 85%, black);
  transform: translateY(-1px);
}

.btn-add:disabled {
  opacity: 0.55;
  cursor: default;
}

/* ─── CART SIDEBAR ─── */
.cart-panel {
  position: sticky;
  top: calc(72px + var(--cds-space-md));
  display: flex;
  flex-direction: column;
  gap: var(--cds-space-md);
  padding: var(--cds-space-lg);
  border-radius: var(--cds-radius-lg);
  border: 1px solid var(--cds-border-soft);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: var(--cds-shadow-md);
  max-height: calc(100vh - 100px);
  overflow-y: auto;
}

.cart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.cart-header h2 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--cds-dark);
}

.cart-count {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0.2rem 0.75rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--cds-primary) 16%, white);
  color: var(--cds-dark);
  font-size: 0.9rem;
  font-weight: 700;
}

.cart-empty {
  min-height: 120px;
  display: grid;
  place-items: center;
  text-align: center;
  color: var(--cds-dark);
  opacity: 0.65;
  font-size: 0.95rem;
}

.cart-list {
  display: flex;
  flex-direction: column;
  gap: var(--cds-space-sm);
}

.cart-item {
  display: flex;
  flex-direction: column;
  gap: var(--cds-space-xs);
  padding: 0.75rem;
  border: 1px solid color-mix(in srgb, var(--cds-dark) 12%, white);
  border-radius: var(--cds-radius-sm);
}

.cart-item-copy {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.cart-item-copy strong {
  font-size: 0.9rem;
  color: var(--cds-dark);
}

.cart-item-copy span,
.cart-item-copy small {
  font-size: 0.82rem;
  color: var(--cds-text-muted);
}

.cart-item-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.qty-btn {
  width: 34px;
  height: 34px;
  border: 1px solid color-mix(in srgb, var(--cds-dark) 18%, white);
  border-radius: var(--cds-radius-sm);
  background: white;
  color: var(--cds-dark);
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.qty-btn:disabled {
  opacity: 0.5;
}

.qty-value {
  min-width: 28px;
  text-align: center;
  font-weight: 700;
  font-size: 1rem;
  color: var(--cds-dark);
}

.remove-btn {
  margin-left: auto;
  padding: 0.25rem 0.6rem;
  border: 1px solid #f87171;
  border-radius: var(--cds-radius-sm);
  background: transparent;
  color: #ef4444;
  font-size: 0.8rem;
  cursor: pointer;
}

.cart-summary {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  padding-top: var(--cds-space-sm);
  border-top: 1px solid color-mix(in srgb, var(--cds-dark) 12%, white);
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: var(--cds-dark);
}

.summary-row--total {
  padding-top: var(--cds-space-xs);
  border-top: 1px solid color-mix(in srgb, var(--cds-dark) 12%, white);
  font-size: 1rem;
}

.btn-checkout {
  width: 100%;
  min-height: 44px;
  padding: 0.7rem 1rem;
  border-radius: var(--cds-radius-sm);
  border: none;
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-checkout:hover:not(:disabled) {
  background: color-mix(in srgb, var(--cds-primary) 85%, black);
}

.btn-checkout:disabled {
  opacity: 0.55;
  cursor: default;
}

.cart-note {
  margin: 0;
  font-size: 0.82rem;
  color: var(--cds-text-muted);
  line-height: 1.5;
}

.btn-secondary {
  min-height: 44px;
  padding: 0.7rem 1.1rem;
  border-radius: 999px;
  font-size: 0.95rem;
  font-weight: var(--cds-font-semibold);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid color-mix(in srgb, var(--cds-dark) 18%, white);
  background: rgba(255, 255, 255, 0.9);
  color: color-mix(in srgb, var(--cds-dark) 92%, white);
  cursor: pointer;
}

/* ─── RESPONSIVE ─── */
@media (max-width: 1100px) {
  .store-toolbar {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .store-layout {
    grid-template-columns: 1fr;
  }
  .cart-panel {
    position: static;
    max-height: none;
  }
}

@media (max-width: 600px) {
  .store-page {
    padding: var(--cds-space-lg) var(--cds-space-sm) var(--cds-space-xl);
  }
  .store-toolbar {
    grid-template-columns: 1fr;
  }
  .products-grid {
    grid-template-columns: 1fr;
  }
}
</style>
