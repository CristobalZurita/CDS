<template>
  <section class="admin-section">
    <div class="section-header">
      <h2 class="section-title">🔧 Últimas Reparaciones</h2>
      <div class="section-actions">
        <input
          v-model="searchQuery"
          type="search"
          class="search-input"
          placeholder="Buscar OT, cliente o instrumento..."
        />
        <button class="btn-refresh" @click="fetchRepairs">Actualizar</button>
      </div>
    </div>
    <div class="table-wrap">
      <table class="admin-table">
        <thead>
          <tr>
            <th>OT</th>
            <th>Cliente</th>
            <th>Instrumento</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="repair in filteredRepairs" :key="repair.id" data-testid="repair-row">
            <td data-label="OT">{{ repair.repair_code || repair.repair_number || repair.id }}</td>
            <td data-label="Cliente">
              <div class="cell-stack">
                <strong>{{ repair.client_name || 'Sin cliente' }}</strong>
                <small v-if="repair.client_code">{{ repair.client_code }}</small>
              </div>
            </td>
            <td data-label="Instrumento">{{ repair.device_model || 'Sin modelo' }}</td>
            <td data-label="Estado">
              <span :class="['status-badge', `status-${repair.status}`]">
                {{ formatStatus(repair.status) }}
              </span>
            </td>
            <td data-label="Acciones">
              <button class="btn-action" @click="editRepair(repair)">Editar</button>
              <button class="btn-action danger" @click="deleteRepair(repair.id)">Borrar</button>
            </td>
          </tr>
          <tr v-if="filteredRepairs.length === 0">
            <td colspan="5" class="empty-row">No se encontraron reparaciones</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
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
  if (!q) return repairs.value.slice(0, 10) // Show last 10
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
  const statusMap = {
    'pending': 'Pendiente',
    'in_progress': 'En progreso',
    'completed': 'Completada',
    'delivered': 'Entregada',
    'cancelled': 'Cancelada'
  }
  return statusMap[status] || status
}

const editRepair = (repair) => {
  router.push(`/admin/repairs/${repair.id}`)
}

onMounted(() => {
  fetchRepairs()
})
</script>

<style scoped>
.admin-section {
  background: var(--color-white, #fff);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.section-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-dark, #1a1a2e);
}

.section-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.search-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-light, #e0e0e0);
  border-radius: 6px;
  min-width: 250px;
}

.btn-refresh {
  padding: 0.5rem 1rem;
  background: var(--color-primary, #ff6b35);
  color: var(--color-white, #fff);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-refresh:hover {
  opacity: 0.9;
}

.table-wrap {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
}

.admin-table th,
.admin-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--color-light, #e0e0e0);
}

.admin-table th {
  font-weight: 600;
  background: var(--color-bg, #f5f5f5);
  color: var(--color-dark, #1a1a2e);
}

.admin-table tr:hover td {
  background: var(--color-bg, #f5f5f5);
}

.cell-stack {
  display: flex;
  flex-direction: column;
}

.cell-stack small {
  color: var(--color-gray-600, #666);
  font-size: 0.8rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-pending {
  background: rgba(255, 193, 7, 0.2);
  color: #856404;
}

.status-in_progress {
  background: rgba(23, 162, 184, 0.2);
  color: #0c5460;
}

.status-completed {
  background: rgba(40, 167, 69, 0.2);
  color: #155724;
}

.status-delivered {
  background: rgba(108, 117, 125, 0.2);
  color: #383d41;
}

.status-cancelled {
  background: rgba(220, 53, 69, 0.2);
  color: #721c24;
}

.btn-action {
  padding: 0.35rem 0.75rem;
  margin-right: 0.25rem;
  background: transparent;
  border: 1px solid var(--color-primary, #ff6b35);
  color: var(--color-primary, #ff6b35);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.btn-action:hover {
  background: var(--color-primary, #ff6b35);
  color: var(--color-white, #fff);
}

.btn-action.danger {
  border-color: var(--color-danger, #dc3545);
  color: var(--color-danger, #dc3545);
}

.btn-action.danger:hover {
  background: var(--color-danger, #dc3545);
  color: var(--color-white, #fff);
}

.empty-row {
  text-align: center;
  color: var(--color-gray-600, #666);
  padding: 2rem;
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .section-actions {
    flex-direction: column;
  }
  
  .search-input {
    min-width: 100%;
  }
  
  .admin-table th,
  .admin-table td {
    padding: 0.5rem;
    font-size: 0.875rem;
  }
}
</style>
