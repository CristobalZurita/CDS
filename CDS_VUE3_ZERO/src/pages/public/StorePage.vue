<template>
  <section class="store-page">
    <div class="store-shell">
      <header class="store-hero">
        <div class="store-hero__copy">
          <p class="store-eyebrow">catalogo cds</p>
          <h1>Arsenal Electrónico, Repuestos Multimarca</h1>
          <p class="store-hero__lede">
            Insumos para tus teclados, sintetizadores, pedales, módulos, pianos elécticos, kits de armado
          placas pcb, todo para crear tus proyectos electrónicos y más en un solo lugar.</p>

          <div class="store-hero__actions">
            <button class="store-btn store-btn--primary" @click="openCartDrawer">
              Abrir carrito
              <span class="store-btn__badge">{{ cartItemsCount }}</span>
            </button>

            <button class="store-btn store-btn--secondary" :disabled="loading" @click="loadCatalog">
              {{ loading ? 'Actualizando...' : 'Actualizar vista' }}
            </button>

            <button
              v-if="!isFullCatalogLoaded"
              class="store-btn store-btn--ghost"
              :disabled="loading"
              @click="loadFullCatalog"
            >
              Ver catálogo completo
            </button>
          </div>
        </div>

        <div class="store-hero__metrics">
          <article class="store-metric-card">
            <span class="store-metric-card__label">Modo</span>
            <strong>{{ modeLabel }}</strong>
            <small>{{ modeDetail }}</small>
          </article>

          <article class="store-metric-card">
            <span class="store-metric-card__label">Resultados</span>
            <strong>{{ filteredProducts.length }}</strong>
            <small>{{ activeCategoryLabel }}</small>
          </article>

          <article class="store-metric-card">
            <span class="store-metric-card__label">Despacho</span>
            <strong>{{ currentShipping.name }}</strong>
            <small>{{ shippingPriceLabel }}</small>
          </article>

          <article class="store-metric-card">
            <span class="store-metric-card__label">Carrito</span>
            <strong>{{ cartItemsCount }}</strong>
            <small>{{ grandTotalLabel }}</small>
          </article>
        </div>
      </header>

      <div class="store-layout">
        <aside class="store-sidebar" :class="{ 'store-sidebar--open': mobileFiltersOpen }">
          <div class="store-sidebar__header">
            <p class="store-sidebar__label">Explorar</p>
            <button class="store-sidebar__close" @click="mobileFiltersOpen = false" aria-label="Cerrar filtros">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <section class="store-sidebar__section">
            <p class="store-sidebar__title">Categorías</p>
            <button
              class="store-filter-chip"
              :class="{ 'store-filter-chip--active': selectedCategory === '' }"
              @click="setCategory('')"
            >
              Todas
            </button>
            <button
              v-for="category in availableCategories"
              :key="category"
              class="store-filter-chip"
              :class="{ 'store-filter-chip--active': selectedCategory === category }"
              @click="setCategory(category)"
            >
              {{ category }}
            </button>
          </section>

          <section class="store-sidebar__section">
            <p class="store-sidebar__title">Disponibilidad</p>
            <button
              v-for="option in availabilityOptions"
              :key="option.value"
              class="store-filter-chip"
              :class="{ 'store-filter-chip--active': selectedAvailability === option.value }"
              @click="selectedAvailability = option.value"
            >
              {{ option.label }}
            </button>
          </section>

          <section class="store-sidebar__section store-sidebar__section--compact">
            <p class="store-sidebar__title">Lectura rápida</p>
            <ul class="store-sidebar__facts">
              <li>{{ modeDetail }}</li>
              <li>{{ availabilityFact }}</li>
              <li>{{ quotedProductsFact }}</li>
            </ul>
          </section>
        </aside>

        <div v-if="mobileFiltersOpen" class="store-sidebar-backdrop" @click="mobileFiltersOpen = false"></div>

        <main class="store-main">
          <section class="store-toolbar">
            <div class="store-toolbar__main">
              <label class="store-field store-field--search">
                <span>Búsqueda</span>
                <input
                  v-model.trim="searchTerm"
                  list="store-search-suggestions"
                  type="search"
                  placeholder="SKU, nombre o familia"
                  data-testid="store-search-input"
                />
                <button
                  v-if="searchTerm"
                  class="store-field__clear"
                  aria-label="Limpiar búsqueda"
                  @click="searchTerm = ''"
                >
                  <i class="fa-solid fa-xmark"></i>
                </button>
              </label>

              <datalist id="store-search-suggestions">
                <option
                  v-for="entry in searchSuggestions"
                  :key="`${entry.id}-${entry.sku || entry.name}`"
                  :value="entry.name"
                >
                  {{ entry.sku }}
                </option>
              </datalist>

              <label class="store-field">
                <span>Orden</span>
                <select v-model="selectedSort">
                  <option v-for="option in sortOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
              </label>

              <label class="store-field">
                <span>Despacho</span>
                <select v-model="selectedShippingKey" data-testid="store-shipping-select">
                  <option v-for="option in shippingOptions" :key="option.key" :value="option.key">
                    {{ option.name }}
                  </option>
                </select>
              </label>
            </div>

            <div class="store-toolbar__actions">
              <button class="store-toolbar__toggle" @click="mobileFiltersOpen = !mobileFiltersOpen">
                <i class="fa-solid fa-sliders"></i>
                Filtros
              </button>
              <button class="store-toolbar__reset" :disabled="!hasActiveFilters" @click="resetFilters">
                Limpiar
              </button>
            </div>
          </section>

          <div class="store-context">
            <div class="store-context__crumbs">
              <button class="store-context__root" @click="resetFilters">Tienda</button>
              <span v-if="selectedCategory" class="store-context__sep">/</span>
              <span v-if="selectedCategory" class="store-context__current">{{ selectedCategory }}</span>
              <span v-if="searchTerm" class="store-context__sep">/</span>
              <span v-if="searchTerm" class="store-context__current">“{{ searchTerm }}”</span>
            </div>

            <div class="store-context__meta">
              <span>{{ filteredProducts.length }} resultados</span>
              <span>{{ selectedAvailabilityLabel }}</span>
            </div>
          </div>

          <div v-if="showExpandBanner" class="store-banner">
            <div>
              <strong>Estás viendo una selección curada.</strong>
              <p>Úsala para explorar rápido o carga todo el catálogo cuando quieras recorrerlo completo.</p>
            </div>
            <button class="store-btn store-btn--ghost" :disabled="loading" @click="loadFullCatalog">
              Mostrar todo
            </button>
          </div>

          <div v-if="availableCategories.length" class="store-chip-row">
            <button
              class="store-chip-row__chip"
              :class="{ 'store-chip-row__chip--active': selectedCategory === '' }"
              @click="setCategory('')"
            >
              Todas
            </button>
            <button
              v-for="category in availableCategories"
              :key="category"
              class="store-chip-row__chip"
              :class="{ 'store-chip-row__chip--active': selectedCategory === category }"
              @click="setCategory(category)"
            >
              {{ category }}
            </button>
          </div>

          <p v-if="error" class="store-error" data-testid="store-error">{{ error }}</p>

          <div v-if="loading && !filteredProducts.length" class="store-grid store-grid--skeleton" data-testid="store-loading">
            <article v-for="n in 8" :key="n" class="store-skeleton"></article>
          </div>

          <section
            v-else-if="filteredProducts.length === 0"
            class="store-empty"
            data-testid="store-empty"
          >
            <i class="fa-solid fa-wave-square store-empty__icon"></i>
            <h2>No hay coincidencias para el filtro actual</h2>
            <p>Puedes limpiar filtros, abrir el catálogo completo o pedir un repuesto especial por WhatsApp.</p>
            <div class="store-empty__actions">
              <button class="store-btn store-btn--secondary" @click="resetFilters">Limpiar filtros</button>
              <button
                v-if="!isFullCatalogLoaded"
                class="store-btn store-btn--ghost"
                :disabled="loading"
                @click="loadFullCatalog"
              >
                Ver todo el catálogo
              </button>
            </div>
          </section>

          <section v-else class="store-grid">
            <StoreProductCard
              v-for="product in filteredProducts"
              :key="product.id"
              :product="product"
              :image-src="productImageSrc(product)"
              :description="describeProduct(product)"
              :price-label="productPriceLabel(product)"
              :can-add="canAddProduct(product)"
              :button-label="addButtonLabel(product)"
              :qty-in-cart="productQtyInCart(product.id)"
              @add="addToCart"
              @view="openProductModal"
            />
          </section>

          <section class="store-special-order">
            <div class="store-special-order__icon">
              <i class="fa-solid fa-toolbox"></i>
            </div>
            <div class="store-special-order__body">
              <p class="store-special-order__eyebrow">pedido especial</p>
              <h2>¿No está lo que necesitas?</h2>
              <p>
                Si el catálogo no lo muestra, no significa que no exista. El taller puede cotizar repuestos,
                componentes y accesorios fuera del listado visible.
              </p>
            </div>
            <a
              class="store-special-order__link"
              href="https://wa.me/56982957538?text=Hola%2C%20necesito%20un%20repuesto%20especial%20para%20la%20tienda%20CDS%3A%20"
              target="_blank"
              rel="noopener noreferrer"
            >
              Pedir por WhatsApp
            </a>
          </section>
        </main>
      </div>
    </div>

    <Teleport to="body">
      <Transition name="store-modal">
        <div v-if="selectedProduct" class="store-modal" @click.self="closeProductModal">
          <div class="store-modal__panel">
            <button class="store-modal__close" @click="closeProductModal" aria-label="Cerrar detalle">
              <i class="fa-solid fa-xmark"></i>
            </button>

            <div class="store-modal__media">
              <img
                v-if="selectedProductImage"
                :src="selectedProductImage"
                :alt="selectedProduct.name"
                loading="lazy"
              />
              <div v-else class="store-modal__placeholder">
                {{ selectedProduct.sku?.slice(0, 3) || 'CDS' }}
              </div>
            </div>

            <div class="store-modal__content">
              <p class="store-modal__eyebrow">{{ selectedProduct.family || selectedProduct.category || 'Repuesto' }}</p>
              <h2>{{ selectedProduct.name }}</h2>
              <p class="store-modal__sku">{{ selectedProduct.sku }}</p>
              <p class="store-modal__description">{{ describeProduct(selectedProduct) }}</p>

              <div class="store-modal__stats">
                <article>
                  <span>Precio</span>
                  <strong>{{ productPriceLabel(selectedProduct) }}</strong>
                </article>
                <article>
                  <span>Estado</span>
                  <strong>{{ selectedProductStatus }}</strong>
                </article>
                <article>
                  <span>En carrito</span>
                  <strong>{{ productQtyInCart(selectedProduct.id) }}</strong>
                </article>
              </div>

              <div class="store-modal__actions">
                <div class="store-modal__qty">
                  <button @click="decreaseModalQty" aria-label="Quitar cantidad">−</button>
                  <span>{{ modalQty }}</span>
                  <button
                    :disabled="modalQty >= selectedProductMaxQty"
                    @click="increaseModalQty"
                    aria-label="Agregar cantidad"
                  >
                    +
                  </button>
                </div>

                <button
                  class="store-btn store-btn--primary store-btn--wide"
                  :disabled="!canAddProduct(selectedProduct)"
                  @click="addSelectedProduct"
                >
                  {{ canAddProduct(selectedProduct) ? 'Agregar al carrito' : addButtonLabel(selectedProduct) }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

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
      @clear-cart="clearCart"
    />
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import StoreCartDrawer from '@/components/business/StoreCartDrawer.vue'
import StoreProductCard from '@/components/business/StoreProductCard.vue'
import { useStorePage } from '@/composables/useStorePage'

const availabilityOptions = [
  { value: 'all', label: 'Todo' },
  { value: 'sellable', label: 'Vendibles ahora' },
  { value: 'reserved', label: 'Reservados taller' },
  { value: 'out', label: 'Sin stock' },
]

const sortOptions = [
  { value: 'featured', label: 'Curado / relevante' },
  { value: 'name', label: 'Nombre A-Z' },
  { value: 'price_asc', label: 'Precio menor' },
  { value: 'price_desc', label: 'Precio mayor' },
  { value: 'stock_desc', label: 'Más stock' },
]

const {
  loading,
  error,
  catalogIndex,
  searchTerm,
  selectedCategory,
  selectedAvailability,
  selectedSort,
  selectedShippingKey,
  shippingOptions,
  cartOpen,
  cartSubmitting,
  availableCategories,
  filteredProducts,
  cartItems,
  cartItemsCount,
  currentShipping,
  totals,
  checkoutLabel,
  catalogMode,
  isFullCatalogLoaded,
  loadCatalog,
  loadFullCatalog,
  formatCurrency,
  productImageSrc,
  describeProduct,
  canAddProduct,
  addButtonLabel,
  addToCart,
  openCartDrawer,
  productQtyInCart,
  removeFromCart,
  clearCart,
  closeCartDrawer,
  onDrawerChangeQty,
  submitCheckout,
} = useStorePage()

const mobileFiltersOpen = ref(false)
const selectedProduct = ref(null)
const modalQty = ref(1)

const hasActiveFilters = computed(() => {
  return Boolean(
    String(searchTerm.value || '').trim() ||
    selectedCategory.value ||
    selectedAvailability.value !== 'all' ||
    selectedSort.value !== 'featured'
  )
})

const searchSuggestions = computed(() => {
  const rows = Array.isArray(catalogIndex.value) ? catalogIndex.value : []
  const normalizedTerm = String(searchTerm.value || '').trim().toLowerCase()
  if (!normalizedTerm) return rows.slice(0, 8)
  return rows
    .filter((entry) => {
      const haystack = [entry?.name, entry?.sku, entry?.family, entry?.category]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
      return haystack.includes(normalizedTerm)
    })
    .slice(0, 8)
})

const modeLabel = computed(() => {
  if (catalogMode.value === 'full') return 'Catálogo completo'
  if (catalogMode.value === 'search') return 'Búsqueda activa'
  return 'Selección curada'
})

const modeDetail = computed(() => {
  if (catalogMode.value === 'full') {
    return 'Vista amplia para revisar familias, stock y precios disponibles.'
  }
  if (catalogMode.value === 'search') {
    return 'La búsqueda consulta backend para abrir resultados reales del catálogo.'
  }
  return 'Selección inicial de productos clave para explorar sin ruido.'
})

const activeCategoryLabel = computed(() => {
  return selectedCategory.value || 'Todas las categorías'
})

const selectedAvailabilityLabel = computed(() => {
  return availabilityOptions.find((option) => option.value === selectedAvailability.value)?.label || 'Todo'
})

const showExpandBanner = computed(() => {
  return !loading.value && !isFullCatalogLoaded.value && !String(searchTerm.value || '').trim()
})

const shippingPriceLabel = computed(() => {
  const amount = Number(totals.value?.shippingPrice || 0)
  return amount > 0 ? formatCurrency(amount) : 'Sin costo extra'
})

const grandTotalLabel = computed(() => {
  if (!totals.value?.itemsCount) return 'Aun sin items'
  return Number(totals.value?.grandTotal || 0) > 0 ? formatCurrency(totals.value.grandTotal) : 'Por cotizar'
})

const availabilityFact = computed(() => {
  if (selectedAvailability.value === 'sellable') return 'Solo se muestran productos realmente vendibles.'
  if (selectedAvailability.value === 'reserved') return 'Se ve el stock retenido por operación interna.'
  if (selectedAvailability.value === 'out') return 'Se muestran piezas sin stock para evaluar reposición.'
  return 'Puedes alternar entre stock vendible, reservado o agotado.'
})

const quotedProductsFact = computed(() => {
  const quoted = filteredProducts.value.filter((product) => Number(product.price || 0) > 0).length
  if (!filteredProducts.value.length) return 'No hay productos visibles para estimar precios.'
  return `${quoted} de ${filteredProducts.value.length} productos muestran precio directo.`
})

const selectedProductImage = computed(() => {
  return selectedProduct.value ? productImageSrc(selectedProduct.value) : ''
})

const selectedProductMaxQty = computed(() => {
  const product = selectedProduct.value
  if (!product) return 1
  const capacity = Number(product.sellable_stock || product.available_stock || 1)
  const inCart = productQtyInCart(product.id)
  return Math.max(1, capacity - inCart)
})

const selectedProductStatus = computed(() => {
  const product = selectedProduct.value
  if (!product) return ''
  if (Number(product.available_stock || 0) <= 0) return 'Sin stock'
  if (Number(product.sellable_stock || 0) <= 0) return 'Reservado taller'
  if (product.is_low_stock) return `Ultimas ${product.sellable_stock || product.available_stock}`
  return `${product.sellable_stock || product.available_stock} disponibles`
})

watch(selectedCategory, () => {
  mobileFiltersOpen.value = false
})

function setCategory(category) {
  selectedCategory.value = String(category || '')
}

function resetFilters() {
  searchTerm.value = ''
  selectedCategory.value = ''
  selectedAvailability.value = 'all'
  selectedSort.value = 'featured'
  mobileFiltersOpen.value = false
}

function productPriceLabel(product) {
  return Number(product?.price || 0) > 0 ? formatCurrency(product.price) : 'Por cotizar'
}

function openProductModal(product) {
  selectedProduct.value = product
  modalQty.value = 1
}

function closeProductModal() {
  selectedProduct.value = null
}

function increaseModalQty() {
  modalQty.value = Math.min(selectedProductMaxQty.value, modalQty.value + 1)
}

function decreaseModalQty() {
  modalQty.value = Math.max(1, modalQty.value - 1)
}

function addSelectedProduct() {
  if (!selectedProduct.value || !canAddProduct(selectedProduct.value)) return
  for (let index = 0; index < modalQty.value; index += 1) {
    addToCart(selectedProduct.value)
  }
  openCartDrawer()
  closeProductModal()
}

function handleKeydown(event) {
  if (event.key !== 'Escape') return
  if (selectedProduct.value) {
    closeProductModal()
    return
  }
  mobileFiltersOpen.value = false
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.store-page {
  min-height: 100vh;
  padding: var(--cds-space-xl) var(--cds-space-md) var(--cds-space-2xl);
  background: var(--cds-background-color);
}

.store-shell {
  max-width: var(--cds-content-max);
  margin: 0 auto;
  display: grid;
  gap: var(--cds-space-lg);
}

.store-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(340px, 0.9fr);
  gap: var(--cds-space-lg);
  padding: var(--cds-space-xl);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-xl);
  background: var(--cds-surface-1);
  box-shadow: var(--cds-shadow-md);
}

