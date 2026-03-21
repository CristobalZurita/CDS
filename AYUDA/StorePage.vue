<template>
  <div class="store-page" :class="{ 'store-page--sidebar-open': sidebarOpen }">

    <!-- ── Barra superior de tienda ─────────────────────────── -->
    <header class="store-topbar">
      <div class="store-topbar__inner">

        <!-- Hamburger (mobile) -->
        <button class="store-topbar__menu-btn" @click="sidebarOpen = !sidebarOpen" aria-label="Categorías">
          <span class="menu-icon" :class="{ 'menu-icon--open': sidebarOpen }">
            <span /><span /><span />
          </span>
        </button>

        <!-- Buscador -->
        <div class="store-search-wrap">
          <span class="store-search__icon">⌕</span>
          <input
            v-model="search"
            type="search"
            class="store-search"
            placeholder="Buscar componentes, SKU, descripción..."
            @keydown.escape="search = ''"
          />
          <button v-if="search" class="store-search__clear" @click="search = ''">✕</button>
        </div>

        <!-- Sort -->
        <select v-model="sort" class="store-sort">
          <option value="name">Nombre A–Z</option>
          <option value="price_asc">Precio ↑</option>
          <option value="price_desc">Precio ↓</option>
          <option value="newest">Más nuevos</option>
        </select>

        <!-- Theme toggle -->
        <button class="theme-toggle" @click="toggleTheme" :aria-label="isDark ? 'Modo claro' : 'Modo oscuro'">
          <span class="theme-toggle__track">
            <span class="theme-toggle__thumb">
              <span v-if="isDark">◑</span>
              <span v-else>○</span>
            </span>
          </span>
        </button>

        <!-- Cart trigger -->
        <button class="cart-trigger" @click="cart.toggleCart()" aria-label="Abrir carrito">
          <span class="cart-trigger__icon">⊡</span>
          <span v-if="cart.count > 0" class="cart-trigger__badge">{{ cart.count }}</span>
        </button>

      </div>
    </header>

    <div class="store-layout">

      <!-- ── Sidebar categorías ─────────────────────────────── -->
      <aside class="store-sidebar" :class="{ 'store-sidebar--open': sidebarOpen }">
        <div class="store-sidebar__inner">
          <p class="store-sidebar__label">Categorías</p>

          <button
            class="store-cat-item"
            :class="{ 'store-cat-item--active': categoryId === null }"
            @click="selectCategory(null)"
          >
            <span class="cat-item__name">Todo</span>
            <span class="cat-item__count">{{ total }}</span>
          </button>

          <button
            v-for="cat in categories"
            :key="cat.id"
            class="store-cat-item"
            :class="{ 'store-cat-item--active': categoryId === cat.id }"
            @click="selectCategory(cat.id)"
          >
            <span class="cat-item__name">{{ cat.name }}</span>
            <span v-if="cat.product_count" class="cat-item__count">{{ cat.product_count }}</span>
          </button>
        </div>
      </aside>

      <!-- Overlay sidebar mobile -->
      <div
        v-if="sidebarOpen"
        class="store-sidebar-overlay"
        @click="sidebarOpen = false"
      />

      <!-- ── Contenido principal ────────────────────────────── -->
      <main class="store-main">

        <!-- Breadcrumb / contexto -->
        <div class="store-context">
          <div class="store-context__crumb">
            <span class="context-crumb__base" @click="clearFilters">Tienda</span>
            <span v-if="activeCategory" class="context-crumb__sep">›</span>
            <span v-if="activeCategory" class="context-crumb__current">{{ activeCategory.name }}</span>
            <span v-if="search" class="context-crumb__sep">›</span>
            <span v-if="search" class="context-crumb__current">"{{ search }}"</span>
          </div>

          <span class="store-context__total">
            <span v-if="!isLoading">{{ total }} resultado{{ total !== 1 ? 's' : '' }}</span>
            <span v-else class="shimmer-text">—</span>
          </span>
        </div>

        <!-- Loading skeleton -->
        <div v-if="isLoading && products.length === 0" class="store-grid">
          <div v-for="n in 12" :key="n" class="product-skeleton" />
        </div>

        <!-- Error -->
        <div v-else-if="isError" class="store-empty">
          <span class="store-empty__icon">⚠</span>
          <p>Error cargando productos. Intenta de nuevo.</p>
          <button class="store-empty__btn" @click="clearFilters">Limpiar filtros</button>
        </div>

        <!-- Sin resultados -->
        <div v-else-if="!isLoading && products.length === 0" class="store-empty">
          <span class="store-empty__icon">∅</span>
          <p>Sin resultados para tu búsqueda</p>
          <button class="store-empty__btn" @click="clearFilters">Ver todo el catálogo</button>
        </div>

        <!-- Grid de productos -->
        <TransitionGroup
          v-else
          name="product-grid"
          tag="div"
          class="store-grid"
          :class="{ 'store-grid--loading': isLoading }"
        >
          <StoreProductCard
            v-for="product in products"
            :key="product.id"
            :product="product"
            @view="openProductModal"
            @added="onAdded"
          />
        </TransitionGroup>

        <!-- Paginación -->
        <nav v-if="totalPages > 1" class="store-pagination">
          <button
            class="page-btn"
            :disabled="page <= 1"
            @click="page--"
          >← Anterior</button>

          <div class="page-numbers">
            <button
              v-for="p in visiblePages"
              :key="p"
              class="page-num"
              :class="{ 'page-num--active': p === page, 'page-num--ellipsis': p === '…' }"
              :disabled="p === '…'"
              @click="p !== '…' && (page = p)"
            >{{ p }}</button>
          </div>

          <button
            class="page-btn"
            :disabled="page >= totalPages"
            @click="page++"
          >Siguiente →</button>
        </nav>

      </main>
    </div>

    <!-- ── Modal detalle producto ──────────────────────────── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="selectedProduct" class="product-modal-overlay" @click.self="selectedProduct = null">
          <div class="product-modal">
            <button class="product-modal__close" @click="selectedProduct = null">✕</button>

            <div class="product-modal__img">
              <img
                v-if="selectedProduct.image_url"
                :src="selectedProduct.image_url"
                :alt="selectedProduct.name"
              />
              <span v-else class="product-modal__img-placeholder">⬡</span>
            </div>

            <div class="product-modal__info">
              <p class="product-modal__sku">{{ selectedProduct.sku }}</p>
              <h2 class="product-modal__name">{{ selectedProduct.name }}</h2>
              <p v-if="selectedProduct.description" class="product-modal__desc">
                {{ selectedProduct.description }}
              </p>

              <div class="product-modal__meta">
                <div class="meta-row">
                  <span class="meta-label">Categoría</span>
                  <span class="meta-value">{{ selectedProduct.category?.name ?? '—' }}</span>
                </div>
                <div class="meta-row">
                  <span class="meta-label">Stock</span>
                  <span class="meta-value" :class="stockClass(selectedProduct.stock)">
                    {{ stockLabel(selectedProduct.stock) }}
                  </span>
                </div>
              </div>

              <div class="product-modal__footer">
                <span class="product-modal__price">{{ formatCLP(selectedProduct.price) }}</span>
                <div class="product-modal__qty-row">
                  <button class="qty-btn-lg" @click="modalQty = Math.max(1, modalQty - 1)">−</button>
                  <span class="qty-val-lg">{{ modalQty }}</span>
                  <button
                    class="qty-btn-lg"
                    @click="modalQty = Math.min(selectedProduct.stock ?? 99, modalQty + 1)"
                    :disabled="modalQty >= (selectedProduct.stock ?? 99)"
                  >+</button>
                </div>
                <button
                  class="product-modal__add-btn"
                  :disabled="(selectedProduct.stock ?? 0) <= 0"
                  @click="addFromModal"
                >
                  Agregar al carrito
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Cart Drawer global -->
    <StoreCartDrawer />

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useStorePage }      from '@/composables/useStorePage.js'
import StoreProductCard      from '@/components/business/StoreProductCard.vue'
import StoreCartDrawer       from '@/components/business/StoreCartDrawer.vue'

