<template>
  <section id="cliente" class="form-section">
    <div class="section-header">
      <h2>1. Datos del Cliente</h2>
      <label class="toggle-existing">
        <input v-model="useExistingClientModel" type="checkbox" />
        <span>Cliente existente</span>
      </label>
    </div>

    <div v-if="useExistingClient" class="field-group">
      <FormField
        v-model="selectedClientIdModel"
        type="select"
        label="Seleccionar cliente"
        :options="clientOptions"
        placeholder="Selecciona..."
      />
    </div>

    <div class="field-grid cols-2">
      <FormField
        v-model="client.name"
        label="Nombre completo"
        placeholder="Ej: Juan Pérez"
        :error="errors['client.name']"
        required
        @blur="$emit('validate-field', 'client.name', client.name)"
      />

      <FormField
        v-model="client.email"
        type="email"
        label="Email"
        placeholder="ejemplo@correo.com"
        :error="errors['client.email']"
        required
        @blur="$emit('validate-field', 'client.email', client.email)"
      />

      <div class="field-phone-wrap">
        <label class="field-phone-label">Teléfono / WhatsApp <span class="req">*</span></label>
        <div class="field-phone-input" :class="{ 'has-error': errors['client.phone'] }">
          <span class="phone-prefix">+569</span>
          <input
            :value="phoneDigits"
            type="tel"
            inputmode="numeric"
            maxlength="8"
            placeholder="12345678"
            class="phone-digits"
            @input="onPhoneInput"
            @blur="$emit('validate-field', 'client.phone', client.phone)"
          />
        </div>
        <span v-if="errors['client.phone']" class="field-phone-error">{{ errors['client.phone'] }}</span>
      </div>

      <FormField
        v-model="client.phone_alt"
        type="tel"
        label="Teléfono alternativo (opcional)"
        placeholder="+56987654321"
      />

      <FormField
        :ref="addressFieldRef"
        v-model="client.address"
        label="Dirección"
        placeholder="Calle, número, depto"
        :error="errors['client.address']"
        required
        @blur="$emit('validate-field', 'client.address', client.address)"
      />

      <FormField
        v-model="client.city"
        label="Ciudad"
        placeholder="Ej: Santiago"
        :error="errors['client.city']"
        required
        @blur="$emit('validate-field', 'client.city', client.city)"
      />

      <FormField
        v-model="client.region"
        label="Región"
        placeholder="Ej: Metropolitana"
        :error="errors['client.region']"
        required
        @blur="$emit('validate-field', 'client.region', client.region)"
      />

      <FormField
        v-model="client.country"
        label="País"
        placeholder="Chile"
        disabled
      />
    </div>

    <div class="subsection">
      <h3>Datos de facturación (opcional)</h3>
      <div class="field-grid cols-3">
        <FormField
          v-model="client.tax_id"
          label="RUT"
          placeholder="12345678-9"
          :error="errors['client.tax_id']"
          @blur="onRutBlur"
        />

        <FormField
          v-model="client.company_name"
          label="Razón social"
          placeholder="Empresa SPA"
        />

        <FormField
          v-model="client.billing_address"
          label="Dirección de facturación"
          placeholder="Si es diferente"
        />
      </div>
    </div>

    <div class="field-group">
      <FormField
        v-model="client.notes"
        type="textarea"
        label="Notas del cliente"
        placeholder="Información adicional..."
        :rows="2"
      />
    </div>
  </section>
</template>

<script setup>
import { computed, watch } from 'vue'

function formatRut(raw) {
  const cleaned = String(raw).replace(/[^0-9kK]/g, '').toUpperCase()
  if (cleaned.length < 2) return cleaned
  const dv = cleaned.slice(-1)
  const num = cleaned.slice(0, -1)
  return num.replace(/\B(?=(\d{3})+(?!\d))/g, '.') + '-' + dv
}
import { FormField } from '@/components/composite'
import { getRegionForCity } from '@/utils/chileRegions'

const props = defineProps({
  client: {
    type: Object,
    required: true
  },
  errors: {
    type: Object,
    required: true
  },
  useExistingClient: {
    type: Boolean,
    default: false
  },
  selectedClientId: {
    type: [String, Number],
    default: ''
  },
  clientOptions: {
    type: Array,
    default: () => []
  },
  addressFieldRef: {
    type: [Function, Object],
    default: null
  }
})

const emit = defineEmits([
  'update:useExistingClient',
  'update:selectedClientId',
  'validate-field',
  'select-client'
])

const useExistingClientModel = computed({
  get: () => props.useExistingClient,
  set: (value) => emit('update:useExistingClient', value)
})

const selectedClientIdModel = computed({
  get: () => props.selectedClientId,
  set: (value) => {
    emit('update:selectedClientId', value)
    if (value) {
      emit('select-client', value)
    }
  }
})

// Teléfono: prefijo +569 fijo, solo los 8 dígitos son editables
const phoneDigits = computed(() => {
  const val = String(props.client.phone || '')
  return val.replace(/^\+?569?/, '')
})
function onPhoneInput(e) {
  const digits = String(e.target.value).replace(/\D/g, '').slice(0, 8)
  props.client.phone = '+569' + digits
}

// RUT: mientras escribe solo dígitos y K — no tocar si ya tiene formato (. o -)
watch(
  () => props.client.tax_id,
  (val) => {
    if (!val || val.includes('.') || val.includes('-')) return
    const stripped = String(val).replace(/[^0-9kK]/g, '').toUpperCase()
    if (stripped !== val) props.client.tax_id = stripped
  }
)

function onRutBlur() {
  if (props.client.tax_id) {
    props.client.tax_id = formatRut(props.client.tax_id)
  }
  emit('validate-field', 'client.tax_id', props.client.tax_id)
}

// Auto-completar región al escribir ciudad
watch(
  () => props.client.city,
  (city) => {
    const region = getRegionForCity(city)
    if (region) {
      props.client.region = region
    }
  }
)
</script>

<style scoped>
@import './intakeWizardSection.css';

.field-phone-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.field-phone-label {
  font-size: var(--cds-text-sm);
  font-weight: 600;
  color: var(--cds-text-muted);
}
.field-phone-label .req { color: var(--cds-primary); }
.field-phone-input {
  display: flex;
  align-items: center;
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-md);
  overflow: hidden;
  background: var(--cds-white);
  height: 2.75rem;
}
.field-phone-input:focus-within {
  border-color: var(--cds-primary);
}
.field-phone-input.has-error {
  border-color: var(--cds-invalid-border, #dc2626);
}
.phone-prefix {
  padding: 0 0.65rem;
  font-size: var(--cds-text-sm);
  font-weight: 600;
  color: var(--cds-text-muted);
  background: var(--cds-light-1);
  border-right: 1px solid var(--cds-border-card);
  height: 100%;
  display: flex;
  align-items: center;
  user-select: none;
  white-space: nowrap;
}
.phone-digits {
  flex: 1;
  border: none;
  outline: none;
  padding: 0 0.75rem;
  font-size: 1rem;
  background: transparent;
  color: var(--cds-text-normal);
  height: 100%;
}
.field-phone-error {
  font-size: var(--cds-text-xs);
  color: var(--cds-invalid-text, #dc2626);
}
</style>
