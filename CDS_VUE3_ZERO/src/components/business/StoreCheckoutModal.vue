<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="co-overlay"
      :class="{ 'co-overlay--blocking': submitting }"
      @click="handleOverlayClick"
    ></div>

    <div
      v-if="open"
      class="co-modal"
      role="dialog"
      aria-modal="true"
      :aria-label="submitted ? 'Pedido confirmado' : 'Confirmar pedido'"
    >
      <!-- SUCCESS -->
      <div v-if="submitted" class="co-state co-state--success">
        <i class="fas fa-check-circle co-icon co-icon--success"></i>
        <h2 class="co-title">Pedido recibido</h2>
        <p class="co-body">
          Revisa <strong>{{ submittedEmail }}</strong> para confirmar tu pedido.
        </p>
        <p class="co-body co-body--muted">
          Si no llega en 5 minutos, revisa la carpeta de spam.
        </p>
        <button class="co-btn co-btn--primary" @click="closeAndReset">
          <i class="fas fa-store"></i> Seguir comprando
        </button>
      </div>

      <!-- FORM -->
      <div v-else>
        <header class="co-header">
          <div>
            <h2 class="co-title">Confirmar pedido</h2>
            <p class="co-subtitle">
              Recibirás un email para confirmar. El taller coordina pago y despacho.
            </p>
          </div>
          <button class="co-close" @click="$emit('close')" aria-label="Cerrar">
            <i class="fas fa-times"></i>
          </button>
        </header>

        <form class="co-form" @submit.prevent="submit" novalidate autocomplete="on">

          <!-- NOMBRE -->
          <div class="co-field" :class="{ 'co-field--error': errors.nombre }">
            <label class="co-label" for="co-nombre">
              Nombre <span class="co-req" aria-hidden="true">*</span>
            </label>
            <input
              id="co-nombre"
              v-model="form.nombre"
              type="text"
              class="co-input"
              placeholder="Tu nombre completo"
              autocomplete="name"
              maxlength="80"
              @input="sanitizeNombre"
            />
            <span v-if="errors.nombre" class="co-field__error" role="alert">{{ errors.nombre }}</span>
          </div>

          <!-- EMAIL -->
          <div class="co-field" :class="{ 'co-field--error': errors.email }">
            <label class="co-label" for="co-email">
              Correo electrónico <span class="co-req" aria-hidden="true">*</span>
            </label>
            <input
              id="co-email"
              v-model="form.email"
              type="email"
              class="co-input"
              placeholder="correo@ejemplo.com"
              autocomplete="email"
              maxlength="120"
              @input="sanitizeEmail"
            />
            <span v-if="errors.email" class="co-field__error" role="alert">{{ errors.email }}</span>
          </div>

          <!-- TELEFONO -->
          <div class="co-field" :class="{ 'co-field--error': errors.phone }">
            <label class="co-label" for="co-phone-number">
              Teléfono <span class="co-req" aria-hidden="true">*</span>
            </label>
            <div class="co-phone-row">
              <select
                v-model="form.phoneCode"
                class="co-select"
                aria-label="Código de país"
                autocomplete="tel-country-code"
              >
                <option v-for="c in COUNTRY_CODES" :key="c.iso" :value="c.code">
                  {{ c.flag }} {{ c.code }} {{ c.name }}
                </option>
              </select>
              <input
                id="co-phone-number"
                v-model="form.phoneNumber"
                type="tel"
                class="co-input co-input--phone"
                placeholder="9 8765 4321"
                autocomplete="tel-national"
                maxlength="20"
                @input="sanitizePhone"
              />
            </div>
            <span v-if="errors.phone" class="co-field__error" role="alert">{{ errors.phone }}</span>
          </div>

          <!-- NOTAS -->
          <div class="co-field">
            <label class="co-label" for="co-notas">
              Notas <span class="co-optional">(opcional)</span>
            </label>
            <textarea
              id="co-notas"
              v-model="form.notas"
              class="co-textarea"
              placeholder="Detalles del pedido, instrucciones de entrega..."
              rows="2"
              maxlength="300"
              @input="sanitizeNotas"
            ></textarea>
          </div>

          <p v-if="serverError" class="co-server-error" role="alert">
            <i class="fas fa-exclamation-circle"></i> {{ serverError }}
          </p>

          <button type="submit" class="co-btn co-btn--primary" :disabled="submitting">
            <i v-if="submitting" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-paper-plane"></i>
            {{ submitting ? 'Enviando...' : 'Confirmar pedido' }}
          </button>

        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/api'
