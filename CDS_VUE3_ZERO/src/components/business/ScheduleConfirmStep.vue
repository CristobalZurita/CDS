<template>
  <div class="schedule-step">
    <h2>Confirmar Cita</h2>
    <div class="confirmation-card">
      <div class="confirmation-section">
        <span class="label">Fecha:</span>
        <span class="value">{{ formatDate(selectedDate) }}</span>
      </div>
      <div class="confirmation-section">
        <span class="label">Hora:</span>
        <span class="value">{{ selectedTime }}</span>
      </div>
      <div class="confirmation-info">
        <p><strong>Duración estimada:</strong> 20-30 minutos.</p>
        <p><strong>Importante:</strong> Trae el instrumento y accesorios asociados.</p>
      </div>
      <p v-if="!contactDetailsComplete" class="schedule-warning">
        Debes tener correo y teléfono en tu perfil para confirmar la cita.
      </p>
      <label class="checkbox-container">
        <input :checked="agreeConditions" type="checkbox" @change="$emit('update:agree-conditions', $event.target.checked)" />
        <span>Acepto los términos y condiciones de esta cita</span>
      </label>
    </div>

    <TurnstileWidget :key="turnstileRenderKey" @verify="$emit('verify', $event)" />

    <p v-if="submissionError" class="schedule-error" data-testid="schedule-error">
      {{ submissionError }}
    </p>

    <div class="step-actions">
      <button class="btn-secondary" @click="$emit('back')">← Atrás</button>
      <button
        class="btn-primary"
        data-testid="schedule-confirm"
        :disabled="isSubmitting || !agreeConditions || !turnstileToken || !contactDetailsComplete"
        @click="$emit('confirm')"
      >
        {{ isSubmitting ? 'Confirmando...' : 'Confirmar Cita' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import TurnstileWidget from '@/components/widgets/TurnstileWidget.vue'

defineProps({
  selectedDate: { type: Date, default: null },
  selectedTime: { type: String, default: '' },
  formatDate: { type: Function, required: true },
  contactDetailsComplete: { type: Boolean, default: false },
  agreeConditions: { type: Boolean, default: false },
  turnstileToken: { type: String, default: '' },
  turnstileRenderKey: { type: Number, default: 0 },
  submissionError: { type: String, default: '' },
  isSubmitting: { type: Boolean, default: false }
})

defineEmits(['back', 'verify', 'confirm', 'update:agree-conditions'])
</script>

<style scoped src="./schedulePageShared.css"></style>
