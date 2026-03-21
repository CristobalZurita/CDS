<template>
  <!-- Overlay -->
  <Teleport to="body">
    <Transition name="overlay">
      <div
        v-if="cart.isOpen"
        class="cart-overlay"
        @click="cart.closeCart()"
      />
    </Transition>

    <!-- Drawer -->
    <Transition name="drawer">
      <aside v-if="cart.isOpen" class="cart-drawer" role="dialog" aria-label="Carrito de compras">

        <!-- Header -->
        <div class="cart-drawer__header">
          <div class="cart-drawer__title">
            <span class="cart-drawer__title-mono">carrito</span>
            <span v-if="cart.count > 0" class="cart-drawer__count">{{ cart.count }}</span>
          </div>
          <button class="cart-drawer__close" @click="cart.closeCart()" aria-label="Cerrar carrito">
            ✕
          </button>
        </div>

        <!-- Vacío -->
        <div v-if="cart.isEmpty" class="cart-drawer__empty">
          <div class="cart-drawer__empty-icon">∅</div>
          <p>Tu carrito está vacío</p>
          <button class="cart-btn-secondary" @click="cart.closeCart()">
            Ver catálogo
          </button>
        </div>

        <!-- Items -->
        <div v-else class="cart-drawer__items">
          <TransitionGroup name="item-list" tag="ul" class="cart-items-list">
            <li
              v-for="item in cart.items"
              :key="item.id"
              class="cart-item"
            >
              <!-- Imagen -->
              <div class="cart-item__img">
                <img v-if="item.image_url" :src="item.image_url" :alt="item.name" loading="lazy" />
                <span v-else>⬡</span>
              </div>

              <!-- Info -->
              <div class="cart-item__info">
                <p class="cart-item__sku">{{ item.sku }}</p>
                <p class="cart-item__name">{{ item.name }}</p>
                <p class="cart-item__price-unit">{{ formatCLP(item.price) }} c/u</p>
              </div>

              <!-- Qty control -->
              <div class="cart-item__qty">
                <button
                  class="qty-btn"
                  @click="cart.decrement(item.id)"
                  :aria-label="`Quitar uno de ${item.name}`"
                >−</button>
                <span class="qty-value">{{ item.qty }}</span>
                <button
                  class="qty-btn"
                  @click="cart.increment(item.id)"
                  :disabled="item.qty >= item.stock"
                  :aria-label="`Agregar uno de ${item.name}`"
                >+</button>
              </div>

              <!-- Subtotal + eliminar -->
              <div class="cart-item__right">
                <span class="cart-item__subtotal">{{ formatCLP(item.price * item.qty) }}</span>
                <button
                  class="cart-item__remove"
                  @click="cart.removeItem(item.id)"
                  :aria-label="`Eliminar ${item.name}`"
                >✕</button>
              </div>
            </li>
          </TransitionGroup>
        </div>

        <!-- Footer -->
        <div v-if="!cart.isEmpty" class="cart-drawer__footer">
          <div class="cart-drawer__summary">
            <div class="cart-summary-row">
              <span>Subtotal ({{ cart.count }} productos)</span>
              <span class="cart-summary-total">{{ formatCLP(cart.subtotal) }}</span>
            </div>
            <p class="cart-summary-note">Envío y descuentos calculados al finalizar</p>
          </div>

          <div class="cart-drawer__actions">
            <button class="cart-btn-primary" @click="goToCheckout">
              Ir a pagar
              <span class="cart-btn-arrow">→</span>
            </button>
            <button class="cart-btn-ghost" @click="cart.clear()">
              Vaciar carrito
            </button>
          </div>
        </div>

      </aside>
    </Transition>
  </Teleport>
</template>

<script setup>
import { useShopCartStore } from '@/stores/shopCart.js'
import { useRouter } from 'vue-router'

const cart   = useShopCartStore()
const router = useRouter()

function formatCLP(n) {
  return new Intl.NumberFormat('es-CL', {
    style: 'currency', currency: 'CLP', maximumFractionDigits: 0,
  }).format(n ?? 0)
}

function goToCheckout() {
  cart.closeCart()
  router.push({ name: 'store-checkout' })
}
</script>