.store-eyebrow,
.store-special-order__eyebrow,
.store-metric-card__label,
.store-sidebar__label,
.store-sidebar__title {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: var(--cds-text-xs);
  font-weight: var(--cds-font-bold);
}

.store-eyebrow,
.store-special-order__eyebrow,
.store-metric-card__label {
  color: var(--cds-primary);
}

.store-hero h1 {
  margin: 0;
  max-width: 14ch;
  font-family: var(--cds-headings-font-family);
  font-size: var(--cds-text-5xl);
  line-height: 0.95;
  letter-spacing: -0.04em;
  text-transform: uppercase;
  color: var(--cds-dark);
}

.store-hero__copy {
  display: grid;
  gap: var(--cds-space-md);
}

.store-hero__lede {
  margin: 0;
  max-width: 60ch;
  font-size: var(--cds-text-xl);
  line-height: var(--cds-leading-relaxed);
  color: var(--cds-text-muted);
}

.store-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--cds-space-sm);
}

.store-btn {
  min-height: 46px;
  padding: var(--cds-space-sm) var(--cds-space-md);
  border-radius: var(--cds-radius-pill);
  border: 1px solid transparent;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-bold);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--cds-space-xs);
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease, border-color 0.18s ease;
}

.store-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.store-btn:disabled {
  opacity: 0.58;
  cursor: default;
}

