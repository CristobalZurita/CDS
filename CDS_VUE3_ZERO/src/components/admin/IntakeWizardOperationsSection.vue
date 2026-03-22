<template>
  <section id="operaciones" class="form-section">
    <div class="section-header">
      <h2>4. Planificación</h2>
    </div>

    <div class="field-grid cols-2">
      <FormField
        v-model="intake.requested_service_type"
        type="select"
        label="Tipo de servicio"
        :options="[
          { value: 'emergency', label: 'Reparación de emergencia' },
          { value: 'maintenance', label: 'Mantenimiento general' }
        ]"
      />

      <FormField
        v-model="intake.estimated_completion_date"
        type="date"
        label="Fecha estimada de entrega"
      />
    </div>

    <div class="field-group">
      <FormField
        v-model="intake.failure_cause"
        type="textarea"
        label="Diagnóstico técnico"
        placeholder="Causa raíz del problema (puede completarse después del diagnóstico)..."
        :rows="3"
      />
    </div>

    <div class="field-group">
      <FormField
        v-model="intake.annotations"
        type="textarea"
        label="Notas internas"
        placeholder="Observaciones, advertencias, acuerdos especiales..."
        :rows="3"
      />
    </div>
  </section>
</template>

<script setup>
import { FormField } from '@/components/composite'

defineProps({
  intake: {
    type: Object,
    required: true
  },
  errors: {
    type: Object,
    required: true
  }
})

defineEmits(['validate-field'])
</script>

<style scoped>
@import './intakeWizardSection.css';
</style>
