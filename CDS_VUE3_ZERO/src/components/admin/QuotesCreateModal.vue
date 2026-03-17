<template>
  <div v-if="open" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content">
      <header class="modal-header">
        <h2>Nueva Cotización</h2>
        <button class="modal-close" @click="emit('close')">×</button>
      </header>

      <form class="modal-form" @submit.prevent="emit('submit')">
        <div class="form-grid">
          <div class="form-group full">
            <label>Nombre del cliente *</label>
            <input :value="quote.client_name" type="text" placeholder="Ej: Juan Pérez" required @input="updateField('client_name', $event.target.value)" />
          </div>

          <div class="form-group">
            <label>Email *</label>
            <input :value="quote.client_email" type="email" placeholder="ejemplo@correo.com" required @input="updateField('client_email', $event.target.value)" />
          </div>

          <div class="form-group">
            <label>Teléfono</label>
            <input :value="quote.client_phone" type="tel" placeholder="+56912345678" @input="updateField('client_phone', $event.target.value)" />
          </div>

          <div class="form-group full">
            <label>Descripción del problema *</label>
            <textarea :value="quote.problem_description" placeholder="Describa el problema del equipo..." rows="3" required @input="updateField('problem_description', $event.target.value)"></textarea>
          </div>

          <div class="form-group full">
            <label>Diagnóstico (opcional)</label>
            <textarea :value="quote.diagnosis" placeholder="Su diagnóstico técnico preliminar..." rows="2" @input="updateField('diagnosis', $event.target.value)"></textarea>
          </div>

          <div class="form-group">
            <label>Costo repuestos (CLP)</label>
            <input :value="quote.estimated_parts_cost" type="number" min="0" step="1000" placeholder="0" @input="updateNumberField('estimated_parts_cost', $event.target.value)" />
          </div>

          <div class="form-group">
            <label>Costo mano de obra (CLP)</label>
            <input :value="quote.estimated_labor_cost" type="number" min="0" step="1000" placeholder="0" @input="updateNumberField('estimated_labor_cost', $event.target.value)" />
          </div>

          <div class="form-group">
            <label>Total estimado * (CLP)</label>
            <input :value="quote.estimated_total" type="number" min="0" step="1000" placeholder="0" required @input="updateNumberField('estimated_total', $event.target.value)" />
          </div>

          <div class="form-group">
            <label>Válida hasta</label>
            <input :value="quote.valid_until" type="date" @input="updateField('valid_until', $event.target.value)" />
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-secondary" @click="emit('close')">Cancelar</button>
          <button type="submit" class="btn-primary" :disabled="isCreating">
            {{ isCreating ? 'Creando...' : 'Crear Cotización' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
defineProps({
  open: {
    type: Boolean,
    default: false
  },
  quote: {
    type: Object,
    required: true
  },
  isCreating: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'submit', 'update-field'])

function updateField(field, value) {
  emit('update-field', { field, value })
}

function updateNumberField(field, value) {
  emit('update-field', { field, value: Number(value || 0) })
}
</script>

<style scoped src="@/pages/admin/commonAdminPage.css"></style>
<style scoped src="@/pages/admin/quotesPageShared.css"></style>
