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
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useRepairs } from '@/composables/useRepairs'

const { repairs, fetchRepairs, deleteRepair } = useRepairs()
const router = useRouter()
const searchQuery = ref('')

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

const removeRepair = async (id) => {
  if (!confirm('¿Eliminar esta reparación?')) return
  await deleteRepair(id)
}

onMounted(fetchRepairs)
</script>

<style scoped>
/* 35% larger */
.repairs-list {
  width: 100%;
}

.list-toolbar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.35rem;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 340px;
  padding: 0.85rem 1.2rem;
  border: 1px solid #e8ecf1;
  border-radius: 11px;
  font-size: 1.35rem;
}

.search-input:focus {
  outline: none;
  border-color: #ff6b35;
}

.btn-refresh {
  padding: 0.85rem 1.35rem;
  background: #f8fafc;
  border: 1px solid #e8ecf1;
  border-radius: 11px;
  cursor: pointer;
  font-size: 1.35rem;
  color: #374151;
}

.btn-refresh:hover {
  background: #e8ecf1;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 1.4rem;
}

.data-table th {
  text-align: left;
  padding: 1rem;
  font-weight: 600;
  color: #6b7280;
  border-bottom: 1px solid #e8ecf1;
  font-size: 1.15rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.data-table td {
  padding: 1.2rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  color: #374151;
}

.data-table tr:hover td {
  background: #f8fafc;
}

.mono {
  font-family: ui-monospace, monospace;
  font-size: 1.25rem;
  color: #6b7280;
}

.client-cell {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.client-name {
  font-weight: 500;
  color: #1a1f36;
}

.client-code {
  font-size: 1.15rem;
  color: #6b7280;
}

.status-pill {
  display: inline-block;
  padding: 0.4rem 1rem;
  border-radius: 999px;
  font-size: 1.1rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-pill.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-pill.in_progress {
  background: #dbeafe;
  color: #1e40af;
}

.status-pill.completed {
  background: #d1fae5;
  color: #065f46;
}

.status-pill.delivered {
  background: #f3f4f6;
  color: #374151;
}

.status-pill.cancelled {
  background: #fee2e2;
  color: #991b1b;
}

.actions {
  text-align: right;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  font-size: 1.35rem;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.btn-icon:hover {
  opacity: 1;
}

.btn-icon.danger:hover {
  color: #dc2626;
}

.empty-cell {
  text-align: center;
  color: #6b7280;
  padding: 2.7rem;
}
</style>
