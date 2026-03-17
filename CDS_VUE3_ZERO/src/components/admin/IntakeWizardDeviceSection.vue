<template>
  <section id="equipo" class="form-section">
    <div class="section-header">
      <h2>2. Datos del Equipo</h2>
    </div>

    <div class="field-grid cols-2">
      <FormField
        v-model="device.brand_other"
        label="Marca"
        placeholder="Ej: Korg, Roland, Yamaha"
        :error="errors['device.brand_other']"
        required
        @blur="$emit('validate-field', 'device.brand_other', device.brand_other)"
      />

      <FormField
        v-model="device.model"
        label="Modelo"
        placeholder="Ej: MS-20, Juno-106"
        :error="errors['device.model']"
        required
        @blur="$emit('validate-field', 'device.model', device.model)"
      />

      <FormField
        v-model="device.serial_number"
        label="Número de serie"
        placeholder="SN123456789"
      />

      <FormField
        v-model="device.year_manufactured"
        type="number"
        label="Año de fabricación"
        placeholder="2020"
        :min="1950"
        :max="2030"
      />

      <FormField
        v-model="device.accessories"
        label="Accesorios entregados"
        placeholder="Cable, manual, fuente..."
      />
    </div>

    <div class="field-group">
      <FormField
        v-model="device.condition_notes"
        type="textarea"
        label="Estado físico del equipo"
        placeholder="Describa el estado: rayones, golpes, piezas faltantes..."
        :error="errors['device.condition_notes']"
        required
        :rows="3"
        @blur="$emit('validate-field', 'device.condition_notes', device.condition_notes)"
      />
    </div>

    <div class="field-group">
      <FormField
        v-model="device.description"
        type="textarea"
        label="Descripción adicional (opcional)"
        placeholder="Modificaciones, historia, etc."
        :rows="2"
      />
    </div>

    <div class="subsection">
      <h3>Fotos del equipo</h3>
      <PhotoUpload
        v-model="device.photos"
        :max="5"
        description="Fotos del estado inicial del equipo"
      />
    </div>
  </section>
</template>

<script setup>
import { FormField } from '@/components/composite'
import PhotoUpload from '@/components/business/PhotoUpload.vue'

defineProps({
  device: {
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
