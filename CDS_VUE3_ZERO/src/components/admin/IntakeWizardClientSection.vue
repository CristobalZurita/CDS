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

      <FormField
        v-model="client.phone"
        type="tel"
        label="Teléfono / WhatsApp"
        placeholder="+56912345678"
        :error="errors['client.phone']"
        required
        @blur="$emit('validate-field', 'client.phone', client.phone)"
      />

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
          placeholder="12.345.678-9"
          :error="errors['client.tax_id']"
          @blur="$emit('validate-field', 'client.tax_id', client.tax_id)"
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
import { computed } from 'vue'
import { FormField } from '@/components/composite'

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
</script>

<style scoped>
@import './intakeWizardSection.css';
</style>
