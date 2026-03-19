<template>
  <div class="cotizador-card">
    <template v-if="!leadSubmitted">
      <CotizadorStepHeader
        :badge="notFoundMode ? 'Paso 2 de 2' : 'Paso 4 de 4'"
        title="Tus datos de contacto"
      >
        <template #description>
          Te contactaremos para coordinar la revisión de tu equipo.
        </template>
      </CotizadorStepHeader>

      <div class="form-grid">
        <label class="field">
          <span>Nombre completo <em class="required">*</em></span>
          <input
            v-model.trim="nombreModel"
            type="text"
            autocomplete="name"
            placeholder="Tu nombre"
          />
          <small v-if="firstError('nombre')" class="field-error">{{ firstError('nombre') }}</small>
        </label>

        <label class="field">
          <span>Email <em class="required">*</em></span>
          <input
            v-model.trim="emailModel"
            type="email"
            autocomplete="email"
            placeholder="correo@dominio.com"
          />
          <small v-if="firstError('email')" class="field-error">{{ firstError('email') }}</small>
        </label>

        <label class="field">
          <span>Teléfono <em class="optional">(opcional)</em></span>
          <input
            v-model.trim="telefonoModel"
            type="tel"
            autocomplete="tel"
            placeholder="+56 9 1234 5678"
          />
          <small v-if="firstError('telefono')" class="field-error">{{ firstError('telefono') }}</small>
        </label>
      </div>

      <label class="checkbox-row">
        <input v-model="acceptedDisclaimerModel" type="checkbox" />
        <span>Acepto las condiciones del servicio de cotización referencial</span>
      </label>
      <small v-if="firstError('acceptedDisclaimer')" class="field-error">
        {{ firstError('acceptedDisclaimer') }}
      </small>

      <TurnstileWidget
        :key="leadTurnstileRenderKey"
        @verify="emit('lead-verify', $event)"
      />

      <div class="actions">
        <button class="btn-secondary" @click="emit('back')">← Atrás</button>
        <button
          class="btn-primary"
          :disabled="!canSubmitValidated || loading"
          @click="handleSubmit"
        >
          <span v-if="loading"><span class="spinner spinner--sm"></span> Enviando…</span>
          <span v-else>Enviar y agendar</span>
        </button>
      </div>
    </template>

    <template v-else>
      <CotizadorLeadSuccess
        :lead-name="leadForm.nombre"
        :selected-brand-name="selectedBrandName"
        :selected-model-name="selectedModelName"
        :formatted-final-cost="formattedFinalCost"
        :not-found-mode="notFoundMode"
      />

      <div class="actions actions--center">
        <button class="btn-secondary" @click="emit('reset')">Nueva cotización</button>
        <button class="btn-primary" @click="emit('schedule')">Agendar ahora</button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import CotizadorLeadSuccess from '@/components/business/CotizadorLeadSuccess.vue'
import CotizadorStepHeader from '@/components/business/CotizadorStepHeader.vue'
import TurnstileWidget from '@/components/widgets/TurnstileWidget.vue'
import { quotationLeadSchema } from '@/validation/schemas/quotationLeadSchema'

const props = defineProps({
  leadSubmitted: {
    type: Boolean,
    default: false
  },
  notFoundMode: {
    type: Boolean,
    default: false
  },
  leadForm: {
    type: Object,
    required: true
  },
  acceptedDisclaimer: {
    type: Boolean,
    default: false
  },
  leadTurnstileRenderKey: {
    type: Number,
    default: 0
  },
  canSubmitLead: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  selectedBrandName: {
    type: String,
    required: true
  },
  selectedModelName: {
    type: String,
    required: true
  },
  formattedFinalCost: {
    type: String,
    required: true
  }
})

const emit = defineEmits([
  'update-lead-field',
  'update:acceptedDisclaimer',
  'lead-verify',
  'back',
  'submit',
  'reset',
  'schedule'
])

function updateLeadField(field, value) {
  emit('update-lead-field', { field, value })
}

const nombreModel = computed({
  get: () => props.leadForm.nombre,
  set: (value) => updateLeadField('nombre', value)
})

const emailModel = computed({
  get: () => props.leadForm.email,
  set: (value) => updateLeadField('email', value)
})

const telefonoModel = computed({
  get: () => props.leadForm.telefono,
  set: (value) => updateLeadField('telefono', value)
})

const acceptedDisclaimerModel = computed({
  get: () => props.acceptedDisclaimer,
  set: (value) => emit('update:acceptedDisclaimer', value)
})

const validationResult = computed(() => quotationLeadSchema.safeParse({
  nombre: props.leadForm?.nombre,
  email: props.leadForm?.email,
  telefono: props.leadForm?.telefono,
  acceptedDisclaimer: props.acceptedDisclaimer,
}))

const submitAttempted = ref(false)

const fieldErrors = computed(() => {
  if (validationResult.value.success) return {}
  return validationResult.value.error.flatten().fieldErrors
})

const visibleFieldErrors = computed(() => (submitAttempted.value ? fieldErrors.value : {}))
const canSubmitValidated = computed(() => props.canSubmitLead && validationResult.value.success)

function firstError(fieldName) {
  return visibleFieldErrors.value?.[fieldName]?.[0] || ''
}

function handleSubmit() {
  submitAttempted.value = true
  if (!canSubmitValidated.value) return
  emit('submit')
}
</script>

<style scoped>
@import './cotizadorStepShared.css';

.field-error {
  display: block;
  margin-top: 0.35rem;
  font-size: var(--cds-text-xs);
  color: var(--cds-primary);
}
</style>
