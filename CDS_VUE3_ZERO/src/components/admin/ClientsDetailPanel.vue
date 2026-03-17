<template>
  <article class="detail-panel">
    <template v-if="selectedClient">
      <div class="detail-head">
        <div>
          <h3>{{ selectedClient.name }}</h3>
          <p>{{ selectedClient.client_code }} · {{ selectedClient.email || 'Sin email' }}</p>
        </div>
        <div class="header-actions">
          <button class="btn-secondary" :disabled="contextLoading" @click="emit('toggle-device-form')">
            {{ showDeviceForm ? 'Cerrar dispositivo' : 'Agregar dispositivo' }}
          </button>
          <button class="btn-secondary" :disabled="contextLoading" @click="emit('toggle-repair-form')">
            {{ showRepairForm ? 'Cerrar OT' : 'Crear OT' }}
          </button>
          <button class="btn-danger" :disabled="loading" @click="emit('delete-client')">Eliminar</button>
        </div>
      </div>

      <div class="summary-grid">
        <article class="summary-card">
          <span>Telefono</span>
          <strong>{{ selectedClient.phone || '—' }}</strong>
        </article>
        <article class="summary-card">
          <span>Reparaciones</span>
          <strong>{{ selectedClient.total_repairs }}</strong>
        </article>
        <article class="summary-card">
          <span>Total gastado</span>
          <strong>{{ formatMoney(selectedClient.total_spent) }}</strong>
        </article>
      </div>

      <section v-if="showEditForm" class="panel-nested">
        <h4>Editar cliente</h4>
        <div class="form-grid two-cols">
          <label><span>Nombre *</span><input :value="editForm.name" type="text" @input="updateEditField('name', $event.target.value)" /></label>
          <label><span>Email</span><input :value="editForm.email" type="email" @input="updateEditField('email', $event.target.value)" /></label>
          <label><span>Telefono</span><input :value="editForm.phone" type="text" @input="updateEditField('phone', $event.target.value)" /></label>
          <label><span>Telefono alterno</span><input :value="editForm.phone_alt" type="text" @input="updateEditField('phone_alt', $event.target.value)" /></label>
          <label><span>Ciudad</span><input :value="editForm.city" type="text" @input="updateEditField('city', $event.target.value)" /></label>
          <label><span>Region</span><input :value="editForm.region" type="text" @input="updateEditField('region', $event.target.value)" /></label>
          <label><span>Pais</span><input :value="editForm.country" type="text" @input="updateEditField('country', $event.target.value)" /></label>
          <label class="full"><span>Direccion</span><input :ref="editAddressRef" :value="editForm.address" type="text" @input="updateEditField('address', $event.target.value)" /></label>
          <label class="full"><span>Notas</span><textarea :value="editForm.notes" rows="3" @input="updateEditField('notes', $event.target.value)"></textarea></label>
          <label class="full"><span>Notas internas</span><textarea :value="editForm.internal_notes" rows="3" @input="updateEditField('internal_notes', $event.target.value)"></textarea></label>
        </div>
        <div class="panel-actions">
          <button class="btn-primary" :disabled="loading" @click="emit('update-client')">Guardar cambios</button>
        </div>
      </section>

      <section v-if="showDeviceForm" class="panel-nested">
        <h4>Nuevo dispositivo</h4>
        <div class="form-grid two-cols">
          <label><span>Modelo *</span><input :value="deviceForm.model" type="text" @input="updateDeviceField('model', $event.target.value)" /></label>
          <label><span>Marca</span><input :value="deviceForm.brand_other" type="text" @input="updateDeviceField('brand_other', $event.target.value)" /></label>
          <label><span>Serial</span><input :value="deviceForm.serial_number" type="text" @input="updateDeviceField('serial_number', $event.target.value)" /></label>
          <label class="full"><span>Descripcion</span><textarea :value="deviceForm.description" rows="2" @input="updateDeviceField('description', $event.target.value)"></textarea></label>
          <label class="full"><span>Condicion</span><textarea :value="deviceForm.condition_notes" rows="2" @input="updateDeviceField('condition_notes', $event.target.value)"></textarea></label>
        </div>
        <div class="panel-actions">
          <button class="btn-primary" :disabled="contextLoading" @click="emit('create-device')">
            {{ contextLoading ? 'Guardando...' : 'Guardar dispositivo' }}
          </button>
        </div>
      </section>

      <section v-if="showRepairForm" class="panel-nested">
        <h4>Nueva orden de trabajo</h4>
        <div class="form-grid two-cols">
          <label>
            <span>Dispositivo</span>
            <select :value="repairForm.device_id" @change="updateRepairField('device_id', $event.target.value)">
              <option value="">Sin seleccionar</option>
              <option v-for="device in devices" :key="device.id" :value="device.id">
                {{ device.model || `Dispositivo #${device.id}` }}
              </option>
            </select>
          </label>
          <label>
            <span>Prioridad</span>
            <select :value="repairForm.priority" @change="updateRepairField('priority', Number($event.target.value))">
              <option :value="1">Alta</option>
              <option :value="2">Normal</option>
              <option :value="3">Baja</option>
            </select>
          </label>
          <label class="full"><span>Problema reportado *</span><textarea :value="repairForm.problem_reported" rows="3" @input="updateRepairField('problem_reported', $event.target.value)"></textarea></label>
          <label><span>Abono (CLP)</span><input :value="repairForm.paid_amount" type="number" min="0" @input="updateRepairField('paid_amount', toNumberOrEmpty($event.target.value))" /></label>
          <label>
            <span>Medio de pago</span>
            <select :value="repairForm.payment_method" @change="updateRepairField('payment_method', $event.target.value)">
              <option value="cash">Efectivo</option>
              <option value="web">Web</option>
              <option value="transfer">Transferencia</option>
            </select>
          </label>
          <label class="checkbox-row full"><input :checked="repairForm.group_with_ot" type="checkbox" @change="updateRepairField('group_with_ot', $event.target.checked)" /><span>Agrupar con OT existente</span></label>
          <label v-if="repairForm.group_with_ot" class="full">
            <span>OT base</span>
            <select :value="repairForm.ot_parent_id" @change="updateRepairField('ot_parent_id', $event.target.value)">
              <option value="">Seleccionar OT base</option>
              <option v-for="item in repairs" :key="item.id" :value="item.id">
                {{ item.repair_code || `OT #${item.id}` }}
              </option>
            </select>
          </label>
        </div>
        <div class="panel-actions">
          <button class="btn-primary" :disabled="contextLoading" @click="emit('create-repair')">
            {{ contextLoading ? 'Creando...' : 'Crear OT' }}
          </button>
        </div>
      </section>

      <section class="panel-nested">
        <h4>Dispositivos ({{ devices.length }})</h4>
        <p v-if="devices.length === 0" class="empty-state">No hay dispositivos registrados.</p>
        <div v-else class="table-wrap">
          <table>
            <thead><tr><th>ID</th><th>Modelo</th><th>Marca</th><th>Serial</th></tr></thead>
            <tbody>
              <tr v-for="device in devices" :key="device.id">
                <td>{{ device.id }}</td>
                <td>{{ device.model || '—' }}</td>
                <td>{{ device.brand_other || '—' }}</td>
                <td>{{ device.serial_number || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="panel-nested">
        <h4>OT activas ({{ repairs.length }})</h4>
        <p v-if="repairs.length === 0" class="empty-state">No hay OT activas para este cliente.</p>
        <div v-else class="table-wrap">
          <table>
            <thead><tr><th>OT</th><th>Estado</th><th>Problema</th><th>Creada</th></tr></thead>
            <tbody>
              <tr v-for="item in repairs" :key="item.id">
                <td>{{ item.repair_code || item.repair_number }}</td>
                <td>{{ item.status_id || '—' }}</td>
                <td>{{ item.problem_reported || '—' }}</td>
                <td>{{ formatDate(item.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>

    <div v-else class="empty-state">Selecciona un cliente para ver detalle.</div>
  </article>
</template>

<script setup>
const moneyFormatter = new Intl.NumberFormat('es-CL')

defineProps({
  selectedClient: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  contextLoading: {
    type: Boolean,
    default: false
  },
  showEditForm: {
    type: Boolean,
    default: false
  },
  showDeviceForm: {
    type: Boolean,
    default: false
  },
  showRepairForm: {
    type: Boolean,
    default: false
  },
  editForm: {
    type: Object,
    required: true
  },
  deviceForm: {
    type: Object,
    required: true
  },
  repairForm: {
    type: Object,
    required: true
  },
  devices: {
    type: Array,
    default: () => []
  },
  repairs: {
    type: Array,
    default: () => []
  },
  editAddressRef: {
    type: Function,
    required: true
  }
})

const emit = defineEmits([
  'toggle-device-form',
  'toggle-repair-form',
  'delete-client',
  'update-client',
  'create-device',
  'create-repair',
  'update-edit-field',
  'update-device-field',
  'update-repair-field'
])

function updateEditField(field, value) {
  emit('update-edit-field', { field, value })
}

function updateDeviceField(field, value) {
  emit('update-device-field', { field, value })
}

function updateRepairField(field, value) {
  emit('update-repair-field', { field, value })
}

function formatMoney(value) {
  return moneyFormatter.format(Number(value || 0))
}

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString('es-CL') : '—'
}

function toNumberOrEmpty(value) {
  return value === '' ? '' : Number(value)
}
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/clientsPageShared.css"></style>
