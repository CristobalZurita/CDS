<template>
  <section class="store-page">
    <div class="store-shell">

      <header class="store-header">
        <div>
          <p class="eyebrow">Catálogo público</p>
          <h1>Tienda técnica de repuestos</h1>
     
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


      <p v-if="error" class="store-error" data-testid="store-error">{{ error }}</p>

      <!-- CATÁLOGO — ancho completo -->
      <section class="catalog-panel">
        <div v-if="loading" class="catalog-state" data-testid="store-loading">
          Cargando catálogo...
        </div>

        <div v-else-if="filteredProducts.length === 0" class="catalog-state" data-testid="store-empty">
          No hay productos disponibles para el filtro actual.
        </div>

        <div v-else class="products-grid">
          <StoreProductCard
            v-for="product in filteredProducts"
            :key="product.id"
            :product="product"
            :image-src="productImageSrc(product)"
            :description="describeProduct(product)"
            :price-label="formatCurrency(product.price)"
            :can-add="canAddProduct(product)"
            :button-label="addButtonLabel(product)"
            @add="addToCart"
          />
        </div>
      </section>

    </div><!-- /store-shell -->

    <StoreCartDrawer
      :open="cartOpen"
      :items="cartItems"
      :totals="totals"
      :current-shipping="currentShipping"
      :checkout-label="checkoutLabel"
      :submitting="cartSubmitting"
      :can-add-product="canAddProduct"
      @close="closeCartDrawer"
      @change-qty="onDrawerChangeQty"
      @remove="removeFromCart"
      @checkout="submitCheckout"
    />

  </section>
</template>

<script setup>
import StoreCartDrawer from '@/components/business/StoreCartDrawer.vue'
import StoreProductCard from '@/components/business/StoreProductCard.vue'
import { useStorePage } from '@/composables/useStorePage'

const {
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
  cartOpen,
  cartSubmitting,
  currentShipping,
  totals,
  checkoutLabel,
  loadCatalog,
  formatCurrency,
  productImageSrc,
  describeProduct,
  canAddProduct,
  addButtonLabel,
  addToCart,
  removeFromCart,
  closeCartDrawer,
  onDrawerChangeQty,
  submitCheckout,
} = useStorePage()
</script>

<style scoped>
.store-page {
  min-height: 100vh;
  background: var(--cds-background-color);
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
  border: 1px solid var(--cds-border-card);
  background: var(--cds-white);
  box-shadow: var(--cds-shadow-md);
}

.eyebrow {
  margin: 0 0 var(--cds-space-2xs);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: var(--cds-font-bold);
  color: var(--cds-primary);
  font-size: var(--cds-text-sm);
}

.store-header h1 {
  margin: 0;
  font-size: clamp(2rem, 3.2vw, 3rem);
  line-height: 1.1;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

/* ─── TOOLBAR ─── */
.store-toolbar {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--cds-space-md);
  padding: var(--cds-space-lg);
  border-radius: var(--cds-radius-lg);
  border: 1px solid var(--cds-border-card);
  background: var(--cds-white);
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
  color: var(--cds-dark);
}

.field input,
.field select {
  min-height: 44px;
  padding: 0.65rem 0.8rem;
  border: 1px solid var(--cds-border-input);
  border-radius: var(--cds-radius-sm);
  background: var(--cds-white);
  font-size: var(--cds-text-base);
}

.store-error {
  margin: 0;
  border: 1px solid var(--cds-invalid-border);
  background: var(--cds-invalid-bg);
  color: var(--cds-invalid-text);
  border-radius: var(--cds-radius-sm);
  padding: var(--cds-space-sm);
}

/* ─── CATALOG — full width ─── */
.catalog-panel {
  width: 100%;
}

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
.btn-secondary {
  min-height: 44px;
  padding: 0.7rem 1.1rem;
  border-radius: var(--cds-radius-pill);
  font-size: 0.95rem;
  font-weight: var(--cds-font-semibold);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--cds-border-card);
  background: var(--cds-white);
  color: var(--cds-dark);
  cursor: pointer;
}

/* ─── RESPONSIVE ─── */
@media (max-width: 1100px) {
  .store-toolbar {
    grid-template-columns: repeat(2, minmax(0, 1fr));
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
  .cart-toggle-label {
    display: none;
  }
}
</style>