.store-btn--primary {
  background: var(--cds-primary);
  color: var(--cds-white);
  box-shadow: 0 14px 28px rgba(200, 100, 34, 0.24);
}

.store-btn--secondary {
  background: var(--cds-dark);
  color: var(--cds-white);
  border-color: var(--cds-dark);
}

.store-btn--ghost {
  background: var(--cds-surface-2);
  color: var(--cds-primary);
  border-color: var(--cds-border-card);
}

.store-btn--wide {
  width: 100%;
}

.store-btn__badge {
  min-width: 1.55rem;
  min-height: 1.55rem;
  padding: 0 0.4rem;
  border-radius: var(--cds-radius-pill);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--cds-warm-support);
  color: var(--cds-white);
}

.store-hero__metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--cds-space-sm);
}

.store-metric-card {
  display: grid;
  gap: var(--cds-space-2xs);
  padding: var(--cds-space-md);
  border-radius: var(--cds-radius-lg);
  border: 1px solid var(--cds-border-card);
  background: var(--cds-surface-2);
}

.store-metric-card strong {
  font-size: var(--cds-text-xl);
  line-height: 1.1;
  color: var(--cds-dark);
}

.store-metric-card small {
  color: var(--cds-text-muted);
  line-height: var(--cds-leading-normal);
}