// ── Composable principal ──────────────────────────────────
const {
  search, categoryId, sort, page,
  products, categories, totalPages, total, activeCategory,
  isLoading, isError,
  selectCategory, clearFilters, addToCart, cart,
} = useStorePage()

// ── Sidebar mobile ────────────────────────────────────────
const sidebarOpen = ref(false)
watch(categoryId, () => { sidebarOpen.value = false })

// ── Dark mode ─────────────────────────────────────────────
const isDark = ref(document.documentElement.dataset.theme === 'dark')

function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.dataset.theme = isDark.value ? 'dark' : 'light'
  localStorage.setItem('cds_theme', isDark.value ? 'dark' : 'light')
}

onMounted(() => {
  const saved = localStorage.getItem('cds_theme')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  isDark.value = saved ? saved === 'dark' : prefersDark
  document.documentElement.dataset.theme = isDark.value ? 'dark' : 'light'
})

// ── Modal producto ────────────────────────────────────────
const selectedProduct = ref(null)
const modalQty        = ref(1)

function openProductModal(product) {
  selectedProduct.value = product
  modalQty.value        = 1
}
function addFromModal() {
  if (!selectedProduct.value) return
  for (let i = 0; i < modalQty.value; i++) {
    cart.addItem(selectedProduct.value)
  }
  selectedProduct.value = null
}
function onAdded(product) {
  // feedback ya manejado en StoreProductCard
}

