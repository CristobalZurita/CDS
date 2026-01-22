<template>
  <section class="client-detail">
    <div v-if="!client.id" class="text-muted text-center py-4">
      <i class="fa-solid fa-user-large fa-2x mb-2"></i>
      <p>Selecciona un cliente</p>
    </div>

    <div v-else>
      <!-- Client Info -->
      <div class="client-info mb-4">
        <div class="d-flex justify-content-between align-items-start mb-2">
          <h4 class="mb-0">{{ client.name || 'Cliente' }}</h4>
          <span v-if="client.client_code" class="client-code">{{ client.client_code }}</span>
        </div>
        <div class="info-row">
          <i class="fa-solid fa-envelope"></i>
          <span>{{ client.email || 'Sin correo' }}</span>
        </div>
        <div class="info-row">
          <i class="fa-solid fa-phone"></i>
          <span>{{ client.phone || 'Sin telefono' }}</span>
        </div>
        <div v-if="client.address" class="info-row">
          <i class="fa-solid fa-location-dot"></i>
          <span>{{ client.address }}</span>
        </div>
        <div v-if="client.notes" class="info-row">
          <i class="fa-solid fa-note-sticky"></i>
          <span>{{ client.notes }}</span>
        </div>
        <div class="stats-row mt-3">
          <span class="stat-badge">
            <i class="fa-solid fa-screwdriver-wrench"></i>
            {{ client.total_repairs || 0 }} reparaciones
          </span>
          <span class="stat-badge">
            <i class="fa-solid fa-money-bill"></i>
            ${{ formatNumber(client.total_spent || 0) }}
          </span>
        </div>
      </div>

      <!-- Devices Section -->
        <div class="devices-section">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 class="mb-0"><i class="fa-solid fa-keyboard me-2"></i>Dispositivos</h5>
          <button class="btn btn-sm btn-primary" @click="showAddDevice = !showAddDevice">
            <i class="fa-solid fa-plus me-1"></i> Agregar
          </button>
        </div>

        <!-- Add Device Form -->
        <div v-if="showAddDevice" class="add-device-form mb-3 p-3 border rounded">
          <div class="mb-2">
            <label class="form-label">Marca</label>
            <input v-model="newDevice.brand_other" type="text" class="form-control" placeholder="Ej: Korg" />
          </div>
          <div class="mb-2">
            <label class="form-label">Modelo/Nombre</label>
            <input v-model="newDevice.model" type="text" class="form-control" placeholder="Ej: Korg MS-20" />
          </div>
          <div class="mb-2">
            <label class="form-label">Numero de serie (opcional)</label>
            <input v-model="newDevice.serial_number" type="text" class="form-control" placeholder="Ej: SN123456" />
          </div>
          <div class="mb-2">
            <label class="form-label">Accesorios / Detalles de entrada (opcional)</label>
            <textarea v-model="newDevice.description" class="form-control" rows="2" placeholder="Fundas, cables, fuente, piezas faltantes..."></textarea>
          </div>
          <div class="mb-2">
            <label class="form-label">Estado visual / condición (opcional)</label>
            <textarea v-model="newDevice.condition_notes" class="form-control" rows="2" placeholder="Golpes, roturas, teclas faltantes, etc."></textarea>
          </div>
          <button class="btn btn-success btn-sm" :disabled="!newDevice.model || savingDevice" @click="addDevice">
            {{ savingDevice ? 'Guardando...' : 'Guardar' }}
          </button>
          <button class="btn btn-outline-secondary btn-sm ms-2" @click="showAddDevice = false">Cancelar</button>
        </div>

        <!-- Devices List -->
        <div v-if="devices.length > 0" class="devices-list">
          <div v-for="device in devices" :key="device.id" class="device-item">
            <div class="device-icon">
              <i class="fa-solid fa-keyboard"></i>
            </div>
            <div class="device-info">
              <strong>{{ device.model }}</strong>
              <small v-if="device.serial_number" class="text-muted d-block">S/N: {{ device.serial_number }}</small>
            </div>
            <div class="device-actions">
              <button class="btn btn-sm btn-outline-primary" @click="toggleRepairForm(device.id)">
                {{ activeDeviceId === device.id ? 'Cerrar OT' : 'Crear OT' }}
              </button>
            </div>
          </div>
          <div v-if="activeDeviceId" class="repair-intake-card mt-3">
            <h6 class="mb-2">Nueva orden de trabajo</h6>
            <div class="row g-2">
              <div class="col-md-8">
                <label class="form-label">Problema reportado *</label>
                <input v-model="newRepair.problem_reported" class="form-control" placeholder="Ej: Teclas 2 y 3 no suenan" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Prioridad</label>
                <select v-model="newRepair.priority" class="form-select">
                  <option :value="1">Alta</option>
                  <option :value="2">Normal</option>
                  <option :value="3">Baja</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Abono (CLP)</label>
                <input v-model.number="newRepair.paid_amount" type="number" min="0" class="form-control" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Medio de pago</label>
                <select v-model="newRepair.payment_method" class="form-select">
                  <option value="cash">Efectivo</option>
                  <option value="web">Web</option>
                  <option value="transfer">Transferencia</option>
                </select>
              </div>
              <div class="col-12">
                <div class="form-check">
                  <input id="groupOt" v-model="groupWithRepair" class="form-check-input" type="checkbox" />
                  <label class="form-check-label" for="groupOt">
                    Agrupar bajo OT existente (mismo cliente)
                  </label>
                </div>
              </div>
              <div v-if="groupWithRepair" class="col-12">
                <label class="form-label">OT base</label>
                <select v-model.number="selectedParentRepairId" class="form-select">
                  <option :value="null">Selecciona OT base</option>
                  <option v-for="r in clientRepairs" :key="r.id" :value="r.id">
                    {{ r.repair_number || ('OT #' + r.id) }} - {{ r.problem_reported }}
                  </option>
                </select>
              </div>
            </div>
            <div class="mt-3 d-flex gap-2 justify-content-end">
              <button class="btn btn-outline-secondary btn-sm" @click="resetRepairForm">Limpiar</button>
              <button class="btn btn-primary btn-sm" :disabled="!newRepair.problem_reported || savingRepair" @click="createRepair">
                {{ savingRepair ? 'Creando...' : 'Crear OT' }}
              </button>
            </div>
          </div>
        </div>
        <p v-else class="text-muted small">Sin dispositivos registrados</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import { api } from '@/services/api'

