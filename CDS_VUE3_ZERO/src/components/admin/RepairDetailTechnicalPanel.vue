<template>
  <section class="panel-card">
    <h2>Estado y costos</h2>
    <div class="form-grid two-cols">
      <label>
        <span>Estado OT</span>
        <select :value="statusDraft" @change="emit('update-status-draft', Number($event.target.value))">
          <option v-for="status in statusOptions" :key="status.id" :value="status.id">{{ status.id }} - {{ status.label }}</option>
        </select>
      </label>
      <div class="field-actions">
        <button class="btn-primary" :disabled="updatingStatus" @click="emit('update-status')">
          {{ updatingStatus ? 'Guardando...' : 'Actualizar estado' }}
        </button>
      </div>

      <label class="full"><span>Diagnostico</span><textarea :value="editForm.diagnosis" rows="3" @input="updateEditField('diagnosis', $event.target.value)"></textarea></label>
      <label class="full"><span>Trabajo realizado</span><textarea :value="editForm.work_performed" rows="3" @input="updateEditField('work_performed', $event.target.value)"></textarea></label>

      <label><span>Costo partes</span><input :value="editForm.parts_cost" type="number" min="0" @input="updateNumberField('parts_cost', $event.target.value)" /></label>
      <label><span>Costo mano de obra</span><input :value="editForm.labor_cost" type="number" min="0" @input="updateNumberField('labor_cost', $event.target.value)" /></label>
      <label><span>Costo adicional</span><input :value="editForm.additional_cost" type="number" min="0" @input="updateNumberField('additional_cost', $event.target.value)" /></label>
      <label><span>Descuento</span><input :value="editForm.discount" type="number" min="0" @input="updateNumberField('discount', $event.target.value)" /></label>
      <label><span>Total</span><input :value="editForm.total_cost" type="number" min="0" @input="updateNumberField('total_cost', $event.target.value)" /></label>
      <label><span>Abonado</span><input :value="editForm.paid_amount" type="number" min="0" @input="updateNumberField('paid_amount', $event.target.value)" /></label>
      <label>
        <span>Estado de pago</span>
        <select :value="editForm.payment_status" @change="updateEditField('payment_status', $event.target.value)">
          <option value="pending">Pendiente</option>
          <option value="partial">Parcial</option>
          <option value="paid">Pagado</option>
          <option value="refunded">Reembolsado</option>
          <option value="cancelled">Cancelado</option>
        </select>
      </label>
      <label>
        <span>Medio de pago</span>
        <select :value="editForm.payment_method" @change="updateEditField('payment_method', $event.target.value)">
          <option value="">Sin definir</option>
          <option value="cash">Efectivo</option>
          <option value="web">Web</option>
          <option value="transfer">Transferencia</option>
        </select>
      </label>
    </div>
    <div class="panel-actions">
      <button class="btn-primary" :disabled="savingRepair" @click="emit('save-repair-fields')">
        {{ savingRepair ? 'Guardando...' : 'Guardar cambios tecnicos' }}
      </button>
    </div>
  </section>
</template>

<script setup>
defineProps({
  statusOptions: {
    type: Array,
    default: () => []
  },
  statusDraft: {
    type: Number,
    default: 1
  },
  editForm: {
    type: Object,
    required: true
  },
  updatingStatus: {
    type: Boolean,
    default: false
  },
  savingRepair: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update-status-draft', 'update-edit-field', 'update-status', 'save-repair-fields'])

function updateEditField(field, value) {
  emit('update-edit-field', { field, value })
}

function updateNumberField(field, value) {
  emit('update-edit-field', { field, value: value === '' ? 0 : Number(value) })
}
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/repairDetailAdminShared.css"></style>
