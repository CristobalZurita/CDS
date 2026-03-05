<template>
  <div class="dashboard-page">
    <div class="dashboard-container">
      <!-- Header -->
      <div class="dashboard-header">
        <div>
          <h1>Mi Panel de Control</h1>
          <p class="welcome-text">Bienvenido {{ userFirstName || 'cliente' }}</p>
        </div>
        <div class="header-actions">
          <router-link to="/cotizador-ia" class="btn-primary">
            + Nueva Cotización
          </router-link>
          <button class="btn-logout" type="button" data-testid="dashboard-logout" @click="handleLogout">
            Cerrar sesión
          </button>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon pending">📋</div>
          <div class="stat-content">
            <div class="stat-value">{{ pendingRepairs }}</div>
            <div class="stat-label">Reparaciones Pendientes</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon active">🔧</div>
          <div class="stat-content">
            <div class="stat-value">{{ activeRepairs }}</div>
            <div class="stat-label">En Proceso</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon completed">✓</div>
          <div class="stat-content">
            <div class="stat-value">{{ completedRepairs }}</div>
            <div class="stat-label">Completadas</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon total">💰</div>
          <div class="stat-content">
            <div class="stat-value">${{ totalSpent }}</div>
            <div class="stat-label">Total Invertido</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon pending">💳</div>
          <div class="stat-content">
            <div class="stat-value">{{ pendingOtPayments }}</div>
            <div class="stat-label">Pagos OT Pendientes</div>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="dashboard-content">
        <!-- Left Column: Active Repairs -->
        <div class="column">
          <h2>Reparaciones Activas</h2>

          <div v-if="activeRepairsList.length > 0" class="repairs-list">
            <div
              v-for="repair in activeRepairsList"
              :key="repair.id"
              class="repair-card"
              data-testid="dashboard-repair-card"
            >
              <div class="repair-header">
                <div class="repair-info">
                  <h3>{{ repair.instrument }}</h3>
                  <p class="repair-id">OT: {{ repair.repair_code || repair.repair_number || repair.id }}</p>
                </div>
                <div class="repair-status" :class="getStatusClass(repair.status_normalized || repair.status)">
                  {{ getStatusLabel(repair.status_normalized || repair.status) }}
                </div>
              </div>

              <div class="repair-details">
                <p><strong>Falla:</strong> {{ repair.fault }}</p>
                <p><strong>Ingresado:</strong> {{ formatDate(repair.date_in) }}</p>
                <p v-if="repair.estimated_completion">
                  <strong>Estimado:</strong> {{ formatDate(repair.estimated_completion) }}
                </p>
              </div>

              <div class="repair-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :class="getProgressClass(repair.progress)"></div>
                </div>
                <span class="progress-text">{{ repair.progress }}% completado</span>
              </div>

              <div class="repair-actions">
                <button @click="viewRepair(repair)" class="btn-link" data-testid="dashboard-repair-view">Ver detalles →</button>
              </div>
            </div>
          </div>

          <div v-else class="empty-state" data-testid="dashboard-empty-repairs">
            <p>No tienes reparaciones activas</p>
            <router-link to="/cotizador-ia" class="btn-secondary">
              Solicitar cotización
            </router-link>
          </div>
        </div>

        <!-- Right Column: Quick Actions & Notifications -->
        <div class="column">
          <h2>Acciones Rápidas</h2>

          <div class="quick-actions">
            <router-link to="/cotizador-ia" class="action-card">
              <div class="action-icon">🎛️</div>
              <div class="action-text">
                <h4>Nueva Cotización</h4>
                <p>Solicita presupuesto para tu instrumento</p>
              </div>
            </router-link>

            <router-link to="/agendar" class="action-card">
              <div class="action-icon">📅</div>
              <div class="action-text">
                <h4>Agendar Cita</h4>
                <p>Reserva un horario para tu reparación</p>
              </div>
            </router-link>

            <router-link to="/ot-payments" class="action-card">
              <div class="action-icon">💳</div>
              <div class="action-text">
                <h4>Pagos OT</h4>
                <p>Sube comprobantes y revisa cobros de repuestos</p>
              </div>
            </router-link>

            <router-link to="/repairs" class="action-card">
              <div class="action-icon">📋</div>
              <div class="action-text">
                <h4>Ver Historial</h4>
                <p>Todas tus reparaciones completadas</p>
              </div>
            </router-link>

            <router-link to="/profile" class="action-card">
              <div class="action-icon">👤</div>
              <div class="action-text">
                <h4>Mi Perfil</h4>
                <p>Actualiza tus datos y preferencias</p>
              </div>
            </router-link>
          </div>

          <!-- Notifications -->
          <h2 class="notifications-title">Notificaciones</h2>

          <div v-if="notifications.length > 0" class="notifications-list">
            <div
              v-for="notification in notifications"
              :key="notification.id"
              class="notification-card"
              :class="notification.type"
              data-testid="dashboard-notification"
            >
              <div class="notification-icon">{{ getNotificationIcon(notification.type) }}</div>
              <div class="notification-content">
                <p class="notification-message">{{ notification.message }}</p>
                <p class="notification-time">{{ formatTime(notification.date) }}</p>
              </div>
              <button
                @click="dismissNotification(notification.id)"
                class="notification-close"
                data-testid="dashboard-notification-dismiss"
              >
                ✕
              </button>
            </div>
          </div>

          <div v-else class="empty-state" data-testid="dashboard-empty-notifications">
            <p>No hay notificaciones nuevas</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'