const props = defineProps({
  client: { type: Object, default: () => ({}) }
})

const devices = ref([])
const showAddDevice = ref(false)
const savingDevice = ref(false)
const savingRepair = ref(false)
const activeDeviceId = ref(null)
const clientRepairs = ref([])
const groupWithRepair = ref(false)
const selectedParentRepairId = ref(null)
const newDevice = ref({
  brand_other: '',
  model: '',
  serial_number: '',
  description: '',
  condition_notes: ''
})
const newRepair = ref({
  problem_reported: '',
  priority: 2,
  paid_amount: 20000,
  payment_method: 'cash'
})

const loadDevices = async () => {
  if (!props.client?.id) {
    devices.value = []
    return
  }
  try {
    const res = await api.get(`/clients/${props.client.id}/devices`)
    devices.value = res.data || res || []
  } catch (e) {
    devices.value = []
  }
}

const loadClientRepairs = async () => {
  if (!props.client?.id) {
    clientRepairs.value = []
    return
  }
  try {
    const res = await api.get(`/clients/${props.client.id}/repairs`)
    clientRepairs.value = res.data || res || []
  } catch (e) {
    clientRepairs.value = []
  }
}

const addDevice = async () => {
  if (!newDevice.value.model || !props.client?.id) return
  savingDevice.value = true
  try {
    await api.post('/devices/', {
      client_id: props.client.id,
      brand_other: newDevice.value.brand_other || null,
      model: newDevice.value.model,
      serial_number: newDevice.value.serial_number || null,
      description: newDevice.value.description || null,
      condition_notes: newDevice.value.condition_notes || null
    })
    await loadDevices()
    newDevice.value = { brand_other: '', model: '', serial_number: '', description: '', condition_notes: '' }
    showAddDevice.value = false
  } catch (e) {
    console.error('Error agregando dispositivo:', e)
    alert('Error al agregar dispositivo')
  } finally {
    savingDevice.value = false
  }
}

const toggleRepairForm = (deviceId) => {
  activeDeviceId.value = activeDeviceId.value === deviceId ? null : deviceId
}

const resetRepairForm = () => {
  newRepair.value = { problem_reported: '', priority: 2, paid_amount: 20000, payment_method: 'cash' }
  groupWithRepair.value = false
  selectedParentRepairId.value = null
}

const createRepair = async () => {
  if (!activeDeviceId.value || !newRepair.value.problem_reported) return
  savingRepair.value = true
  try {
    const payload = {
      device_id: activeDeviceId.value,
      problem_reported: newRepair.value.problem_reported,
      priority: newRepair.value.priority,
      paid_amount: newRepair.value.paid_amount,
      payment_method: newRepair.value.payment_method,
      payment_status: 'deposit'
    }
    if (groupWithRepair.value && selectedParentRepairId.value) {
      payload.ot_parent_id = selectedParentRepairId.value
    }
    await api.post('/repairs', payload)
    resetRepairForm()
    activeDeviceId.value = null
  } catch (e) {
    console.error('Error creando OT:', e)
    alert('Error al crear OT')
  } finally {
    savingRepair.value = false
  }
}

const formatNumber = (n) => {
  return new Intl.NumberFormat('es-CL').format(n)
}

// Watch for client changes
watch(() => props.client?.id, () => {
  loadDevices()
  loadClientRepairs()
}, { immediate: true })
</script>

<style scoped lang="scss">
.client-detail {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1rem;
  background: #fff;
}
.client-code {
  font-size: 0.95rem;
  font-weight: 700;
  color: #ec6b00;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4b5563;
  margin-bottom: 0.25rem;

  i {
    width: 18px;
    color: #9ca3af;
  }
}

.stats-row {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.stat-badge {
  background: #f3f4f6;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  color: #374151;

  i {
    color: #ec6b00;
    margin-right: 0.35rem;
  }
}

.devices-section {
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
}

.devices-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.device-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fafafa;
}

.device-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ec6b00;
  color: white;
  border-radius: 8px;
}

.device-info {
  flex: 1;

  strong {
    color: #1f2937;
    font-size: 0.95rem;
  }
}
.device-actions {
  display: flex;
  gap: 0.5rem;
}

.add-device-form {
  background: #f9fafb;
}
.repair-intake-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 1rem;
  background: #fffaf3;
}
</style>
