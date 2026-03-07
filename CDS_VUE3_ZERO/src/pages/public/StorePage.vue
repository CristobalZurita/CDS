<template>
  <main class="store-page">
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
  </main>
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
  padding: 1rem;
}

.store-shell {
  max-width: 1120px;
  margin: 0 auto;
  display: grid;
  gap: 1rem;
}

.store-header,
.store-toolbar,
.store-summary,
.store-empty,
.products-grid,
.store-actions {
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
  border-radius: 0.9rem;
  background: var(--cds-white);
  padding: 0.9rem;
}

.store-header {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  justify-content: space-between;
  align-items: center;
}

.eyebrow {
  margin: 0;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
}

.store-header h1 {
  margin: 0.2rem 0 0;
  font-size: var(--cds-text-3xl);
}

.subtitle {
  margin: 0.35rem 0 0;
  color: var(--cds-text-muted);
}

.store-toolbar {
  display: grid;
  gap: 0.7rem;
  grid-template-columns: 1fr;
}

.field {
  display: grid;
  gap: 0.35rem;
}

.field span {
  font-size: var(--cds-text-sm);
}

.field input,
.field select {
  min-height: 44px;
  padding: 0.65rem 0.75rem;
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
  border-radius: 0.55rem;
  font-size: var(--cds-text-base);
}

.store-summary {
  font-size: var(--cds-text-base);
}

.store-error {
  margin: 0;
  border: 1px solid #f4c7c3;
  background: #fef3f2;
  color: #b42318;
  border-radius: 0.6rem;
  padding: 0.75rem;
}

.store-empty {
  text-align: center;
}

.products-grid {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: 1fr;
}

.product-card {
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
  border-radius: 0.8rem;
  overflow: hidden;
  display: grid;
}

.product-media {
  background: color-mix(in srgb, var(--cds-light) 10%, white);
  min-height: 140px;
  display: grid;
  place-items: center;
}

.product-image {
  width: 100%;
  height: 190px;
  object-fit: cover;
}

.product-placeholder {
  font-size: var(--cds-text-xl);
  color: var(--cds-text-muted);
}

.product-body {
  padding: 0.75rem;
  display: grid;
  gap: 0.35rem;
}

.product-family,
.product-sku {
  margin: 0;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
}

.product-body h2 {
  margin: 0;
  font-size: var(--cds-text-lg);
}

.product-description {
  margin: 0;
  font-size: var(--cds-text-base);
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.55rem;
}

.product-footer small {
  color: var(--cds-text-muted);
}

.store-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  min-height: 44px;
  padding: 0.65rem 0.95rem;
  border-radius: 0.55rem;
  font-size: var(--cds-text-base);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.btn-primary {
  border: 1px solid var(--cds-primary);
  background: var(--cds-primary);
  color: var(--cds-white);
}

.btn-secondary {
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  background: var(--cds-white);
  color: var(--cds-text-normal);
}

@media (min-width: 780px) {
  .store-toolbar {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .products-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