.store-layout {
  position: relative;
  display: grid;
  grid-template-columns: minmax(220px, 280px) minmax(0, 1fr);
  gap: var(--cds-space-lg);
  align-items: start;
}

.store-sidebar {
  position: sticky;
  top: calc(var(--layout-header-offset, 0px) + var(--cds-space-md));
  display: grid;
  gap: var(--cds-space-md);
  padding: var(--cds-space-md);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-xl);
  background: var(--cds-surface-1);
  box-shadow: var(--cds-shadow-sm);
}

.store-sidebar__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.store-sidebar__close {
  display: none;
  width: 34px;
  height: 34px;
  border: 1px solid var(--cds-border-card);
  border-radius: 50%;
  background: var(--cds-surface-1);
  cursor: pointer;
}

.store-sidebar__section {
  display: grid;
  gap: var(--cds-space-xs);
}

.store-sidebar__section--compact {
  padding-top: var(--cds-space-xs);
  border-top: 1px solid var(--cds-border-card);
}

.store-filter-chip {
  width: 100%;
  padding: var(--cds-space-sm) var(--cds-space-md);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-pill);
  background: var(--cds-surface-1);
  color: var(--cds-dark);
  font-size: var(--cds-text-sm);
  font-weight: 600;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.18s ease, transform 0.18s ease, background 0.18s ease;
}