<style scoped>
/* Overlay */
.cart-overlay {
  position: fixed;
  inset:    0;
  background: rgba(0, 0, 0, 0.45);
  z-index:  400;
  backdrop-filter: blur(2px);
}

/* Drawer */
.cart-drawer {
  position:       fixed;
  top:            0;
  right:          0;
  bottom:         0;
  width:          var(--store-cart-w);
  max-width:      100vw;
  background:     var(--c-surface);
  z-index:        401;
  display:        flex;
  flex-direction: column;
  box-shadow:     var(--shadow-cart);
  overflow:       hidden;
}

/* Header */
.cart-drawer__header {
  display:         flex;
  align-items:     center;
  justify-content: space-between;
  padding:         18px 20px 16px;
  border-bottom:   1px solid var(--c-border);
  flex-shrink:     0;
}
.cart-drawer__title {
  display:     flex;
  align-items: center;
  gap:         10px;
}
.cart-drawer__title-mono {
  font-family:  var(--font-display);
  font-size:    13px;
  font-weight:  500;
  color:        var(--c-text-primary);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.cart-drawer__count {
  background:   var(--c-accent-dim);
  color:        var(--c-accent-text);
  border:       1px solid var(--c-accent-border);
  font-family:  var(--font-display);
  font-size:    11px;
  font-weight:  600;
  padding:      2px 8px;
  border-radius: 20px;
}
.cart-drawer__close {
  background:  transparent;
  border:      none;
  cursor:      pointer;
  color:       var(--c-text-muted);
  font-size:   16px;
  padding:     4px 6px;
  line-height: 1;
  border-radius: var(--store-radius);
  transition:  color var(--t-fast), background var(--t-fast);
}
.cart-drawer__close:hover {
  color:       var(--c-text-primary);
  background:  var(--c-surface-2);
}

/* Vacío */
.cart-drawer__empty {
  flex:            1;
  display:         flex;
  flex-direction:  column;
  align-items:     center;
  justify-content: center;
  gap:             16px;
  color:           var(--c-text-secondary);
  font-family:     var(--font-body);
  font-size:       14px;
}
.cart-drawer__empty-icon {
  font-size:   40px;
  color:       var(--c-text-muted);
  font-family: var(--font-display);
}

/* Items */
.cart-drawer__items {
  flex:       1;
  overflow-y: auto;
  padding:    8px 0;
}
.cart-items-list {
  list-style: none;
  margin:     0;
  padding:    0;
}
.cart-item {
  display:     grid;
  grid-template-columns: 52px 1fr auto auto;
  align-items: center;
  gap:         12px;
  padding:     12px 20px;
  border-bottom: 1px solid var(--c-border);
  transition:  background var(--t-fast);
}
.cart-item:hover { background: var(--c-surface-2); }

.cart-item__img {
  width:           52px;
  height:          52px;
  background:      var(--c-surface-2);
  border-radius:   var(--store-radius);
  overflow:        hidden;
  display:         flex;
  align-items:     center;
  justify-content: center;
  flex-shrink:     0;
  font-size:       20px;
  color:           var(--c-text-muted);
}
.cart-item__img img {
  width:      100%;
  height:     100%;
  object-fit: contain;
  padding:    4px;
}
.cart-item__info { min-width: 0; }
.cart-item__sku {
  font-family: var(--font-display);
  font-size:   9px;
  color:       var(--c-text-muted);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin:      0 0 2px;
}
.cart-item__name {
  font-size:  12.5px;
  font-weight: 500;
  color:       var(--c-text-primary);
  margin:      0 0 2px;
  white-space: nowrap;
  overflow:    hidden;
  text-overflow: ellipsis;
}
.cart-item__price-unit {
  font-family: var(--font-display);
  font-size:   11px;
  color:       var(--c-text-muted);
  margin:      0;
}

/* Qty */
.cart-item__qty {
  display:     flex;
  align-items: center;
  gap:         6px;
  border:      1px solid var(--c-border-mid);
  border-radius: var(--store-radius);
  padding:     3px 4px;
}
.qty-btn {
  background:  transparent;
  border:      none;
  cursor:      pointer;
  color:       var(--c-text-secondary);
  font-size:   16px;
  line-height: 1;
  width:       22px;
  height:      22px;
  display:     flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition:  color var(--t-fast), background var(--t-fast);
}
.qty-btn:hover:not(:disabled) {
  color:       var(--c-text-primary);
  background:  var(--c-surface-2);
}
.qty-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.qty-value {
  font-family: var(--font-display);
  font-size:   13px;
  font-weight: 600;
  color:       var(--c-text-primary);
  min-width:   18px;
  text-align:  center;
}

/* Right */
.cart-item__right {
  display:        flex;
  flex-direction: column;
  align-items:    flex-end;
  gap:            6px;
}
.cart-item__subtotal {
  font-family:  var(--font-display);
  font-size:    13px;
  font-weight:  600;
  color:        var(--c-text-primary);
  white-space:  nowrap;
}
.cart-item__remove {
  background:  transparent;
  border:      none;
  cursor:      pointer;
  color:       var(--c-text-muted);
  font-size:   11px;
  padding:     2px 4px;
  border-radius: 3px;
  transition:  color var(--t-fast);
}
.cart-item__remove:hover { color: var(--c-danger); }

/* Footer */
.cart-drawer__footer {
  border-top:  1px solid var(--c-border);
  padding:     16px 20px;
  flex-shrink: 0;
}
.cart-drawer__summary { margin-bottom: 16px; }
.cart-summary-row {
  display:         flex;
  justify-content: space-between;
  align-items:     baseline;
  font-size:       13.5px;
  color:           var(--c-text-secondary);
  margin-bottom:   4px;
}
.cart-summary-total {
  font-family: var(--font-display);
  font-size:   20px;
  font-weight: 700;
  color:       var(--c-text-primary);
  letter-spacing: -0.03em;
}
.cart-summary-note {
  font-size: 11px;
  color:     var(--c-text-muted);
  margin:    0;
}
.cart-drawer__actions {
  display:        flex;
  flex-direction: column;
  gap:            8px;
}

/* Botones */
.cart-btn-primary {
  width:           100%;
  padding:         13px 20px;
  background:      var(--c-accent);
  color:           #fff;
  border:          none;
  border-radius:   var(--store-radius);
  font-family:     var(--font-display);
  font-size:       13px;
  font-weight:     600;
  letter-spacing:  0.04em;
  cursor:          pointer;
  display:         flex;
  align-items:     center;
  justify-content: center;
  gap:             8px;
  transition:      opacity var(--t-fast), transform var(--t-fast);
}
.cart-btn-primary:hover  { opacity: 0.88; }
.cart-btn-primary:active { transform: scale(0.98); }
.cart-btn-arrow { font-size: 16px; }

.cart-btn-secondary,
.cart-btn-ghost {
  width:        100%;
  padding:      10px;
  background:   transparent;
  border:       1px solid var(--c-border-mid);
  border-radius: var(--store-radius);
  font-size:    12px;
  color:        var(--c-text-secondary);
  cursor:       pointer;
  transition:   border-color var(--t-fast), color var(--t-fast), background var(--t-fast);
}
.cart-btn-secondary:hover,
.cart-btn-ghost:hover {
  border-color: var(--c-border-mid);
  color:        var(--c-text-primary);
  background:   var(--c-surface-2);
}

/* Transiciones Vue */
.overlay-enter-active, .overlay-leave-active { transition: opacity var(--t-mid) var(--ease-out); }
.overlay-enter-from, .overlay-leave-to       { opacity: 0; }

.drawer-enter-active, .drawer-leave-active {
  transition: transform var(--t-slow) var(--ease-out);
}
.drawer-enter-from, .drawer-leave-to { transform: translateX(100%); }

.item-list-enter-active { transition: all var(--t-mid) var(--ease-out); }
.item-list-leave-active { transition: all var(--t-mid) var(--ease-in); }
.item-list-enter-from   { opacity: 0; transform: translateX(20px); }
.item-list-leave-to     { opacity: 0; transform: translateX(-20px); }
.item-list-move         { transition: transform var(--t-mid) var(--ease-out); }
</style>
