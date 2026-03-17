<template>
  <div class="repairs-list">
    <div class="list-toolbar">
      <input
        v-model="searchQuery"
        type="search"
        class="search-input"
        placeholder="Buscar OT, cliente o instrumento..."
      />
      <button class="btn-refresh" @click="fetchRepairs">↻ Actualizar</button>
    </div>

    <p v-if="error" class="list-error">{{ error }}</p>
    
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>OT</th>
            <th>Cliente</th>
            <th>Instrumento</th>
            <th>Estado</th>
            <th class="actions">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="repair in filteredRepairs" :key="repair.id">
            <td class="mono">{{ repair.repair_code || repair.repair_number || repair.id }}</td>
            <td>
              <div class="client-cell">
                <span class="client-name">{{ repair.client_name || 'Sin cliente' }}</span>
                <span v-if="repair.client_code" class="client-code">{{ repair.client_code }}</span>
              </div>
            </td>
            <td>{{ repair.device_model || 'Sin modelo' }}</td>
            <td>
              <span :class="['status-pill', repair.status]">
                {{ formatStatus(repair.status) }}
              </span>
            </td>
            <td class="actions">
              <button class="btn-icon" @click="editRepair(repair)" title="Editar">✏️</button>
              <button class="btn-icon danger" @click="removeRepair(repair.id)" title="Eliminar">🗑️</button>
            </td>
          </tr>
          <tr v-if="filteredRepairs.length === 0">
            <td colspan="5" class="empty-cell">No se encontraron reparaciones</td>
          </tr>
        </tbody>
      </table>
    </div>

    <BaseConfirmDialog
      :open="repairPendingDelete !== null"
      title="Eliminar reparación"
      message="¿Eliminar esta reparación?"
      confirm-label="Eliminar"
      :confirm-loading="isDeleting"
      @cancel="cancelDelete"
      @confirm="confirmDelete"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { BaseConfirmDialog } from '@/components/base'
import { useRepairs } from '@/composables/useRepairs'

const { repairs, fetchRepairs, deleteRepair, error } = useRepairs()
const router = useRouter()
const searchQuery = ref('')
const repairPendingDelete = ref(null)
const isDeleting = ref(false)

const filteredRepairs = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return repairs.value.slice(0, 10)
  return (repairs.value || []).filter((repair) => {
    const haystack = [
      repair.repair_code,
      repair.repair_number,
      repair.client_name,
      repair.client_code,
      repair.device_model
    ].filter(Boolean).join(' ').toLowerCase()
    return haystack.includes(q)
  }).slice(0, 10)
})

const formatStatus = (status) => {
  const map = {
    'pending': 'Pendiente',
    'in_progress': 'En progreso',
    'completed': 'Completada',
    'delivered': 'Entregada',
    'cancelled': 'Cancelada'
  }
  return map[status] || status
}

const editRepair = (repair) => {
  router.push(`/admin/repairs/${repair.id}`)
}

const removeRepair = (id) => {
  repairPendingDelete.value = id
}

const cancelDelete = () => {
  if (isDeleting.value) return
  repairPendingDelete.value = null
}

const confirmDelete = async () => {
  if (repairPendingDelete.value === null || isDeleting.value) return
  isDeleting.value = true
  try {
    await deleteRepair(repairPendingDelete.value)
    repairPendingDelete.value = null
  } catch {
    // El mensaje queda expuesto en error
  } finally {
    isDeleting.value = false
  }
}

onMounted(fetchRepairs)
</script>

<style scoped src="./commonAdminTable.css"></style>

<style scoped>
.repairs-list {
  width: 100%;
}

.list-toolbar {
  display: flex;
  gap: var(--admin-space-sm, 0.96rem);
  margin-bottom: var(--admin-space-md, 1.2rem);
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 26rem;
  min-height: var(--admin-control-min-height, 52px);
  padding: var(--admin-space-sm, 0.96rem) var(--admin-space-md, 1.2rem);
  border: 1px solid var(--cds-border-input);
  border-radius: var(--cds-radius-md);
  font-size: var(--cds-text-base);
  color: var(--cds-text-normal);
  background: var(--cds-white);
}

.search-input:focus {
  outline: none;
  border-color: var(--cds-primary);
  box-shadow: var(--cds-focus-ring);
}

.mono {
  font-family: ui-monospace, monospace;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.client-cell {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.client-name {
  font-weight: 500;
  color: var(--cds-dark);
}

.client-code {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.status-pill {
  display: inline-block;
  padding: var(--cds-space-xs) var(--cds-space-md);
  border-radius: var(--cds-radius-pill);
  font-size: var(--cds-text-sm);
  font-weight: 600;
  text-transform: uppercase;
}

.status-pill.pending {
  background: var(--cds-warning-bg);
  color: var(--cds-warning-text);
}

.status-pill.in_progress {
  background: color-mix(in srgb, var(--cds-info) 18%, white);
  color: color-mix(in srgb, var(--cds-info) 85%, black);
}

.status-pill.completed {
  background: var(--cds-valid-bg);
  color: var(--cds-valid-text);
}

.status-pill.delivered {
  background: var(--cds-light-2);
  color: var(--cds-light-7);
}

.status-pill.cancelled {
  background: var(--cds-invalid-bg);
  color: var(--cds-invalid-text);
}

</style>