.store-filter-chip:hover {
  transform: translateX(2px);
}

.store-filter-chip--active {
  border-color: var(--cds-primary);
  background: var(--cds-surface-2);
  color: var(--cds-primary);
}

.store-sidebar__facts {
  margin: 0;
  padding-left: var(--cds-space-md);
  display: grid;
  gap: var(--cds-space-xs);
  color: var(--cds-text-muted);
  line-height: var(--cds-leading-normal);
}

.store-sidebar-backdrop {
  display: none;
}

.store-main {
  display: grid;
  gap: var(--cds-space-md);
}

.store-toolbar {
  display: grid;
  gap: var(--cds-space-sm);
  padding: var(--cds-space-md);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-xl);
  background: var(--cds-surface-1);
  box-shadow: var(--cds-shadow-sm);
}

.store-toolbar__main {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) repeat(2, minmax(180px, 0.5fr));
  gap: var(--cds-space-sm);
}

.store-toolbar__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--cds-space-sm);
}

.store-toolbar__toggle,
.store-toolbar__reset,
.store-context__root {
  border: none;
  background: none;
  cursor: pointer;
  font: inherit;
}

.store-toolbar__toggle {
  display: none;
  align-items: center;
  gap: var(--cds-space-2xs);
  color: var(--cds-dark);
  font-weight: var(--cds-font-bold);
}