// Cerrar modal con Escape
function onKeydown(e) {
  if (e.key === 'Escape') selectedProduct.value = null
}
onMounted(()  => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))

// ── Paginación visible ────────────────────────────────────
const visiblePages = computed(() => {
  const total = totalPages.value
  const cur   = page.value
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  const pages = [1]
  if (cur > 3)       pages.push('…')
  for (let p = Math.max(2, cur - 1); p <= Math.min(total - 1, cur + 1); p++) pages.push(p)
  if (cur < total - 2) pages.push('…')
  pages.push(total)
  return pages
})

// ── Helpers ───────────────────────────────────────────────
function formatCLP(n) {
  return new Intl.NumberFormat('es-CL', {
    style: 'currency', currency: 'CLP', maximumFractionDigits: 0,
  }).format(n ?? 0)
}
function stockLabel(s) {
  if (s == null) return 'Disponible'
  if (s <= 0)   return 'Sin stock'
  if (s <= 5)   return `${s} unidades`
  return 'En stock'
}
function stockClass(s) {
  if (s == null || s > 5) return 'meta-value--ok'
  if (s <= 0)             return 'meta-value--danger'
  return 'meta-value--warn'
}
</script>

<style scoped>
/* ── Page layout ─────────────────────────────────────────── */
.store-page {
  min-height:  100vh;
  background:  var(--c-bg);
  font-family: var(--font-body);
  color:       var(--c-text-primary);
  transition:  background var(--t-mid), color var(--t-mid);
}

/* ── Topbar ──────────────────────────────────────────────── */
.store-topbar {
  position:    sticky;
  top:         0;
  z-index:     100;
  height:      var(--store-header-h);
  background:  var(--c-surface);
  border-bottom: 1px solid var(--c-border);
  display:     flex;
  align-items: center;
}
.store-topbar__inner {
  width:       100%;
  max-width:   1440px;
  margin:      0 auto;
  padding:     0 20px;
  display:     flex;
  align-items: center;
  gap:         12px;
}

/* Hamburger */
.store-topbar__menu-btn {
  display:         none;
  background:      transparent;
  border:          none;
  cursor:          pointer;
  padding:         6px;
  flex-shrink:     0;
}
.menu-icon {
  display:        flex;
  flex-direction: column;
  gap:            4px;
  width:          20px;
}
.menu-icon span {
  height:       2px;
  background:   var(--c-text-primary);
  border-radius: 2px;
  transition:   transform var(--t-mid) var(--ease-out), opacity var(--t-mid);
}

