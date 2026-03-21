<template>
  <article
    class="product-card"
    :class="{ 'product-card--added': justAdded, 'product-card--out': outOfStock }"
    @click="$emit('view', product)"
  >
    <!-- ── Imagen ─────────────────────────────────────────── -->
    <div class="product-card__img-wrap">
      <img
        v-if="product.image_url"
        :src="product.image_url"
        :alt="product.name"
        class="product-card__img"
        loading="lazy"
      />
      <div v-else class="product-card__img-placeholder">
        <IconComponent />
      </div>

      <!-- Badges -->
      <span v-if="outOfStock"   class="badge badge--danger">Sin stock</span>
      <span v-else-if="lowStock" class="badge badge--warning">
        Últimas {{ product.stock }}
      </span>

      <!-- Qty en carrito -->
      <span v-if="qtyInCart > 0" class="badge badge--cart">
        {{ qtyInCart }} en carrito
      </span>
    </div>

    <!-- ── Info ───────────────────────────────────────────── -->
    <div class="product-card__body">
      <p class="product-card__sku">{{ product.sku }}</p>
      <h3 class="product-card__name">{{ product.name }}</h3>

      <div class="product-card__footer">
        <span class="product-card__price">{{ formatCLP(product.price) }}</span>

        <button
          class="product-card__btn"
          :class="{ 'product-card__btn--added': justAdded }"
          :disabled="outOfStock"
          @click.stop="handleAdd"
          :aria-label="`Agregar ${product.name} al carrito`"
        >
          <span v-if="justAdded" class="btn-icon">✓</span>
          <span v-else           class="btn-icon">+</span>
        </button>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useShopCartStore } from '@/stores/shopCart.js'

const props  = defineProps({ product: { type: Object, required: true } })
const emit   = defineEmits(['view', 'added'])
const cart   = useShopCartStore()

const justAdded  = ref(false)
const outOfStock = computed(() => (props.product.stock ?? 1) <= 0)
const lowStock   = computed(() => {
  const s = props.product.stock
  return s != null && s > 0 && s <= 5
})
const qtyInCart  = computed(() => cart.getQty(props.product.id))

watch(() => cart.lastAdded, id => {
  if (id === props.product.id) {
    justAdded.value = true
    setTimeout(() => { justAdded.value = false }, 1100)
  }
})

function handleAdd() {
  if (outOfStock.value) return
  cart.addItem(props.product)
  emit('added', props.product)
}

function formatCLP(n) {
  return new Intl.NumberFormat('es-CL', {
    style:    'currency',
    currency: 'CLP',
    maximumFractionDigits: 0,
  }).format(n ?? 0)
}

// Placeholder icon inline (sin dependencia externa)
function IconComponent() {
  return null
}
</script>

<style scoped>
.product-card {
  background:     var(--c-surface);
  border:         1px solid var(--c-border);
  border-radius:  var(--store-radius-lg);
  overflow:       hidden;
  cursor:         pointer;
  display:        flex;
  flex-direction: column;
  transition:     border-color var(--t-mid) var(--ease-out),
                  box-shadow   var(--t-mid) var(--ease-out),
                  transform    var(--t-mid) var(--ease-out);
  box-shadow:     var(--shadow-card);
}
.product-card:hover {
  border-color: var(--c-accent-border);
  box-shadow:   0 4px 20px rgba(0, 193, 124, 0.1), var(--shadow-card);
  transform:    translateY(-2px);
}
.product-card--out {
  opacity: 0.55;
}
.product-card--added {
  border-color: var(--c-accent);
}

/* Imagen */
.product-card__img-wrap {
  position:        relative;
  aspect-ratio:    4 / 3;
  background:      var(--c-surface-2);
  overflow:        hidden;
}
.product-card__img {
  width:      100%;
  height:     100%;
  object-fit: contain;
  padding:    12px;
  transition: transform var(--t-slow) var(--ease-out);
}
.product-card:hover .product-card__img {
  transform: scale(1.04);
}
.product-card__img-placeholder {
  width:           100%;
  height:          100%;
  display:         flex;
  align-items:     center;
  justify-content: center;
  color:           var(--c-text-muted);
  font-size:       32px;
}

/* Badges */
.badge {
  position:      absolute;
  top:           8px;
  left:          8px;
  font-family:   var(--font-display);
  font-size:     10px;
  font-weight:   500;
  letter-spacing: 0.04em;
  padding:       3px 7px;
  border-radius: 4px;
  text-transform: uppercase;
}
.badge--danger  {
  background: var(--c-danger-dim);
  color:      var(--c-danger);
  border:     1px solid var(--c-danger);
}
.badge--warning {
  background: var(--c-warning-dim);
  color:      var(--c-warning);
  border:     1px solid var(--c-warning);
}
.badge--cart {
  top:        auto;
  bottom:     8px;
  left:       8px;
  background: var(--c-accent-dim);
  color:      var(--c-accent-text);
  border:     1px solid var(--c-accent-border);
}

/* Body */
.product-card__body {
  padding:        12px 14px 14px;
  display:        flex;
  flex-direction: column;
  gap:            4px;
  flex:           1;
}
.product-card__sku {
  font-family: var(--font-display);
  font-size:   10px;
  color:       var(--c-text-muted);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin:      0;
}
.product-card__name {
  font-family:  var(--font-body);
  font-size:    13.5px;
  font-weight:  500;
  color:        var(--c-text-primary);
  line-height:  1.35;
  margin:       0;
  display:      -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow:     hidden;
  flex:         1;
}
.product-card__footer {
  display:     flex;
  align-items: center;
  justify-content: space-between;
  margin-top:  10px;
}
.product-card__price {
  font-family:  var(--font-display);
  font-size:    16px;
  font-weight:  600;
  color:        var(--c-text-primary);
  letter-spacing: -0.02em;
}

/* Botón agregar */
.product-card__btn {
  width:           34px;
  height:          34px;
  border-radius:   50%;
  border:          1.5px solid var(--c-accent);
  background:      transparent;
  color:           var(--c-accent-text);
  cursor:          pointer;
  display:         flex;
  align-items:     center;
  justify-content: center;
  font-size:       18px;
  line-height:     1;
  transition:      background var(--t-fast) var(--ease-out),
                   color    var(--t-fast) var(--ease-out),
                   transform var(--t-fast) var(--ease-out);
  flex-shrink:     0;
}
.product-card__btn:hover:not(:disabled) {
  background: var(--c-accent);
  color:      #fff;
  transform:  scale(1.08);
}
.product-card__btn:active:not(:disabled) {
  transform: scale(0.94);
}
.product-card__btn--added {
  background: var(--c-accent);
  color:      #fff;
  border-color: var(--c-accent);
}
.product-card__btn:disabled {
  opacity: 0.35;
  cursor:  not-allowed;
}
.btn-icon {
  pointer-events: none;
  user-select:    none;
}
</style>