.store-toolbar__reset {
  color: var(--cds-primary);
  font-weight: var(--cds-font-bold);
}

.store-toolbar__reset:disabled {
  opacity: 0.45;
  cursor: default;
}

.store-field {
  display: grid;
  gap: var(--cds-space-2xs);
}

.store-field span {
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: var(--cds-text-xs);
  font-weight: var(--cds-font-bold);
  color: var(--cds-text-muted);
}

.store-field--search {
  position: relative;
}

.store-field input,
.store-field select {
  min-height: 46px;
  width: 100%;
  padding: var(--cds-space-sm) var(--cds-space-md);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-md);
  background: var(--cds-surface-1);
  color: var(--cds-dark);
  font-size: var(--cds-text-sm);
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

.store-field input:focus,
.store-field select:focus {
  border-color: var(--cds-primary);
  box-shadow: var(--cds-focus-ring);
  outline: none;
}

.store-field__clear {
  position: absolute;
  right: 0.85rem;
  bottom: 0.8rem;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 50%;
  background: var(--cds-surface-2);
  color: var(--cds-primary);
  cursor: pointer;
}

.store-context {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--cds-space-sm);
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
}

.store-context__crumbs,
.store-context__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--cds-space-2xs);
  align-items: center;
}

.store-context__root {
  padding: 0;
  color: var(--cds-primary);
  font-weight: var(--cds-font-bold);
}

