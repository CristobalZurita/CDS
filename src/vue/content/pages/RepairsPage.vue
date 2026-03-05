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
          <select v-model="selectedStatus" class="filter-select" data-testid="repairs-status-filter">
            <option value="">Todos</option>
            <option value="pending_quote">Ingreso / Diagnóstico</option>
            <option value="in_progress">En Proceso</option>
            <option value="completed">Completadas / Entregadas</option>
            <option value="cancelled">Rechazadas</option>
          </select>
        </div>
      </div>

      <!-- Repairs List -->
      <div v-if="filteredRepairs.length > 0" class="repairs-list">
        <div
          v-for="repair in filteredRepairs"
          :key="repair.id"
          class="repair-card"
          data-testid="repairs-card"
        >
          <div class="repair-card-header">
            <div class="repair-info">
              <h3>{{ repair.instrument }}</h3>
              <p class="repair-ticket">OT: {{ repair.repair_code || repair.repair_number || repair.id }}</p>
            </div>
            <div class="repair-status" :class="repair.status_normalized">
              {{ getStatusLabel(repair.status_normalized || repair.status) }}
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

          <div v-if="shouldShowProgress(repair)" class="repair-progress">
            <div class="progress-bar">
              <div class="progress-fill" :class="getProgressClass(repair.progress)"></div>
            </div>
            <span class="progress-text">{{ repair.progress }}% completado</span>
          </div>

          <div class="repair-actions">
            <button @click="viewRepair(repair)" class="btn-view" data-testid="repair-view">
              Ver detalles →
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state" data-testid="repairs-empty">
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
import { useRepairs } from '@/composables/useRepairs'
import { showError } from '@/services/toastService'
import {
  getRepairProgressByStatus,
  getRepairStatusBucket,
  getRepairStatusLabel,
  isActiveRepairStatus,
  normalizeRepairStatus
} from '@/utils/repairStatus'

const router = useRouter()
const selectedStatus = ref('')
const { repairs, fetchClientRepairs } = useRepairs()

const decoratedRepairs = computed(() => {
  return (repairs.value || []).map((repair) => {
    const normalizedStatus = normalizeRepairStatus(repair.status_normalized || repair.status)
    const fallbackProgress = getRepairProgressByStatus(normalizedStatus)
    return {
      ...repair,
      status_normalized: normalizedStatus,
      status_bucket: getRepairStatusBucket(normalizedStatus),
      progress: Number.isFinite(Number(repair.progress))
        ? Number(repair.progress)
        : fallbackProgress
    }
  })
})

const filteredRepairs = computed(() => {
  if (!selectedStatus.value) return decoratedRepairs.value
  return decoratedRepairs.value.filter(r => r.status_bucket === selectedStatus.value)
})

const getStatusLabel = (status) => {
  return getRepairStatusLabel(status)
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

const shouldShowProgress = (repair) => {
  return isActiveRepairStatus(repair?.status_normalized || repair?.status)
}

const getProgressClass = (progress) => {
  const normalized = Math.max(0, Math.min(100, Math.round(Number(progress) || 0)))
  return `progress-${normalized}`
}

const fetchRepairs = async () => {
  try {
    await fetchClientRepairs()
  } catch (err) {
    showError(err.response?.data?.detail || 'Error cargando reparaciones')
  }
}

onMounted(() => {
  fetchRepairs()
})
</script>
