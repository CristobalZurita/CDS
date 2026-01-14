<template>
  <div class="repairs-page">
    <div class="repairs-container">
      <!-- Header -->
      <div class="repairs-header">
        <div>
          <h1>Mis Reparaciones</h1>
          <p class="subtitle">Historial completo de tus reparaciones</p>
        </div>
        <div class="header-actions">
          <router-link to="/cotizador-ia" class="btn-primary">
            + Nueva Cotización
          </router-link>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters">
        <div class="filter-group">
          <label>Filtrar por estado:</label>
          <select v-model="selectedStatus" class="filter-select">
            <option value="">Todos</option>
            <option value="completed">Completadas</option>
            <option value="in-progress">En Proceso</option>
            <option value="waiting">En Espera</option>
            <option value="cancelled">Canceladas</option>
          </select>
        </div>
      </div>

      <!-- Repairs List -->
      <div v-if="filteredRepairs.length > 0" class="repairs-list">
        <div
          v-for="repair in filteredRepairs"
          :key="repair.id"
          class="repair-card"
        >
          <div class="repair-card-header">
            <div class="repair-info">
              <h3>{{ repair.instrument }}</h3>
              <p class="repair-ticket">Ticket: {{ repair.id }}</p>
            </div>
            <div class="repair-status" :class="repair.status">
              {{ getStatusLabel(repair.status) }}
            </div>
          </div>

          <div class="repair-details">
            <div class="detail-row">
              <span class="detail-label">Falla reportada:</span>
              <span class="detail-value">{{ repair.fault }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Ingresado:</span>
              <span class="detail-value">{{ formatDate(repair.date_in) }}</span>
            </div>
            <div v-if="repair.date_out" class="detail-row">
              <span class="detail-label">Completado:</span>
              <span class="detail-value">{{ formatDate(repair.date_out) }}</span>
            </div>
            <div v-if="repair.cost" class="detail-row">
              <span class="detail-label">Costo:</span>
              <span class="detail-value">${{ formatPrice(repair.cost) }}</span>
            </div>
          </div>

          <div v-if="repair.status === 'in-progress'" class="repair-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: repair.progress + '%' }"></div>
            </div>
            <span class="progress-text">{{ repair.progress }}% completado</span>
          </div>

          <div class="repair-actions">
            <button @click="viewRepair(repair)" class="btn-view">
              Ver detalles →
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">📋</div>
        <p>No hay reparaciones que coincidan con los filtros</p>
        <router-link to="/cotizador-ia" class="btn-primary">
          Solicitar cotización ahora
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const selectedStatus = ref('')

// Mock data
const repairs = ref([
  {
    id: 'REP-2024-001',
    instrument: 'Moog Minimoog Model D',
    fault: 'No genera sonido',
    status: 'completed',
    date_in: new Date('2024-11-15'),
    date_out: new Date('2024-11-28'),
    cost: 450000,
    progress: 100
  },
  {
    id: 'REP-2024-002',
    instrument: 'Roland TR-808',
    fault: 'Batería defectuosa',
    status: 'completed',
    date_in: new Date('2024-12-01'),
    date_out: new Date('2024-12-08'),
    cost: 280000,
    progress: 100
  },
  {
    id: 'REP-2024-003',
    instrument: 'Korg MS-20',
    fault: 'Teclado con teclas pegadas',
    status: 'completed',
    date_in: new Date('2024-12-10'),
    date_out: new Date('2024-12-22'),
    cost: 350000,
    progress: 100
  },
  {
    id: 'REP-2025-001',
    instrument: 'Moog Minimoog Model D',
    fault: 'Filtro no responde',
    status: 'in-progress',
    date_in: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    progress: 65
  },
  {
    id: 'REP-2025-002',
    instrument: 'Roland TR-909',
    fault: 'No enciende',
    status: 'waiting',
    date_in: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    progress: 10
  }
])

const filteredRepairs = computed(() => {
  if (!selectedStatus.value) return repairs.value
  return repairs.value.filter(r => r.status === selectedStatus.value)
})

const getStatusLabel = (status) => {
  const labels = {
    'completed': '✓ Completada',
    'in-progress': '🔧 En Proceso',
    'waiting': '⌛ En Espera',
    'cancelled': '✕ Cancelada'
  }
  return labels[status] || status
}

const formatDate = (date) => {
  return new Intl.DateTimeFormat('es-CL', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date)
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('es-CL', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(price)
}

const viewRepair = (repair) => {
  router.push(`/repairs/${repair.id}`)
}
</script>

<style scoped>
.repairs-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem 1rem;
}

.repairs-container {
  max-width: 1000px;
  margin: 0 auto;
}

/* Header */
.repairs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.repairs-header h1 {
  margin: 0 0 0.5rem 0;
  color: #2d3748;
  font-size: 2rem;
}

.subtitle {
  margin: 0;
  color: #718096;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.btn-primary {
  padding: 0.875rem 1.75rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

/* Filters */
.filters {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  gap: 2rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 600;
  color: #4a5568;
  font-size: 0.9rem;
}

.filter-select {
  padding: 0.75rem;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  background: white;
  color: #4a5568;
  font-weight: 500;
  cursor: pointer;
  min-width: 200px;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Repairs List */
.repairs-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.repair-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #667eea;
  transition: all 0.2s;
}

.repair-card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
  transform: translateX(4px);
}

.repair-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.repair-info h3 {
  margin: 0 0 0.25rem 0;
  color: #2d3748;
  font-size: 1.1rem;
}

.repair-ticket {
  margin: 0;
  color: #a0aec0;
  font-size: 0.85rem;
}

.repair-status {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
}

.repair-status.completed {
  background: #c6f6d5;
  color: #22543d;
}

.repair-status.in-progress {
  background: #bee3f8;
  color: #2c5282;
}

.repair-status.waiting {
  background: #fed7d7;
  color: #742a2a;
}

.repair-status.cancelled {
  background: #fed7d7;
  color: #742a2a;
}

/* Repair Details */
.repair-details {
  margin-bottom: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.detail-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.85rem;
  color: #718096;
  font-weight: 600;
  text-transform: uppercase;
}

.detail-value {
  color: #2d3748;
  font-size: 0.95rem;
}

/* Progress */
.repair-progress {
  margin-bottom: 1rem;
}

.progress-bar {
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.85rem;
  color: #718096;
}

/* Actions */
.repair-actions {
  text-align: right;
}

.btn-view {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  text-decoration: none;
  font-weight: 600;
  padding: 0;
  transition: all 0.2s;
}

.btn-view:hover {
  color: #764ba2;
}

/* Empty State */
.empty-state {
  background: white;
  border-radius: 12px;
  padding: 4rem 2rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-state p {
  margin: 0 0 1.5rem 0;
  color: #718096;
  font-size: 1.1rem;
}

/* Responsive */
@media (max-width: 768px) {
  .repairs-page {
    padding: 1rem;
  }

  .repairs-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1.5rem;
  }

  .filters {
    flex-direction: column;
  }

  .repair-details {
    grid-template-columns: 1fr;
  }

  .repair-card-header {
    flex-direction: column;
    gap: 0.5rem;
  }

  .repair-status {
    align-self: flex-start;
  }
}
</style>
