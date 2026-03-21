<template>
  <div class="checkout-page">

    <div class="checkout-inner">

      <!-- Header -->
      <div class="checkout-header">
        <button class="checkout-back" @click="$router.push({ name: 'store' })">
          ← Volver a la tienda
        </button>
        <h1 class="checkout-title">Finalizar compra</h1>
      </div>

      <!-- Layout 2 columnas -->
      <div class="checkout-layout">

        <!-- Formulario -->
        <section class="checkout-form-section">

          <!-- Datos cliente -->
          <div class="checkout-block">
            <h2 class="checkout-block__title">
              <span class="block-num">01</span> Tus datos
            </h2>
            <div class="form-grid">
              <div class="form-field">
                <label class="form-label">Nombre completo *</label>
                <input v-model="form.customer.name"    class="form-input" type="text"  placeholder="Juan Pérez" />
                <span v-if="errors['customer.name']" class="form-error">{{ errors['customer.name'] }}</span>
              </div>
              <div class="form-field">
                <label class="form-label">Email *</label>
                <input v-model="form.customer.email"   class="form-input" type="email" placeholder="juan@correo.cl" />
                <span v-if="errors['customer.email']" class="form-error">{{ errors['customer.email'] }}</span>
              </div>
              <div class="form-field">
                <label class="form-label">Teléfono *</label>
                <input v-model="form.customer.phone"   class="form-input" type="tel"   placeholder="+56 9 1234 5678" />
                <span v-if="errors['customer.phone']" class="form-error">{{ errors['customer.phone'] }}</span>
              </div>
              <div class="form-field">
                <label class="form-label">RUT (opcional)</label>
                <input v-model="form.customer.rut"     class="form-input" type="text"  placeholder="12.345.678-9" />
              </div>
            </div>
          </div>

          <!-- Envío -->
          <div class="checkout-block">
            <h2 class="checkout-block__title">
              <span class="block-num">02</span> Despacho
            </h2>
            <div class="shipping-methods">
              <label
                v-for="method in shippingMethods"
                :key="method.id"
                class="shipping-option"
                :class="{ 'shipping-option--active': shippingMethod === method.id }"
              >
                <input type="radio" v-model="shippingMethod" :value="method.id" class="sr-only" />
                <div class="shipping-option__radio" />
                <div class="shipping-option__info">
                  <span class="shipping-option__name">{{ method.name }}</span>
                  <span class="shipping-option__desc">{{ method.desc }}</span>
                </div>
                <span class="shipping-option__price">
                  {{ method.cost === 0 ? 'Gratis' : formatCLP(method.cost) }}
                </span>
              </label>
            </div>

            <div v-if="shippingMethod === 'delivery'" class="form-grid" style="margin-top: 16px">
              <div class="form-field form-field--full">
                <label class="form-label">Dirección *</label>
                <input v-model="form.shipping.address" class="form-input" type="text" placeholder="Av. Libertad 1234, Depto 5" />
                <span v-if="errors['shipping.address']" class="form-error">{{ errors['shipping.address'] }}</span>
              </div>
              <div class="form-field">
                <label class="form-label">Comuna *</label>
                <input v-model="form.shipping.commune" class="form-input" type="text" placeholder="Viña del Mar" />
              </div>
              <div class="form-field">
                <label class="form-label">Región</label>
                <input v-model="form.shipping.region"  class="form-input" type="text" placeholder="Valparaíso" />
              </div>
            </div>
          </div>

          <!-- Pago -->
          <div class="checkout-block">
            <h2 class="checkout-block__title">
              <span class="block-num">03</span> Método de pago
            </h2>
            <div class="payment-methods">
              <label
                v-for="pm in paymentMethods"
                :key="pm.id"
                class="payment-option"
                :class="{ 'payment-option--active': form.payment_method === pm.id }"
              >
                <input type="radio" v-model="form.payment_method" :value="pm.id" class="sr-only" />
                <div class="payment-option__radio" />
                <div class="payment-option__info">
                  <span class="payment-option__name">{{ pm.name }}</span>
                  <span class="payment-option__desc">{{ pm.desc }}</span>
                </div>
              </label>
            </div>
          </div>

          <!-- Notas -->
          <div class="checkout-block">
            <h2 class="checkout-block__title">
              <span class="block-num">04</span> Notas (opcional)
            </h2>
            <textarea
              v-model="form.notes"
              class="form-textarea"
              placeholder="Instrucciones especiales, referencias de entrega..."
              rows="3"
            />
          </div>

        </section>

        <!-- Resumen del pedido -->
        <aside class="checkout-summary">
          <div class="summary-card">
            <h2 class="summary-card__title">Resumen del pedido</h2>

            <ul class="summary-items">
              <li v-for="item in cart.items" :key="item.id" class="summary-item">
                <div class="summary-item__img">
                  <img v-if="item.image_url" :src="item.image_url" :alt="item.name" />
                  <span v-else>⬡</span>
                </div>
                <div class="summary-item__info">
                  <p class="summary-item__name">{{ item.name }}</p>
                  <p class="summary-item__qty">× {{ item.qty }}</p>
                </div>
                <span class="summary-item__price">{{ formatCLP(item.price * item.qty) }}</span>
              </li>
            </ul>

            <div class="summary-totals">
              <div class="summary-row">
                <span>Subtotal</span>
                <span>{{ formatCLP(cart.subtotal) }}</span>
              </div>
              <div class="summary-row">
                <span>Envío</span>
                <span>{{ shippingCost === 0 ? 'Gratis' : formatCLP(shippingCost) }}</span>
              </div>
              <div class="summary-row summary-row--total">
                <span>Total</span>
                <span class="summary-grand-total">{{ formatCLP(cart.subtotal + shippingCost) }}</span>
              </div>
            </div>

            <button
              class="checkout-submit"
              :disabled="isSubmitting || cart.isEmpty"
              @click="submitOrder"
            >
              <span v-if="isSubmitting" class="checkout-submit__spinner" />
              <span v-else>
                {{ form.payment_method === 'webpay' ? 'Pagar con Webpay' : 'Confirmar pedido' }}
              </span>
            </button>

            <p class="checkout-disclaimer">
              Al confirmar aceptas nuestros términos de servicio.
              Tus datos son tratados de forma segura.
            </p>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter }         from 'vue-router'