.store-banner,
.store-special-order,
.store-empty {
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-xl);
}

.store-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--cds-space-md);
  padding: var(--cds-space-md) var(--cds-space-lg);
  background: var(--cds-surface-2);
}

.store-banner strong,
.store-empty h2,
.store-special-order h2 {
  color: var(--cds-dark);
}

.store-banner p,
.store-empty p,
.store-special-order p {
  margin: 0;
  line-height: var(--cds-leading-relaxed);
  color: var(--cds-text-muted);
}

.store-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--cds-space-xs);
}

.store-chip-row__chip {
  padding: var(--cds-space-xs) var(--cds-space-md);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-pill);
  background: var(--cds-surface-1);
  color: var(--cds-dark);
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-bold);
  cursor: pointer;
}

.store-chip-row__chip--active {
  background: var(--cds-primary);
  color: var(--cds-white);
}

.store-error {
  margin: 0;
  padding: var(--cds-space-sm) var(--cds-space-md);
  border-radius: var(--cds-radius-md);
  border: 1px solid var(--cds-invalid-border);
  background: var(--cds-invalid-bg);
  color: var(--cds-invalid-text);
}

.store-grid {
  display: grid;
  gap: var(--cds-space-md);
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
}

.store-grid--skeleton {
  pointer-events: none;
}

.store-skeleton {
  min-height: 320px;
  border-radius: var(--cds-radius-xl);
  border: 1px solid var(--cds-border-card);
  background: var(--cds-surface-2);
  animation: store-skeleton 1.2s ease-in-out infinite alternate;
}

.store-empty {
  display: grid;
  justify-items: center;
  gap: var(--cds-space-sm);
  padding: var(--cds-space-xl) var(--cds-space-md);
  text-align: center;
  background: var(--cds-surface-1);
}

.store-empty__icon {
  font-size: var(--cds-text-2xl);
  color: var(--cds-primary);
}

.store-empty__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--cds-space-sm);
  justify-content: center;
}

.store-special-order {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: var(--cds-space-md);
  align-items: center;
  padding: var(--cds-space-lg);
  background: var(--cds-surface-1);
}

.store-special-order__icon {
  width: 62px;
  height: 62px;
  display: grid;
  place-items: center;
  border-radius: var(--cds-radius-lg);
  background: var(--cds-dark);
  color: var(--cds-white);
  font-size: var(--cds-text-xl);
}

.store-special-order__body {
  display: grid;
  gap: var(--cds-space-2xs);
}

.store-special-order__link {
  min-height: 46px;
  padding: var(--cds-space-sm) var(--cds-space-md);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--cds-radius-pill);
  background: #25d366;
  color: var(--cds-white);
  font-weight: var(--cds-font-bold);
  text-decoration: none;
  box-shadow: 0 12px 24px rgba(37, 211, 102, 0.26);
}

.store-modal-enter-active,
.store-modal-leave-active {
  transition: opacity 0.22s ease;
}

.store-modal-enter-from,
.store-modal-leave-to {
  opacity: 0;
}

.store-modal {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: grid;
  place-items: center;
  padding: var(--cds-space-md);
  background: rgba(10, 12, 15, 0.78);
  backdrop-filter: blur(3px);
}

.store-modal__panel {
  position: relative;
  width: min(880px, 100%);
  display: grid;
  grid-template-columns: minmax(260px, 0.9fr) minmax(0, 1.1fr);
  gap: var(--cds-space-lg);
  padding: var(--cds-space-lg);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-xl);
  background: var(--cds-surface-1);
  box-shadow: var(--cds-shadow-lg);
}

