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
            <option value="in_progress">En Proceso</option>
            <option value="waiting_parts">En Espera</option>
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
              <div class="progress-fill" :class="getProgressClass(repair.progress)"></div>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'
import { showError } from '@/services/toastService'

const router = useRouter()
const selectedStatus = ref('')
const repairs = ref([])
const isLoading = ref(false)

const filteredRepairs = computed(() => {
  if (!selectedStatus.value) return repairs.value
  return repairs.value.filter(r => r.status === selectedStatus.value)
})

const getStatusLabel = (status) => {
  const labels = {
    pending_quote: '⏳ Pendiente',
    quoted: '💬 Cotizado',
    approved: '✅ Aprobado',
    in_progress: '🔧 En Proceso',
    waiting_parts: '⌛ En Espera',
    testing: '🧪 En Pruebas',
    completed: '✓ Completada',
    delivered: '📦 Entregado',
    cancelled: '✕ Cancelada'
  }
  return labels[status] || status
}

const formatDate = (date) => {
  if (!date) return '—'
  return new Intl.DateTimeFormat('es-CL', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(new Date(date))
}

const formatPrice = (price) => {
  if (!price && price !== 0) return '—'
  return new Intl.NumberFormat('es-CL', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(price)
}

const viewRepair = (repair) => {
  router.push(`/repairs/${repair.id}`)
}

const getProgressClass = (progress) => {
  const normalized = Math.max(0, Math.min(100, Math.round(Number(progress) || 0)))
  return `progress-${normalized}`
}

const fetchRepairs = async () => {
  isLoading.value = true
  try {
    const { data } = await api.get('/client/repairs')
    repairs.value = data || []
  } catch (err) {
    showError(err.response?.data?.detail || 'Error cargando reparaciones')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchRepairs()
})
</script>

<style lang="scss" scoped>
@import '@/scss/_core.scss';

.repairs-page {
  min-height: 100vh;
  background: linear-gradient(135deg, $light-1 0%, $light-4 100%);
  padding: $spacer-xl $spacer-md;
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
  margin-bottom: $spacer-xl;
  background: $color-white;
  padding: $spacer-xl;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-md;
}

.repairs-header h1 {
  margin: 0 0 $spacer-sm 0;
  color: $color-dark;
  font-size: $h2-size;
}

.subtitle {
  margin: 0;
  color: $light-6;
}

.header-actions {
  display: flex;
  gap: $spacer-md;
}

.btn-primary {
  padding: $text-sm $spacer-lg;
  background: linear-gradient(135deg, $color-primary, $color-primary-dark);
  color: $color-white;
  border: none;
  border-radius: $border-radius-md;
  font-weight: $fw-semibold;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: $spacer-sm;
  transition: $transition-fast;
  box-shadow: $shadow-md;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: $shadow-lg;
}

/* Filters */
.filters {
  background: $color-white;
  padding: $spacer-lg;
  border-radius: $border-radius-lg;
  margin-bottom: $spacer-xl;
  box-shadow: $shadow-md;
  display: flex;
  gap: $spacer-xl;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: $spacer-sm;
}

.filter-group label {
  font-weight: $fw-semibold;
  color: $light-7;
  font-size: $text-sm;
}

.filter-select {
  padding: $spacer-sm + $spacer-xs;
  border: 1px solid $light-4;
  border-radius: 6px;
  background: $color-white;
  color: $light-7;
  font-weight: $fw-medium;
  cursor: pointer;
  min-width: 200px;
}

.filter-select:focus {
  outline: none;
  border-color: $color-primary;
  box-shadow: 0 0 0 3px rgba($color-primary, 0.1);
}

/* Repairs List */
.repairs-list {
  display: flex;
  flex-direction: column;
  gap: $spacer-lg;
}

.repair-card {
  background: $color-white;
  border-radius: $border-radius-lg;
  padding: $spacer-lg;
  box-shadow: $shadow-md;
  border-left: 4px solid $color-primary;
  transition: $transition-fast;
}

.repair-card:hover {
  box-shadow: $shadow-lg;
  transform: translateX(4px);
}

.repair-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacer-lg;
  padding-bottom: $spacer-md;
  border-bottom: 1px solid $light-3;
}

.repair-info h3 {
  margin: 0 0 $spacer-xs 0;
  color: $color-dark;
  font-size: $text-lg;
}

.repair-ticket {
  margin: 0;
  color: $light-5;
  font-size: $text-sm;
}

.repair-status {
  padding: $spacer-sm $spacer-md;
  border-radius: $border-radius-pill;
  font-size: $text-sm;
  font-weight: $fw-semibold;
  white-space: nowrap;
}

.repair-status.completed {
  background: $color-green-200-legacy;
  color: $color-green-darker-legacy;
}

.repair-status.in-progress,
.repair-status.in_progress {
  background: $color-blue-150-legacy;
  color: $color-blue-800-legacy;
}

.repair-status.pending_quote,
.repair-status.quoted,
.repair-status.approved,
.repair-status.testing {
  background: $color-orange-100-legacy;
  color: $color-amber-800-legacy;
}

.repair-status.waiting,
.repair-status.waiting_parts {
  background: $color-red-200-legacy;
  color: $color-red-900-legacy;
}

.repair-status.cancelled {
  background: $color-red-200-legacy;
  color: $color-red-900-legacy;
}

/* Repair Details */
.repair-details {
  margin-bottom: $spacer-md;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: $spacer-md;
}

.detail-row {
  display: flex;
  flex-direction: column;
  gap: $spacer-xs;
}

.detail-label {
  font-size: $text-sm;
  color: $light-6;
  font-weight: $fw-semibold;
  text-transform: uppercase;
}

.detail-value {
  color: $color-dark;
  font-size: $text-base;
}

/* Progress */
.repair-progress {
  margin-bottom: $spacer-md;
}

.progress-bar {
  height: 8px;
  background: $light-3;
  border-radius: $border-radius-sm;
  overflow: hidden;
  margin-bottom: $spacer-sm;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, $color-primary, $color-primary-dark);
  transition: $transition-base;

  @for $i from 0 through 100 {
    &.progress-#{$i} {
      width: #{$i}%;
    }
  }
}

.progress-text {
  font-size: $text-sm;
  color: $light-6;
}

/* Actions */
.repair-actions {
  text-align: right;
}

.btn-view {
  background: none;
  border: none;
  color: $color-primary;
  cursor: pointer;
  text-decoration: none;
  font-weight: $fw-semibold;
  padding: 0;
  transition: $transition-fast;
}

.btn-view:hover {
  color: $color-primary-dark;
}

/* Empty State */
.empty-state {
  background: $color-white;
  border-radius: $border-radius-lg;
  padding: ($spacer-xl * 2) $spacer-xl;
  text-align: center;
  box-shadow: $shadow-md;
}

.empty-icon {
  font-size: $h1-size;
  margin-bottom: $spacer-md;
}

.empty-state p {
  margin: 0 0 $spacer-lg 0;
  color: $light-6;
  font-size: $text-lg;
}

/* Responsive */
@include media-breakpoint-down(md) {
  .repairs-page {
    padding: $spacer-md;
  }

  .repairs-header {
    flex-direction: column;
    align-items: flex-start;
    gap: $spacer-lg;
  }

  .filters {
    flex-direction: column;
  }

  .repair-details {
    grid-template-columns: 1fr;
  }

  .repair-card-header {
    flex-direction: column;
    gap: $spacer-sm;
  }

  .repair-status {
    align-self: flex-start;
  }
}
</style>