/* Búsqueda */
.store-search-wrap {
  flex:       1;
  position:   relative;
  min-width:  0;
}
.store-search__icon {
  position:     absolute;
  left:         12px;
  top:          50%;
  transform:    translateY(-50%);
  font-size:    16px;
  color:        var(--c-text-muted);
  pointer-events: none;
}
.store-search {
  width:          100%;
  height:         36px;
  padding:        0 36px 0 36px;
  background:     var(--c-surface-2);
  border:         1px solid var(--c-border);
  border-radius:  var(--store-radius);
  font-family:    var(--font-body);
  font-size:      13px;
  color:          var(--c-text-primary);
  outline:        none;
  transition:     border-color var(--t-fast), box-shadow var(--t-fast);
  appearance:     none;
}
.store-search::placeholder { color: var(--c-text-muted); }
.store-search:focus {
  border-color: var(--c-accent-border);
  box-shadow:   0 0 0 3px var(--c-accent-dim);
}
.store-search__clear {
  position:    absolute;
  right:       8px;
  top:         50%;
  transform:   translateY(-50%);
  background:  transparent;
  border:      none;
  cursor:      pointer;
  color:       var(--c-text-muted);
  font-size:   12px;
  line-height: 1;
  padding:     4px;
  transition:  color var(--t-fast);
}
.store-search__clear:hover { color: var(--c-text-primary); }

/* Sort */
.store-sort {
  height:       36px;
  padding:      0 10px;
  background:   var(--c-surface-2);
  border:       1px solid var(--c-border);
  border-radius: var(--store-radius);
  font-family:  var(--font-display);
  font-size:    11px;
  color:        var(--c-text-primary);
  cursor:       pointer;
  white-space:  nowrap;
  outline:      none;
  flex-shrink:  0;
}
.store-sort:focus { border-color: var(--c-accent-border); }

/* Theme toggle */
.theme-toggle {
  background:   transparent;
  border:       1px solid var(--c-border-mid);
  border-radius: 20px;
  cursor:       pointer;
  padding:      3px;
  flex-shrink:  0;
  transition:   border-color var(--t-fast);
}
.theme-toggle:hover { border-color: var(--c-accent-border); }
.theme-toggle__track {
  display:     flex;
  align-items: center;
  width:       40px;
  height:      22px;
  position:    relative;
}
.theme-toggle__thumb {
  position:     absolute;
  width:        22px;
  height:       22px;
  background:   var(--c-surface-2);
  border-radius: 50%;
  display:      flex;
  align-items:  center;
  justify-content: center;
  font-size:    13px;
  left:         0;
  transition:   left var(--t-mid) var(--ease-out);
}
[data-theme='dark'] .theme-toggle__thumb { left: 18px; }

/* Cart trigger */
.cart-trigger {
  position:    relative;
  background:  transparent;
  border:      1px solid var(--c-border-mid);
  border-radius: var(--store-radius);
  cursor:      pointer;
  padding:     7px 10px;
  font-size:   18px;
  line-height: 1;
  color:       var(--c-text-primary);
  flex-shrink: 0;
  transition:  border-color var(--t-fast), background var(--t-fast);
}
.cart-trigger:hover {
  border-color: var(--c-accent-border);
  background:   var(--c-accent-dim);
}
.cart-trigger__badge {
  position:    absolute;
  top:         -5px;
  right:       -5px;
  background:  var(--c-accent);
  color:       #fff;
  font-family: var(--font-display);
  font-size:   9px;
  font-weight: 700;
  padding:     2px 5px;
  border-radius: 10px;
  min-width:   16px;
  text-align:  center;
}

/* ── Layout ──────────────────────────────────────────────── */
.store-layout {
  display:        flex;
  max-width:      1440px;
  margin:         0 auto;
  padding:        0 20px;
  gap:            0;
  min-height:     calc(100vh - var(--store-header-h));
}