import { useShopCartStore }  from '@/stores/shopCart.js'
import { createOrder }       from '@/services/storeCatalogService.js'

const cart   = useShopCartStore()
const router = useRouter()

// ── Form state ────────────────────────────────────────────
const form = ref({
  customer: { name: '', email: '', phone: '', rut: '' },
  shipping: { address: '', commune: '', region: 'Valparaíso' },
  notes:    '',
  payment_method: 'transfer',
})
const errors      = ref({})
const isSubmitting = ref(false)
const shippingMethod = ref('store')  // store | delivery

// ── Opciones ──────────────────────────────────────────────
const shippingMethods = [
  { id: 'store',    name: 'Retiro en tienda',  desc: 'Lautaro 37, Viña del Mar', cost: 0 },
  { id: 'delivery', name: 'Despacho a domicilio', desc: 'Chilexpress / Starken',  cost: 3990 },
]
const paymentMethods = [
  { id: 'transfer', name: 'Transferencia bancaria', desc: 'Te enviamos los datos por email' },
  { id: 'webpay',   name: 'Webpay Plus',             desc: 'Tarjeta débito o crédito' },
  { id: 'store',    name: 'Pago en tienda',           desc: 'Efectivo o tarjeta al retirar' },
]

const shippingCost = computed(() =>
  shippingMethods.find(m => m.id === shippingMethod.value)?.cost ?? 0
)

// ── Validación ────────────────────────────────────────────
function validate() {
  const e = {}
  if (!form.value.customer.name.trim())  e['customer.name']  = 'Requerido'
  if (!form.value.customer.email.trim()) e['customer.email'] = 'Requerido'
  if (!form.value.customer.phone.trim()) e['customer.phone'] = 'Requerido'
  if (shippingMethod.value === 'delivery' && !form.value.shipping.address.trim())
    e['shipping.address'] = 'Requerido para despacho'
  errors.value = e
  return Object.keys(e).length === 0
}

// ── Submit ────────────────────────────────────────────────
async function submitOrder() {
  if (!validate()) return
  isSubmitting.value = true

  try {
    const payload = {
      ...form.value,
      items: cart.items.map(i => ({
        product_id: i.id,
        qty:        i.qty,
        unit_price: i.price,
      })),
    }
    if (shippingMethod.value === 'store') {
      payload.shipping = { address: 'Retiro en tienda', commune: 'Viña del Mar', region: 'Valparaíso' }
    }

    const result = await createOrder(payload)

    cart.clear()

    if (result.webpay_url) {
      window.location.href = result.webpay_url
    } else {
      router.push({ name: 'store-payment-result', query: { status: 'ok', code: result.code ?? '' } })
    }
  } catch (err) {
    const msg = err?.response?.data?.detail ?? 'Error al procesar el pedido. Inténtalo de nuevo.'
    errors.value['_global'] = msg
  } finally {
    isSubmitting.value = false
  }
}

