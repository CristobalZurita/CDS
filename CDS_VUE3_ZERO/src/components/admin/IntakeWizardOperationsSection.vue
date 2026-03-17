<template>
  <section id="operaciones" class="form-section">
    <div class="section-header">
      <h2>4. Planilla de Operaciones y Mantenimiento</h2>
    </div>

    <div class="field-grid cols-2">
      <FormField
        v-model="intake.equipment_name"
        label="Nombre del dispositivo"
        placeholder="Nombre técnico del equipo"
        :error="errors['intake.equipment_name']"
        required
        @blur="$emit('validate-field', 'intake.equipment_name', intake.equipment_name)"
      />

      <FormField
        v-model="intake.equipment_model"
        label="Modelo del dispositivo"
        placeholder="Si difiere del modelo comercial"
      />

      <FormField
        v-model="intake.equipment_type"
        type="select"
        label="Tipo de equipo"
        :options="[
          { value: 'general', label: 'Equipo general' },
          { value: 'precision', label: 'Equipo de precisión' }
        ]"
      />

      <FormField
        v-model="intake.requested_service_type"
        type="select"
        label="Tipo de servicio"
        :options="[
          { value: 'emergency', label: 'Reparación de emergencia' },
          { value: 'maintenance', label: 'Mantenimiento general' }
        ]"
      />
    </div>

    <div class="field-group">
      <FormField
        v-model="intake.failure_cause"
        type="textarea"
        label="Causa del problema"
        placeholder="Descripción técnica de la causa del fallo..."
        :error="errors['intake.failure_cause']"
        required
        :rows="3"
        @blur="$emit('validate-field', 'intake.failure_cause', intake.failure_cause)"
      />
    </div>

    <div class="field-grid cols-3">
      <FormField
        v-model="intake.estimated_repair_time"
        label="Tiempo estimado"
        placeholder="Ej: 7 días hábiles"
      />

      <FormField
        v-model="intake.estimated_completion_date"
        type="date"
        label="Fecha estimada de término"
      />

      <FormField
        v-model="intake.tabulator_name"
        label="Nombre del tabulador"
        placeholder="Quien llena esta planilla"
      />
    </div>

    <div class="subsection">
      <h3>Firmas y aprobaciones</h3>
      <div class="field-grid cols-2">
        <FormField
          v-model="intake.operation_department_signed_by"
          label="Departamento de Operaciones"
          placeholder="Nombre y firma"
        />

        <FormField
          v-model="intake.finance_department_signed_by"
          label="Departamento de Finanzas"
          placeholder="Nombre y firma"
        />

        <FormField
          v-model="intake.factory_director_signed_by"
          label="Director de Fábrica"
          placeholder="Nombre y firma"
        />

        <FormField
          v-model="intake.general_manager_signed_by"
          label="Gerente General"
          placeholder="Nombre y firma"
        />
      </div>
    </div>

    <div class="field-group">
      <FormField
        v-model="intake.annotations"
        type="textarea"
        label="Anotaciones operativas"
        placeholder="Observaciones adicionales..."
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