/* ── Sidebar ─────────────────────────────────────────────── */
.store-sidebar {
  width:        var(--store-sidebar-w);
  flex-shrink:  0;
  padding:      24px 0;
  position:     sticky;
  top:          var(--store-header-h);
  height:       calc(100vh - var(--store-header-h));
  overflow-y:   auto;
  border-right: 1px solid var(--c-border);
}
.store-sidebar__inner { padding: 0 16px; }
.store-sidebar__label {
  font-family:  var(--font-display);
  font-size:    10px;
  font-weight:  500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color:        var(--c-text-muted);
  margin:       0 0 10px 8px;
}

.store-cat-item {
  display:         flex;
  align-items:     center;
  justify-content: space-between;
  width:           100%;
  padding:         8px 10px;
  background:      transparent;
  border:          none;
  border-radius:   var(--store-radius);
  cursor:          pointer;
  text-align:      left;
  font-family:     var(--font-body);
  font-size:       13px;
  color:           var(--c-text-secondary);
  transition:      background var(--t-fast), color var(--t-fast);
  margin-bottom:   2px;
}
.store-cat-item:hover {
  background: var(--c-surface-2);
  color:      var(--c-text-primary);
}
.store-cat-item--active {
  background:  var(--c-accent-dim);
  color:       var(--c-accent-text);
  font-weight: 500;
}
.cat-item__name { flex: 1; }
.cat-item__count {
  font-family: var(--font-display);
  font-size:   10px;
  color:       var(--c-text-muted);
  background:  var(--c-surface-2);
  padding:     1px 6px;
  border-radius: 8px;
  flex-shrink: 0;
}
.store-cat-item--active .cat-item__count {
  background: var(--c-accent-border);
  color:      var(--c-accent-text);
}

/* ── Main ────────────────────────────────────────────────── */
.store-main {
  flex:    1;
  padding: 24px 0 40px 28px;
  min-width: 0;
}

/* Context bar */
.store-context {
  display:         flex;
  justify-content: space-between;
  align-items:     baseline;
  margin-bottom:   20px;
}
.store-context__crumb {
  display:     flex;
  align-items: center;
  gap:         6px;
  font-size:   13px;
}
.context-crumb__base {
  color:  var(--c-text-muted);
  cursor: pointer;
  transition: color var(--t-fast);
}
.context-crumb__base:hover { color: var(--c-accent-text); }
.context-crumb__sep     { color: var(--c-text-muted); }
.context-crumb__current {
  color:       var(--c-text-primary);
  font-weight: 500;
}
.store-context__total {
  font-family: var(--font-display);
  font-size:   11px;
  color:       var(--c-text-muted);
  letter-spacing: 0.04em;
}

/* Grid */
.store-grid {
  display:               grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap:                   16px;
  transition:            opacity var(--t-mid);
}
.store-grid--loading { opacity: 0.6; pointer-events: none; }

/* Skeletons */
.product-skeleton {
  background:    var(--c-surface);
  border-radius: var(--store-radius-lg);
  aspect-ratio:  3 / 4;
  animation:     skeleton-pulse 1.4s ease-in-out infinite;
  border:        1px solid var(--c-border);
}
@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.45; }
}

/* Vacío / error */
.store-empty {
  display:         flex;
  flex-direction:  column;
  align-items:     center;
  justify-content: center;
  padding:         80px 20px;
  gap:             12px;
  color:           var(--c-text-secondary);
  font-size:       14px;
}
.store-empty__icon {
  font-family: var(--font-display);
  font-size:   40px;
  color:       var(--c-text-muted);
}
.store-empty__btn {
  margin-top:    8px;
  padding:       8px 20px;
  background:    transparent;
  border:        1px solid var(--c-border-mid);
  border-radius: var(--store-radius);
  font-size:     13px;
  color:         var(--c-text-secondary);
  cursor:        pointer;
  transition:    border-color var(--t-fast), color var(--t-fast), background var(--t-fast);
}
.store-empty__btn:hover {
  border-color: var(--c-accent-border);
  color:        var(--c-accent-text);
  background:   var(--c-accent-dim);
}