function formatCLP(n) {
  return new Intl.NumberFormat('es-CL', {
    style: 'currency', currency: 'CLP', maximumFractionDigits: 0,
  }).format(n ?? 0)
}
</script>

<style scoped>
.checkout-page {
  min-height:  100vh;
  background:  var(--c-bg);
  font-family: var(--font-body);
  color:       var(--c-text-primary);
  padding:     32px 20px 60px;
}
.checkout-inner { max-width: 1100px; margin: 0 auto; }

.checkout-header { margin-bottom: 28px; }
.checkout-back {
  background:   transparent;
  border:       none;
  cursor:       pointer;
  font-size:    13px;
  color:        var(--c-text-muted);
  padding:      0;
  margin-bottom: 12px;
  display:      block;
  transition:   color var(--t-fast);
}
.checkout-back:hover { color: var(--c-accent-text); }
.checkout-title {
  font-family:  var(--font-display);
  font-size:    26px;
  font-weight:  600;
  letter-spacing: -0.02em;
  margin:       0;
}

.checkout-layout {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 28px;
  align-items: start;
}

/* Bloque */
.checkout-block {
  background:    var(--c-surface);
  border:        1px solid var(--c-border);
  border-radius: var(--store-radius-lg);
  padding:       24px;
  margin-bottom: 16px;
}
.checkout-block__title {
  font-family:  var(--font-display);
  font-size:    13px;
  font-weight:  600;
  letter-spacing: 0.04em;
  color:        var(--c-text-primary);
  margin:       0 0 20px;
  display:      flex;
  align-items:  center;
  gap:          10px;
}
.block-num {
  font-size:    11px;
  color:        var(--c-accent-text);
  background:   var(--c-accent-dim);
  border:       1px solid var(--c-accent-border);
  padding:      2px 7px;
  border-radius: 4px;
}

/* Form grid */
.form-grid {
  display:               grid;
  grid-template-columns: 1fr 1fr;
  gap:                   14px;
}
.form-field { display: flex; flex-direction: column; gap: 5px; }
.form-field--full { grid-column: 1 / -1; }
.form-label {
  font-family:  var(--font-display);
  font-size:    10px;
  font-weight:  500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color:        var(--c-text-muted);
}
.form-input {
  height:       38px;
  padding:      0 12px;
  background:   var(--c-surface-2);
  border:       1px solid var(--c-border-mid);
  border-radius: var(--store-radius);
  font-family:  var(--font-body);
  font-size:    13.5px;
  color:        var(--c-text-primary);
  outline:      none;
  transition:   border-color var(--t-fast), box-shadow var(--t-fast);
}
.form-input::placeholder { color: var(--c-text-muted); }
.form-input:focus {
  border-color: var(--c-accent-border);
  box-shadow:   0 0 0 3px var(--c-accent-dim);
}
.form-textarea {
  width:        100%;
  padding:      10px 12px;
  background:   var(--c-surface-2);
  border:       1px solid var(--c-border-mid);
  border-radius: var(--store-radius);
  font-family:  var(--font-body);
  font-size:    13px;
  color:        var(--c-text-primary);
  resize:       vertical;
  outline:      none;
  box-sizing:   border-box;
  transition:   border-color var(--t-fast), box-shadow var(--t-fast);
}
.form-textarea:focus {
  border-color: var(--c-accent-border);
  box-shadow:   0 0 0 3px var(--c-accent-dim);
}
.form-error {
  font-size: 11px;
  color:     var(--c-danger);
}

