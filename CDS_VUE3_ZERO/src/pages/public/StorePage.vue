<template>
  <section class="store-page">
    <section class="store-shell">
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
      </section>

      <div class="store-summary" data-testid="store-results-count">
        Mostrando {{ filteredProducts.length }} de {{ catalog.length }} productos.
      </div>

      <p v-if="error" class="store-error" data-testid="store-error">{{ error }}</p>

      <section v-if="loading" class="store-empty" data-testid="store-loading">
        Cargando catálogo...
      </section>

      <section v-else-if="filteredProducts.length === 0" class="store-empty" data-testid="store-empty">
        No hay productos disponibles para el filtro actual.
      </section>

      <section v-else class="products-grid">
        <article v-for="product in filteredProducts" :key="product.id" class="product-card" data-testid="store-product-card">
          <div class="product-media">
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
          </div>
          <div class="product-body">
            <p class="product-family">{{ product.family || product.category || 'Repuesto' }}</p>
            <h2>{{ product.name }}</h2>
            <p class="product-sku">{{ product.sku }}</p>
            <p class="product-description">{{ describeProduct(product) }}</p>
            <div class="product-footer">
              <strong>{{ formatCurrency(product.price) }}</strong>
              <small>Stock: {{ product.sellable_stock ?? product.stock ?? 0 }}</small>
            </div>
          </div>
        </article>
      </section>

      <div class="store-actions">
        <router-link to="/" class="btn-secondary">Volver al inicio</router-link>
        <router-link
          v-if="isAuthenticated"
          to="/dashboard"
          class="btn-primary"
        >
          Ir al dashboard
        </router-link>
        <router-link
          v-else
          :to="{ name: 'login', query: { redirect: '/tienda' } }"
          class="btn-primary"
        >
          Iniciar sesión para comprar
        </router-link>
      </div>
    </section>
  </section>
</template>

<script setup>
import { useStorePage } from '@new/composables/useStorePage'

const {
  isAuthenticated,
  catalog,
  loading,
  error,
  searchTerm,
  selectedCategory,
  availableCategories,
  filteredProducts,
  loadCatalog,
  formatCurrency,
  productImageSrc,
  describeProduct
} = useStorePage()
</script>

<style scoped>
.store-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(236, 107, 0, 0.12), transparent 30%),
    radial-gradient(circle at top right, rgba(3, 134, 0, 0.1), transparent 25%),
    linear-gradient(180deg, #f8f9f6 0%, #ece9df 100%);
  padding: var(--cds-space-xl) var(--cds-space-md) var(--cds-space-2xl);
}

.store-shell {
  max-width: min(1440px, 98vw);
  margin: 0 auto;
  display: grid;
  gap: var(--cds-space-lg);
}

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
  backdrop-filter: blur(8px);
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
  font-size: 1.02rem;
}

.store-toolbar {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
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
  font-size: 0.95rem;
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

.store-empty {
  padding: var(--cds-space-xl);
  border-radius: var(--cds-radius-md);
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid var(--cds-border-soft);
  text-align: center;
  box-shadow: var(--cds-shadow-sm);
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--cds-space-md);
  align-items: stretch;
}

.product-card {
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: var(--cds-radius-lg);
  overflow: hidden;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(233, 236, 230, 0.9));
  box-shadow: var(--cds-shadow-sm);
}

.product-media {
  min-height: 180px;
  position: relative;
  display: grid;
  place-items: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background:
    linear-gradient(135deg, rgba(236, 107, 0, 0.12), rgba(3, 134, 0, 0.08)),
    #edf0e8;
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

.product-body {
  padding: var(--cds-space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--cds-space-xs);
  flex: 1;
}

.product-family,
.product-sku {
  margin: 0;
  color: var(--cds-text-muted);
  font-size: 0.88rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.product-body h2 {
  margin: 0;
  font-size: 1.1rem;
  line-height: 1.3;
}

.product-description {
  margin: 0;
  font-size: 0.97rem;
  color: var(--cds-text-muted);
}

.product-footer {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--cds-space-sm);
}

.product-footer small {
  color: var(--cds-text-muted);
}

.store-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--cds-space-sm);
  justify-content: flex-end;
  padding: var(--cds-space-sm) 0;
}

.btn-primary,
.btn-secondary {
  min-height: 44px;
  padding: 0.7rem 1.1rem;
  border-radius: 999px;
  font-size: 0.95rem;
  font-weight: var(--cds-font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  border: 1px solid transparent;
}

.btn-primary {
  border-color: color-mix(in srgb, var(--cds-primary) 75%, #602b00);
  background: linear-gradient(135deg, #ec6b00, #c65a00);
  color: #fff5e8;
  box-shadow: 0 14px 24px rgba(236, 107, 0, 0.24);
}

.btn-secondary {
  border-color: color-mix(in srgb, var(--cds-dark) 18%, white);
  background: rgba(255, 255, 255, 0.9);
  color: color-mix(in srgb, var(--cds-dark) 92%, white);
}

@media (min-width: 780px) {
  .products-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 860px) {
  .store-page {
    padding: var(--cds-space-lg) var(--cds-space-sm) var(--cds-space-xl);
  }

  .store-toolbar {
    grid-template-columns: 1fr;
  }
}
</style>
