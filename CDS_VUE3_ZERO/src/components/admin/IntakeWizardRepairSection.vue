<template>
  <section id="ot" class="form-section">
    <div class="section-header">
      <h2>3. Orden de Trabajo</h2>
    </div>

    <div class="field-group">
      <FormField
        v-model="repair.problem_reported"
        type="textarea"
        label="Problema reportado"
        placeholder="Describa detalladamente el problema que presenta el equipo..."
        :error="errors['repair.problem_reported']"
        required
        :rows="4"
        @blur="$emit('validate-field', 'repair.problem_reported', repair.problem_reported)"
      />
    </div>

    <div class="field-group">
      <FormField
        v-model="repair.diagnosis"
        type="textarea"
        label="Diagnóstico inicial (opcional)"
        placeholder="Si ya tiene una idea del problema..."
        :rows="3"
      />
    </div>

    <div class="field-grid cols-3">
      <FormField
        v-model="repair.priority"
        type="select"
        label="Prioridad"
        :options="[
          { value: 1, label: 'Alta' },
          { value: 2, label: 'Normal' },
          { value: 3, label: 'Baja' }
        ]"
        required
      />

      <FormField
        v-model="repair.paid_amount"
        type="number"
        label="Abono (CLP)"
        :min="0"
        :step="1000"
        :error="errors['repair.paid_amount']"
        required
      />

      <FormField
        v-model="repair.payment_method"
        type="select"
        label="Método de pago"
        :options="[
          { value: 'cash', label: 'Efectivo' },
          { value: 'transfer', label: 'Transferencia' },
          { value: 'web', label: 'Web' }
        ]"
        required
      />
    </div>

    <div class="field-group">
      <FormField
        v-model="repair.warranty_days"
        type="number"
        label="Días de garantía"
        :min="0"
        :max="365"
      />
    </div>
  </section>
</template>

<script setup>
import { FormField } from '@/components/composite'

defineProps({
  repair: {
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