/* Envío */
.shipping-methods, .payment-methods {
  display:        flex;
  flex-direction: column;
  gap:            8px;
}
.shipping-option, .payment-option {
  display:       flex;
  align-items:   center;
  gap:           12px;
  padding:       14px 16px;
  background:    var(--c-surface-2);
  border:        1px solid var(--c-border);
  border-radius: var(--store-radius);
  cursor:        pointer;
  transition:    border-color var(--t-fast), background var(--t-fast);
}
.shipping-option--active, .payment-option--active {
  border-color: var(--c-accent);
  background:   var(--c-accent-dim);
}
.shipping-option__radio, .payment-option__radio {
  width:         16px;
  height:        16px;
  border-radius: 50%;
  border:        2px solid var(--c-border-mid);
  flex-shrink:   0;
  transition:    border-color var(--t-fast), background var(--t-fast);
}
.shipping-option--active .shipping-option__radio,
.payment-option--active  .payment-option__radio {
  border-color: var(--c-accent);
  background:   var(--c-accent);
  box-shadow:   inset 0 0 0 3px var(--c-surface-2);
}
.shipping-option__info, .payment-option__info {
  flex:           1;
  display:        flex;
  flex-direction: column;
  gap:            2px;
}
.shipping-option__name, .payment-option__name {
  font-size:   13.5px;
  font-weight: 500;
  color:       var(--c-text-primary);
}
.shipping-option__desc, .payment-option__desc {
  font-size: 12px;
  color:     var(--c-text-muted);
}
.shipping-option__price {
  font-family:  var(--font-display);
  font-size:    13px;
  font-weight:  600;
  color:        var(--c-text-primary);
}

/* Summary card */
.checkout-summary { position: sticky; top: calc(var(--store-header-h) + 20px); }
.summary-card {
  background:    var(--c-surface);
  border:        1px solid var(--c-border);
  border-radius: var(--store-radius-lg);
  padding:       24px;
}
.summary-card__title {
  font-family:  var(--font-display);
  font-size:    12px;
  font-weight:  600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color:        var(--c-text-muted);
  margin:       0 0 18px;
}
.summary-items { list-style: none; padding: 0; margin: 0 0 16px; }
.summary-item {
  display:     flex;
  align-items: center;
  gap:         10px;
  padding:     10px 0;
  border-bottom: 1px solid var(--c-border);
}
.summary-item:last-child { border-bottom: none; }
.summary-item__img {
  width:           40px;
  height:          40px;
  background:      var(--c-surface-2);
  border-radius:   var(--store-radius);
  flex-shrink:     0;
  overflow:        hidden;
  display:         flex;
  align-items:     center;
  justify-content: center;
  font-size:       16px;
  color:           var(--c-text-muted);
}
.summary-item__img img { width: 100%; height: 100%; object-fit: contain; padding: 4px; }
.summary-item__info  { flex: 1; min-width: 0; }
.summary-item__name  { font-size: 12px; font-weight: 500; color: var(--c-text-primary); margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.summary-item__qty   { font-size: 11px; color: var(--c-text-muted); margin: 2px 0 0; }
.summary-item__price { font-family: var(--font-display); font-size: 13px; font-weight: 600; color: var(--c-text-primary); white-space: nowrap; }

.summary-totals { border-top: 1px solid var(--c-border); padding-top: 14px; margin-top: 4px; }
.summary-row {
  display:     flex;
  justify-content: space-between;
  font-size:   13px;
  color:       var(--c-text-secondary);
  padding:     4px 0;
}
.summary-row--total {
  border-top:  1px solid var(--c-border);
  margin-top:  8px;
  padding-top: 10px;
  font-size:   14px;
  font-weight: 500;
  color:       var(--c-text-primary);
}
.summary-grand-total {
  font-family:  var(--font-display);
  font-size:    22px;
  font-weight:  700;
  letter-spacing: -0.03em;
}

.checkout-submit {
  width:          100%;
  margin-top:     20px;
  padding:        14px;
  background:     var(--c-accent);
  color:          #fff;
  border:         none;
  border-radius:  var(--store-radius);
  font-family:    var(--font-display);
  font-size:      12px;
  font-weight:    700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor:         pointer;
  display:        flex;
  align-items:    center;
  justify-content: center;
  gap:            8px;
  transition:     opacity var(--t-fast), transform var(--t-fast);
}
.checkout-submit:hover:not(:disabled)  { opacity: 0.88; }
.checkout-submit:active                { transform: scale(0.98); }
.checkout-submit:disabled              { opacity: 0.4; cursor: not-allowed; }
.checkout-submit__spinner {
  width:  16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.checkout-disclaimer {
  font-size:  11px;
  color:      var(--c-text-muted);
  text-align: center;
  margin:     12px 0 0;
  line-height: 1.5;
}

.sr-only {
  position: absolute;
  width: 1px; height: 1px;
  padding: 0; margin: -1px;
  overflow: hidden; clip: rect(0,0,0,0);
  white-space: nowrap; border: 0;
}

@media (max-width: 800px) {
  .checkout-layout         { grid-template-columns: 1fr; }
  .checkout-summary        { position: static; }
  .form-grid               { grid-template-columns: 1fr; }
}
</style>