.store-modal__close {
  position: absolute;
  top: var(--cds-space-sm);
  right: var(--cds-space-sm);
  width: 38px;
  height: 38px;
  border: 1px solid var(--cds-border-card);
  border-radius: 50%;
  background: var(--cds-surface-2);
  cursor: pointer;
}

.store-modal__media {
  min-height: 320px;
  display: grid;
  place-items: center;
  border-radius: var(--cds-radius-lg);
  background: var(--cds-surface-2);
  overflow: hidden;
}

.store-modal__media img {
  max-width: 100%;
  max-height: 320px;
  object-fit: contain;
}

.store-modal__placeholder {
  width: 96px;
  height: 96px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: var(--cds-glow-primary);
  color: var(--cds-primary);
  font-weight: var(--cds-font-bold);
  letter-spacing: 0.08em;
}

.store-modal__content {
  display: grid;
  gap: var(--cds-space-sm);
  align-content: start;
}

.store-modal__eyebrow,
.store-modal__sku {
  margin: 0;
  color: var(--cds-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.store-modal__eyebrow {
  font-size: var(--cds-text-xs);
  font-weight: var(--cds-font-bold);
}

.store-modal__sku {
  font-size: var(--cds-text-xs);
  font-weight: var(--cds-font-bold);
}

.store-modal__content h2 {
  margin: 0;
  font-family: var(--cds-headings-font-family);
  font-size: var(--cds-text-3xl);
  line-height: 0.98;
  color: var(--cds-dark);
}

.store-modal__description {
  margin: 0;
  color: var(--cds-text-muted);
  line-height: var(--cds-leading-relaxed);
}

.store-modal__stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--cds-space-sm);
}

.store-modal__stats article {
  display: grid;
  gap: var(--cds-space-2xs);
  padding: var(--cds-space-sm);
  border-radius: var(--cds-radius-md);
  background: var(--cds-surface-2);
}

.store-modal__stats span {
  font-size: var(--cds-text-xs);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--cds-text-muted);
}

.store-modal__stats strong {
  color: var(--cds-dark);
}

.store-modal__actions {
  display: grid;
  gap: var(--cds-space-sm);
  align-items: center;
}

.store-modal__qty {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-pill);
  overflow: hidden;
}

.store-modal__qty button,
.store-modal__qty span {
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.store-modal__qty button {
  border: none;
  background: var(--cds-surface-2);
  cursor: pointer;
  font-size: var(--cds-text-base);
}

.store-modal__qty button:disabled {
  opacity: 0.4;
  cursor: default;
}

@keyframes store-skeleton {
  0% {
    opacity: 0.65;
  }
  100% {
    opacity: 1;
  }
}

@media (max-width: 1180px) {
  .store-hero {
    grid-template-columns: 1fr;
  }

  .store-layout {
    grid-template-columns: 1fr;
  }

  .store-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1100;
    width: min(340px, 86vw);
    height: 100vh;
    border-radius: 0 var(--cds-radius-xl) var(--cds-radius-xl) 0;
    transform: translateX(-104%);
    transition: transform 0.22s ease;
  }

  .store-sidebar--open {
    transform: translateX(0);
  }

  .store-sidebar__close,
  .store-toolbar__toggle,
  .store-sidebar-backdrop {
    display: inline-flex;
  }

  .store-sidebar-backdrop {
    position: fixed;
    inset: 0;
    z-index: 1090;
    background: rgba(10, 12, 15, 0.62);
  }
}

@media (max-width: 960px) {
  .store-toolbar__main {
    grid-template-columns: 1fr;
  }

  .store-banner,
  .store-special-order {
    grid-template-columns: 1fr;
  }

  .store-special-order__link {
    width: 100%;
  }

  .store-modal__panel {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .store-page {
    padding-inline: var(--cds-space-sm);
  }

  .store-hero h1 {
    max-width: none;
    font-size: var(--cds-text-4xl);
  }

  .store-hero__metrics,
  .store-modal__stats {
    grid-template-columns: 1fr;
  }

  .store-context,
  .store-toolbar__actions {
    align-items: flex-start;
    flex-direction: column;
  }

  .store-grid {
    grid-template-columns: 1fr;
  }
}
</style>
