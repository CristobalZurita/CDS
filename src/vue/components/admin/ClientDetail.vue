<template>
  <section class="client-detail">
    <div v-if="!client.id" class="text-muted text-center py-4">
      <i class="fa-solid fa-user-large fa-2x mb-2"></i>
      <p>Selecciona un cliente</p>
    </div>

    <div v-else>
      <!-- Client Info -->
      <div class="client-info mb-4">
        <h4 class="mb-2">{{ client.name || 'Cliente' }}</h4>
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
            <label class="form-label">Modelo/Nombre</label>
            <input v-model="newDevice.model" type="text" class="form-control" placeholder="Ej: Korg MS-20" />
          </div>
          <div class="mb-2">
            <label class="form-label">Numero de serie (opcional)</label>
            <input v-model="newDevice.serial_number" type="text" class="form-control" placeholder="Ej: SN123456" />
          </div>
          <div class="mb-2">
            <label class="form-label">Descripcion (opcional)</label>
            <textarea v-model="newDevice.description" class="form-control" rows="2" placeholder="Notas adicionales..."></textarea>
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
const newDevice = ref({
  model: '',
  serial_number: '',
  description: ''
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

const addDevice = async () => {
  if (!newDevice.value.model || !props.client?.id) return
  savingDevice.value = true
  try {
    await api.post('/devices/', {
      client_id: props.client.id,
      model: newDevice.value.model,
      serial_number: newDevice.value.serial_number || null,
      description: newDevice.value.description || null
    })
    await loadDevices()
    newDevice.value = { model: '', serial_number: '', description: '' }
    showAddDevice.value = false
  } catch (e) {
    console.error('Error agregando dispositivo:', e)
    alert('Error al agregar dispositivo')
  } finally {
    savingDevice.value = false
  }
}

const formatNumber = (n) => {
  return new Intl.NumberFormat('es-CL').format(n)
}

// Watch for client changes
watch(() => props.client?.id, () => {
  loadDevices()
}, { immediate: true })
</script>

<style scoped lang="scss">
.client-detail {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1rem;
  background: #fff;
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

.add-device-form {
  background: #f9fafb;
}
</style>