/* Paginación */
.store-pagination {
  display:         flex;
  align-items:     center;
  justify-content: center;
  gap:             8px;
  margin-top:      40px;
}
.page-btn {
  padding:       8px 16px;
  background:    transparent;
  border:        1px solid var(--c-border-mid);
  border-radius: var(--store-radius);
  font-family:   var(--font-display);
  font-size:     11px;
  color:         var(--c-text-secondary);
  cursor:        pointer;
  transition:    border-color var(--t-fast), color var(--t-fast);
}
.page-btn:hover:not(:disabled) {
  border-color: var(--c-accent-border);
  color:        var(--c-accent-text);
}
.page-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.page-numbers { display: flex; gap: 4px; }
.page-num {
  width:         34px;
  height:        34px;
  background:    transparent;
  border:        1px solid var(--c-border);
  border-radius: var(--store-radius);
  font-family:   var(--font-display);
  font-size:     12px;
  color:         var(--c-text-secondary);
  cursor:        pointer;
  transition:    all var(--t-fast);
}
.page-num:hover:not(.page-num--ellipsis):not(.page-num--active) {
  border-color: var(--c-accent-border);
  color:        var(--c-accent-text);
}
.page-num--active {
  background:   var(--c-accent);
  border-color: var(--c-accent);
  color:        #fff;
  font-weight:  600;
}
.page-num--ellipsis { border: none; cursor: default; }

/* ── Modal producto ──────────────────────────────────────── */
.product-modal-overlay {
  position:        fixed;
  inset:           0;
  background:      rgba(0, 0, 0, 0.55);
  z-index:         500;
  display:         flex;
  align-items:     center;
  justify-content: center;
  padding:         20px;
  backdrop-filter: blur(4px);
}
.product-modal {
  background:    var(--c-surface);
  border-radius: var(--store-radius-xl);
  max-width:     640px;
  width:         100%;
  max-height:    90vh;
  overflow-y:    auto;
  display:       grid;
  grid-template-columns: 1fr 1fr;
  position:      relative;
  box-shadow:    var(--shadow-float);
}
.product-modal__close {
  position:    absolute;
  top:         14px;
  right:       14px;
  background:  var(--c-surface-2);
  border:      none;
  border-radius: 50%;
  width:       30px;
  height:      30px;
  display:     flex;
  align-items: center;
  justify-content: center;
  font-size:   13px;
  color:       var(--c-text-secondary);
  cursor:      pointer;
  z-index:     1;
  transition:  background var(--t-fast), color var(--t-fast);
}
.product-modal__close:hover {
  background: var(--c-danger-dim);
  color:      var(--c-danger);
}
.product-modal__img {
  background:      var(--c-surface-2);
  border-radius:   var(--store-radius-xl) 0 0 var(--store-radius-xl);
  display:         flex;
  align-items:     center;
  justify-content: center;
  padding:         24px;
  min-height:      260px;
}
.product-modal__img img {
  width:      100%;
  height:     100%;
  max-height: 280px;
  object-fit: contain;
}
.product-modal__img-placeholder {
  font-size: 64px;
  color:     var(--c-text-muted);
  font-family: var(--font-display);
}
.product-modal__info {
  padding:        24px 24px 24px 20px;
  display:        flex;
  flex-direction: column;
  gap:            10px;
}
.product-modal__sku {
  font-family:  var(--font-display);
  font-size:    10px;
  color:        var(--c-text-muted);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin:       0;
}
.product-modal__name {
  font-size:   18px;
  font-weight: 600;
  color:       var(--c-text-primary);
  margin:      0;
  line-height: 1.3;
}
.product-modal__desc {
  font-size:   13px;
  color:       var(--c-text-secondary);
  line-height: 1.6;
  margin:      0;
}
.product-modal__meta { display: flex; flex-direction: column; gap: 6px; }
.meta-row {
  display:   flex;
  gap:       8px;
  font-size: 12px;
}
.meta-label { color: var(--c-text-muted); min-width: 72px; }
.meta-value { color: var(--c-text-primary); font-weight: 500; }
.meta-value--ok     { color: var(--c-accent-text); }
.meta-value--warn   { color: var(--c-warning); }
.meta-value--danger { color: var(--c-danger); }
.product-modal__footer {
  margin-top:  auto;
  display:     flex;
  flex-direction: column;
  gap:         12px;
}
.product-modal__price {
  font-family:  var(--font-display);
  font-size:    24px;
  font-weight:  700;
  color:        var(--c-text-primary);
  letter-spacing: -0.03em;
}
.product-modal__qty-row {
  display:     flex;
  align-items: center;
  gap:         12px;
}
.qty-btn-lg {
  width:           34px;
  height:          34px;
  background:      var(--c-surface-2);
  border:          1px solid var(--c-border-mid);
  border-radius:   var(--store-radius);
  cursor:          pointer;
  font-size:       18px;
  color:           var(--c-text-primary);
  display:         flex;
  align-items:     center;
  justify-content: center;
  transition:      background var(--t-fast);
}
.qty-btn-lg:hover:not(:disabled) { background: var(--c-surface-2); }
.qty-btn-lg:disabled { opacity: 0.3; cursor: not-allowed; }
.qty-val-lg {
  font-family: var(--font-display);
  font-size:   18px;
  font-weight: 700;
  min-width:   28px;
  text-align:  center;
  color:       var(--c-text-primary);
}
.product-modal__add-btn {
  width:          100%;
  padding:        13px;
  background:     var(--c-accent);
  color:          #fff;
  border:         none;
  border-radius:  var(--store-radius);
  font-family:    var(--font-display);
  font-size:      12px;
  font-weight:    600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor:         pointer;
  transition:     opacity var(--t-fast), transform var(--t-fast);
}
.product-modal__add-btn:hover:not(:disabled) { opacity: 0.88; }
.product-modal__add-btn:active                { transform: scale(0.98); }
.product-modal__add-btn:disabled              { opacity: 0.35; cursor: not-allowed; }