import { showError } from '@/services/toastService'
import { getRepairStatusLabel, normalizeRepairStatus } from '@/utils/repairStatus'

const router = useRouter()
const authStore = useAuthStore()

const activeRepairsList = ref([])
const notifications = ref([])
const stats = ref({
  pending_repairs: 0,
  active_repairs: 0,
  completed_repairs: 0,
  total_spent: 0
})
const isLoading = ref(false)

// Computed
const userFirstName = computed(() => authStore.user?.full_name?.split(' ')[0] || 'Cliente')
const pendingRepairs = computed(() => stats.value.pending_repairs)
const activeRepairs = computed(() => stats.value.active_repairs)
const completedRepairs = computed(() => stats.value.completed_repairs)
const totalSpent = computed(() => stats.value.total_spent)
const pendingOtPayments = computed(() => stats.value.pending_ot_payments || 0)

// Methods
const getStatusLabel = (status) => {
  return getRepairStatusLabel(status)
}

const getStatusClass = (status) => {
  return normalizeRepairStatus(status)
}

const getNotificationIcon = (type) => {
  const icons = {
    update: '🔄',
    info: 'ℹ️',
    warning: '⚠️',
    error: '❌',
    success: '✓'
  }
  return icons[type] || '📬'
}

const formatDate = (date) => {
  if (!date) return '—'
  return new Intl.DateTimeFormat('es-CL', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(new Date(date))
}

const formatTime = (date) => {
  const now = new Date()
  const base = new Date(date)
  const diff = now - base

  if (diff < 60 * 1000) return 'Hace unos segundos'
  if (diff < 60 * 60 * 1000) return `Hace ${Math.floor(diff / 60 / 1000)} minutos`
  if (diff < 24 * 60 * 60 * 1000) return `Hace ${Math.floor(diff / 60 / 60 / 1000)} horas`
  return formatDate(base)
}

const viewRepair = (repair) => {
  router.push(`/repairs/${repair.id}`)
}

const getProgressClass = (progress) => {
  const normalized = Math.max(0, Math.min(100, Math.round(Number(progress) || 0)))
  return `progress-${normalized}`
}

const handleLogout = () => {
  authStore.logout()
}

const dismissNotification = (id) => {
  notifications.value = notifications.value.filter(n => n.id !== id)
}

const fetchDashboard = async () => {
  isLoading.value = true
  try {
    const { data } = await api.get('/client/dashboard')
    stats.value = data.stats || stats.value
    activeRepairsList.value = data.active_repairs || []
    notifications.value = data.notifications || []
  } catch (err) {
    showError(err.response?.data?.detail || 'Error cargando dashboard')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchDashboard()
})
</script>