import { useShopCartStore } from '@/stores/shopCart'

const COUNTRY_CODES = [
  // Latinoamérica
  { iso: 'CL', name: 'Chile',           code: '+56',   flag: '🇨🇱' },
  { iso: 'AR', name: 'Argentina',       code: '+54',   flag: '🇦🇷' },
  { iso: 'PE', name: 'Perú',            code: '+51',   flag: '🇵🇪' },
  { iso: 'BO', name: 'Bolivia',         code: '+591',  flag: '🇧🇴' },
  { iso: 'CO', name: 'Colombia',        code: '+57',   flag: '🇨🇴' },
  { iso: 'VE', name: 'Venezuela',       code: '+58',   flag: '🇻🇪' },
  { iso: 'EC', name: 'Ecuador',         code: '+593',  flag: '🇪🇨' },
  { iso: 'UY', name: 'Uruguay',         code: '+598',  flag: '🇺🇾' },
  { iso: 'PY', name: 'Paraguay',        code: '+595',  flag: '🇵🇾' },
  { iso: 'BR', name: 'Brasil',          code: '+55',   flag: '🇧🇷' },
  { iso: 'MX', name: 'México',          code: '+52',   flag: '🇲🇽' },
  { iso: 'CU', name: 'Cuba',            code: '+53',   flag: '🇨🇺' },
  { iso: 'DO', name: 'Rep. Dominicana', code: '+1809', flag: '🇩🇴' },
  { iso: 'GT', name: 'Guatemala',       code: '+502',  flag: '🇬🇹' },
  { iso: 'SV', name: 'El Salvador',     code: '+503',  flag: '🇸🇻' },
  { iso: 'HN', name: 'Honduras',        code: '+504',  flag: '🇭🇳' },
  { iso: 'NI', name: 'Nicaragua',       code: '+505',  flag: '🇳🇮' },
  { iso: 'CR', name: 'Costa Rica',      code: '+506',  flag: '🇨🇷' },
  { iso: 'PA', name: 'Panamá',          code: '+507',  flag: '🇵🇦' },
  // Norte América
  { iso: 'US', name: 'EE.UU.',          code: '+1',    flag: '🇺🇸' },
  { iso: 'CA', name: 'Canadá',          code: '+1',    flag: '🇨🇦' },
  // Europa
  { iso: 'ES', name: 'España',          code: '+34',   flag: '🇪🇸' },
  { iso: 'GB', name: 'Reino Unido',     code: '+44',   flag: '🇬🇧' },
  { iso: 'DE', name: 'Alemania',        code: '+49',   flag: '🇩🇪' },
  { iso: 'FR', name: 'Francia',         code: '+33',   flag: '🇫🇷' },
  { iso: 'IT', name: 'Italia',          code: '+39',   flag: '🇮🇹' },
  { iso: 'PT', name: 'Portugal',        code: '+351',  flag: '🇵🇹' },
  { iso: 'NL', name: 'Países Bajos',    code: '+31',   flag: '🇳🇱' },
  { iso: 'CH', name: 'Suiza',           code: '+41',   flag: '🇨🇭' },
  { iso: 'SE', name: 'Suecia',          code: '+46',   flag: '🇸🇪' },
  // África
  { iso: 'ZA', name: 'Sudáfrica',       code: '+27',   flag: '🇿🇦' },
  { iso: 'EG', name: 'Egipto',          code: '+20',   flag: '🇪🇬' },
  { iso: 'NG', name: 'Nigeria',         code: '+234',  flag: '🇳🇬' },
  { iso: 'MA', name: 'Marruecos',       code: '+212',  flag: '🇲🇦' },
  // Asia y Oriente Medio
  { iso: 'JP', name: 'Japón',           code: '+81',   flag: '🇯🇵' },
  { iso: 'CN', name: 'China',           code: '+86',   flag: '🇨🇳' },
  { iso: 'IN', name: 'India',           code: '+91',   flag: '🇮🇳' },
  { iso: 'KR', name: 'Corea del Sur',   code: '+82',   flag: '🇰🇷' },
  { iso: 'IL', name: 'Israel',          code: '+972',  flag: '🇮🇱' },
  { iso: 'AE', name: 'Emiratos Árabes', code: '+971',  flag: '🇦🇪' },
  { iso: 'SA', name: 'Arabia Saudita',  code: '+966',  flag: '🇸🇦' },
  { iso: 'TR', name: 'Turquía',         code: '+90',   flag: '🇹🇷' },
]