/* ── Grid transitions ────────────────────────────────────── */
.product-grid-enter-active {
  transition: all var(--t-mid) var(--ease-out);
}
.product-grid-enter-from { opacity: 0; transform: translateY(8px); }

/* ── Modal transition ────────────────────────────────────── */
.modal-enter-active, .modal-leave-active { transition: all var(--t-mid) var(--ease-out); }
.modal-enter-from, .modal-leave-to       { opacity: 0; }
.modal-enter-from .product-modal         { transform: scale(0.97) translateY(10px); }

/* ── Shimmer ─────────────────────────────────────────────── */
.shimmer-text {
  display:       inline-block;
  background:    linear-gradient(90deg, var(--c-border) 25%, var(--c-surface-2) 50%, var(--c-border) 75%);
  background-size: 200% 100%;
  animation:     shimmer 1.2s linear infinite;
  border-radius: 4px;
  width:         40px;
  height:        12px;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

/* ── Mobile ──────────────────────────────────────────────── */
@media (max-width: 768px) {
  .store-topbar__menu-btn { display: flex; }

  .store-sidebar {
    position:   fixed;
    top:        var(--store-header-h);
    left:       0;
    bottom:     0;
    z-index:    200;
    transform:  translateX(-100%);
    transition: transform var(--t-slow) var(--ease-out);
    background: var(--c-surface);
    border-right: 1px solid var(--c-border);
    box-shadow: var(--shadow-float);
  }
  .store-sidebar--open { transform: translateX(0); }
  .store-sidebar-overlay {
    position:   fixed;
    inset:      0;
    top:        var(--store-header-h);
    background: rgba(0,0,0,0.4);
    z-index:    199;
  }

  .store-main       { padding-left: 0; }
  .store-layout     { padding: 0 12px; }

  .product-modal {
    grid-template-columns: 1fr;
    max-height:            85vh;
  }
  .product-modal__img {
    border-radius: var(--store-radius-xl) var(--store-radius-xl) 0 0;
    min-height:    160px;
  }

  .store-sort { display: none; }
}
</style>