defineProps({ open: { type: Boolean, default: false } })
const emit = defineEmits(['close', 'success'])
const shopCart = useShopCartStore()

const submitting = ref(false)
const submitted  = ref(false)
const submittedEmail = ref('')
const serverError = ref('')

const form = ref({ nombre: '', email: '', phoneCode: '+56', phoneNumber: '', notas: '' })
const errors = ref({ nombre: '', email: '', phone: '' })

// ── Sanitizers (replace forbidden chars as-you-type) ─────────────────────────

// Nombre: letras, tildes, ñ, espacios, guión
function sanitizeNombre() {
  form.value.nombre = form.value.nombre
    .replace(/[^a-zA-ZáéíóúüñÁÉÍÓÚÜÑ\s\-]/g, '')
}

// Email: alfanumérico + . _ - @
function sanitizeEmail() {
  form.value.email = form.value.email
    .replace(/[^a-zA-Z0-9._\-@]/g, '')
}

// Teléfono: solo dígitos, espacios y guión
function sanitizePhone() {
  form.value.phoneNumber = form.value.phoneNumber
    .replace(/[^0-9\s\-]/g, '')
}

// Notas: letras, tildes, ñ, dígitos, espacios, . , ; : - ! ?
function sanitizeNotas() {
  form.value.notas = form.value.notas
    .replace(/[^a-zA-ZáéíóúüñÁÉÍÓÚÜÑ0-9\s.,;:\-!?]/g, '')
}

// ── Validation ────────────────────────────────────────────────────────────────
function validate() {
  errors.value = { nombre: '', email: '', phone: '' }
  let ok = true

  if (form.value.nombre.trim().length < 2) {
    errors.value.nombre = 'Ingresa tu nombre (mínimo 2 caracteres)'
    ok = false
  }

  const emailRe = /^[a-zA-Z0-9._\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/
  if (!emailRe.test(form.value.email.trim())) {
    errors.value.email = 'Ingresa un correo válido (ej: correo@dominio.com)'
    ok = false
  }

  const digits = form.value.phoneNumber.replace(/\D/g, '')
  if (digits.length < 6) {
    errors.value.phone = 'Ingresa tu teléfono (mínimo 6 dígitos)'
    ok = false
  }

  return ok
}

// ── Submit ────────────────────────────────────────────────────────────────────
async function submit() {
  serverError.value = ''
  if (!validate()) return

  submitting.value = true
  try {
    const telefono = `${form.value.phoneCode} ${form.value.phoneNumber.trim()}`
    const payload = {
      nombre:         form.value.nombre.trim(),
      email:          form.value.email.trim().toLowerCase(),
      telefono,
      items:          shopCart.items.map(item => ({
                        product_id: item.id,
                        quantity:   item.qty,
                      })),
      shipping_key:   shopCart.currentShipping.key,
      shipping_label: shopCart.currentShipping.name,
      notes:          form.value.notas.trim() || null,
    }

    await api.post('/store/checkout', payload)

    submittedEmail.value = form.value.email.trim()
    shopCart.clear()
    shopCart.closeCart()
    submitted.value = true
    emit('success')
  } catch (err) {
    serverError.value =
      err?.response?.data?.detail ||
      err?.message ||
      'Error al enviar el pedido. Intenta nuevamente.'
  } finally {
    submitting.value = false
  }
}

function closeAndReset() {
  submitted.value    = false
  submittedEmail.value = ''
  serverError.value  = ''
  form.value = { nombre: '', email: '', phoneCode: '+56', phoneNumber: '', notas: '' }
  errors.value = { nombre: '', email: '', phone: '' }
  emit('close')
}

function handleOverlayClick() {
  if (submitting.value) return
  emit('close')
}
</script>

<style scoped>
/* ── Overlay ─────────────────────────────────────────────────── */
.co-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  z-index: 980;
  cursor: pointer;
}
.co-overlay--blocking {
  cursor: wait;
  pointer-events: none;
}

/* ── Modal shell ─────────────────────────────────────────────── */
.co-modal {
  position: fixed;
  inset: 0;
  margin: auto;
  width: min(480px, calc(100vw - 2rem));
  max-height: calc(100dvh - 2rem);
  overflow-y: auto;
  z-index: 990;
  background: var(--cds-surface-1);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-lg);
  box-shadow: 0 24px 64px rgba(10, 8, 5, 0.42);
  display: flex;
  flex-direction: column;
  font-family: var(--layout-public-font-family-base, var(--cds-font-family-base), sans-serif);
}

/* ── Header ──────────────────────────────────────────────────── */
.co-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.4rem 1.5rem 0;
}

.co-title {
  margin: 0;
  font-family: var(--layout-public-font-family-heading, var(--layout-public-font-family-base, var(--cds-font-family-base)));
  font-size: var(--cds-text-xl);
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--cds-dark);
  line-height: 1.1;
}

.co-subtitle {
  margin: 0.3rem 0 0;
  font-size: var(--layout-public-text-meta, 0.9rem);
  color: var(--cds-text-muted);
  line-height: 1.5;
}

.co-close {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  border: 1px solid var(--cds-border-card);
  border-radius: 50%;
  background: transparent;
  color: var(--cds-text-muted);
  font-size: 0.9rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s;
}
.co-close:hover { background: var(--cds-surface-2); color: var(--cds-dark); }

/* ── Form ────────────────────────────────────────────────────── */
.co-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.25rem 1.5rem 1.5rem;
}

.co-field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.co-label {
  font-size: var(--layout-public-text-meta, 0.9rem);
  font-weight: 600;
  color: var(--cds-dark);
  line-height: 1.3;
}
.co-req { color: var(--cds-primary); font-weight: 700; }
.co-optional { font-weight: 400; color: var(--cds-text-muted); font-size: 0.85em; }

.co-input,
.co-select,
.co-textarea {
  width: 100%;
  min-height: 44px;
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--cds-border-input);
  border-radius: var(--cds-radius-sm);
  background: var(--cds-surface-2);
  color: var(--cds-dark);
  font-size: 1rem;
  font-family: inherit;
  line-height: 1.5;
  box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.co-input:focus,
.co-select:focus,
.co-textarea:focus {
  outline: none;
  border-color: var(--cds-primary);
  box-shadow: 0 0 0 2px rgba(236, 107, 0, 0.18);
}
.co-field--error .co-input,
.co-field--error .co-select,
.co-input--error { border-color: var(--cds-invalid-border); }

.co-textarea {
  min-height: 72px;
  resize: vertical;
}

/* Phone row */
.co-phone-row {
  display: flex;
  gap: 0.5rem;
}
.co-select {
  flex: 0 0 auto;
  width: auto;
  max-width: 160px;
  padding-right: 1.6rem;
  cursor: pointer;
}
.co-input--phone { flex: 1 1 0; min-width: 0; }

/* Field error message */
.co-field__error {
  font-size: var(--layout-public-text-label, 0.82rem);
  color: var(--cds-invalid-text);
  line-height: 1.3;
}

/* Server error */
.co-server-error {
  margin: 0;
  padding: 0.65rem 0.85rem;
  border-radius: var(--cds-radius-sm);
  border: 1px solid var(--cds-invalid-border);
  background: rgba(220, 38, 38, 0.07);
  color: var(--cds-invalid-text);
  font-size: var(--layout-public-text-meta, 0.9rem);
  line-height: 1.5;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Button */
.co-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  min-height: 44px;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: var(--cds-radius-sm);
  font-size: var(--layout-public-text-body, 1rem);
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s, transform 0.12s;
}
.co-btn--primary {
  background: var(--cds-primary);
  color: var(--cds-white);
  width: 100%;
}
.co-btn--primary:hover:not(:disabled) {
  background: var(--cds-dark);
  transform: translateY(-1px);
}
.co-btn--primary:disabled {
  opacity: 0.55;
  cursor: default;
}

/* ── Success state ───────────────────────────────────────────── */
.co-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.9rem;
  text-align: center;
  padding: 2.5rem 2rem;
}
.co-icon { font-size: 3.2rem; line-height: 1; }
.co-icon--success { color: var(--cds-valid-text, #1a7f4b); }

.co-body {
  margin: 0;
  font-size: var(--layout-public-text-body, 1rem);
  color: var(--cds-dark);
  line-height: 1.6;
}
.co-body--muted { color: var(--cds-text-muted); font-size: var(--layout-public-text-meta, 0.9rem); }
</style>
