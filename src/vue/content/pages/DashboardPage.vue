<template>
  <div v-if="isAdmin" class="redirect-notice">
    <p>Redirigiendo al panel de administración...</p>
  </div>
  <div v-else class="dashboard-page">
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
const isAdmin = computed(() => authStore.user?.role === 'admin' || authStore.user?.is_admin === true)

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
  // ADITIVO: Redirigir admins al nuevo panel de ZERO
  if (isAdmin.value) {
    window.location.href = 'http://localhost:5174/admin'
    return
  }
  fetchDashboard()
})
</script>

<style scoped>
.redirect-notice {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at 20% 10%, rgba(236, 107, 0, 0.25) 0%, rgba(62, 60, 56, 0.95) 45%, rgba(0, 0, 0, 0.98) 100%);
  color: white;
  font-size: 1.25rem;
}

.dashboard-page {
  min-height: 100vh;
  background: radial-gradient(circle at 20% 10%, rgba(236, 107, 0, 0.25) 0%, rgba(62, 60, 56, 0.95) 45%, rgba(0, 0, 0, 0.98) 100%);
  padding: var(--spacer-xl) var(--spacer-md);
}

.dashboard-container {
  max-width: 1600px;
  margin: 0 auto;
}

/* Header */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacer-xl);
  background: var(--color-light);
  padding: var(--spacer-xl);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  border: 1px solid rgba(62, 60, 56, 0.2);
}

.dashboard-header h1 {
  margin: 0 0 var(--spacer-sm) 0;
  color: var(--color-dark);
  font-size: var(--text-2xl);
}

.welcome-text {
  margin: 0;
  color: var(--gray-600);
}

.header-actions {
  display: flex;
  gap: var(--spacer-md);
}

.btn-primary {
  padding: var(--spacer-sm) var(--spacer-lg);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  color: var(--color-light);
  border: none;
  border-radius: var(--radius-md);
  font-weight: var(--fw-semibold);
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: var(--spacer-sm);
  transition: var(--transition-fast);
  box-shadow: var(--shadow-md);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--spacer-lg);
  margin-bottom: var(--spacer-xl);
}

.stat-card {
  background: var(--color-light);
  border-radius: var(--radius-lg);
  padding: var(--spacer-lg);
  display: flex;
  gap: var(--spacer-md);
  box-shadow: var(--shadow-md);
  transition: var(--transition-fast);
  border: 1px solid rgba(62, 60, 56, 0.18);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.stat-icon {
  font-size: var(--text-2xl);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: var(--radius-md);
}

.stat-icon.pending {
  background: rgba(255, 193, 7, 0.25);
}

.stat-icon.active {
  background: rgba(236, 107, 0, 0.25);
}

.stat-icon.completed {
  background: rgba(236, 107, 0, 0.2);
}

.stat-icon.total {
  background: rgba(232, 147, 90, 0.25);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: var(--text-xl);
  font-weight: var(--fw-bold);
  color: var(--color-dark);
  margin-bottom: var(--spacer-xs);
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--gray-600);
}

/* Dashboard Content */
.dashboard-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacer-xl);
  margin-bottom: var(--spacer-xl);
}

.column h2 {
  margin: 0 0 var(--spacer-lg) 0;
  color: var(--color-light);
  font-size: var(--text-lg);
}

.notifications-title {
  margin-top: var(--spacer-xl);
}

/* Repairs List */
.repairs-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-lg);
}

.repair-card {
  background: var(--color-light);
  border-radius: var(--radius-lg);
  padding: var(--spacer-lg);
  box-shadow: var(--shadow-md);
  border-left: 4px solid var(--color-primary);
  transition: var(--transition-fast);
}

.repair-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateX(4px);
}

.repair-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacer-md);
  padding-bottom: var(--spacer-md);
  border-bottom: 1px solid rgba(62, 60, 56, 0.12);
}

.repair-info h3 {
  margin: 0 0 var(--spacer-xs) 0;
  color: var(--color-dark);
  font-size: var(--text-lg);
}

.repair-id {
  margin: 0;
  color: var(--gray-600);
  font-size: var(--text-sm);
}

.repair-status {
  padding: var(--spacer-sm) var(--spacer-md);
  border-radius: var(--radius-pill);
  font-size: var(--text-sm);
  font-weight: var(--fw-semibold);
  white-space: nowrap;
}

.repair-status.waiting,
.repair-status.waiting_parts {
  background: rgba(232, 147, 90, 0.18);
  color: var(--color-dark);
}

.repair-status.in-progress,
.repair-status.in_progress {
  background: rgba(236, 107, 0, 0.2);
  color: var(--color-dark);
}

.repair-status.ingreso,
.repair-status.diagnostico,
.repair-status.presupuesto,
.repair-status.aprobado {
  background: rgba(232, 147, 90, 0.25);
  color: var(--color-dark);
}

.repair-status.en_trabajo,
.repair-status.listo {
  background: rgba(236, 107, 0, 0.2);
  color: var(--color-dark);
}

.repair-status.entregado,
.repair-status.noventena,
.repair-status.archivado {
  background: rgba(236, 107, 0, 0.18);
  color: var(--color-dark);
}

.repair-status.rechazado {
  background: rgba(220, 53, 69, 0.18);
  color: var(--color-dark);
}

.repair-status.pending_quote,
.repair-status.quoted,
.repair-status.approved,
.repair-status.testing {
  background: rgba(232, 147, 90, 0.25);
  color: var(--color-dark);
}

.repair-status.completed,
.repair-status.delivered {
  background: rgba(236, 107, 0, 0.18);
  color: var(--color-dark);
}

.repair-details {
  margin-bottom: var(--spacer-md);
  font-size: var(--text-base);
}

.repair-details p {
  margin: var(--spacer-sm) 0;
  color: var(--gray-600);
}

.repair-progress {
  margin-bottom: var(--spacer-md);
}

.progress-bar {
  height: 8px;
  background: rgba(62, 60, 56, 0.15);
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-bottom: var(--spacer-sm);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary-light), var(--color-primary));
  transition: all 0.3s ease-in-out;
}

.progress-fill.progress-0 { width: 0%; }
.progress-fill.progress-25 { width: 25%; }
.progress-fill.progress-50 { width: 50%; }
.progress-fill.progress-75 { width: 75%; }
.progress-fill.progress-100 { width: 100%; }

.progress-text {
  font-size: var(--text-sm);
  color: var(--gray-600);
}

.repair-actions {
  text-align: right;
}

.btn-link {
  background: none;
  border: none;
  color: var(--color-primary);
  cursor: pointer;
  text-decoration: none;
  font-weight: var(--fw-semibold);
  padding: 0;
  transition: var(--transition-fast);
}

.btn-link:hover {
  color: var(--color-primary-light);
}

/* Quick Actions */
.quick-actions {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacer-md);
  margin-bottom: var(--spacer-xl);
}

.action-card {
  background: var(--color-light);
  border-radius: var(--radius-lg);
  padding: var(--spacer-md);
  display: flex;
  gap: var(--spacer-md);
  text-decoration: none;
  color: var(--color-dark);
  box-shadow: var(--shadow-md);
  transition: var(--transition-fast);
  border: 1px solid rgba(62, 60, 56, 0.18);
}

.action-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateX(4px);
  border-left: 4px solid var(--color-primary);
}

.action-icon {
  font-size: var(--text-2xl);
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 50px;
}

.action-text h4 {
  margin: 0 0 var(--spacer-xs) 0;
  color: var(--color-dark);
  font-size: var(--text-base);
}

.action-text p {
  margin: 0;
  color: var(--gray-600);
  font-size: var(--text-sm);
}

/* Notifications */
.notifications-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-md);
}

.notification-card {
  background: var(--color-light);
  border-radius: var(--radius-lg);
  padding: var(--spacer-md);
  display: flex;
  gap: var(--spacer-md);
  box-shadow: var(--shadow-md);
  border-left: 4px solid rgba(62, 60, 56, 0.3);
}

.notification-card.update {
  border-left-color: var(--color-primary-light);
  background: rgba(232, 147, 90, 0.12);
}

.notification-card.info {
  border-left-color: var(--color-primary-light);
  background: rgba(232, 147, 90, 0.12);
}

.notification-card.warning {
  border-left-color: var(--color-primary);
  background: rgba(236, 107, 0, 0.12);
}

.notification-card.error {
  border-left-color: var(--color-danger);
  background: rgba(220, 53, 69, 0.12);
}

.notification-card.success {
  border-left-color: var(--color-primary);
  background: rgba(236, 107, 0, 0.12);
}

.notification-icon {
  font-size: var(--text-2xl);
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
}

.notification-content {
  flex: 1;
}

.notification-message {
  margin: 0 0 var(--spacer-xs) 0;
  color: var(--color-dark);
  font-size: var(--text-base);
}

.notification-time {
  margin: 0;
  color: var(--gray-600);
  font-size: var(--text-xs);
}

.notification-close {
  background: none;
  border: none;
  color: var(--gray-600);
  cursor: pointer;
  font-size: var(--text-xl);
  padding: 0;
  transition: var(--transition-fast);
}

.notification-close:hover {
  color: var(--color-dark);
}

/* Empty State */
.empty-state {
  background: var(--color-light);
  border-radius: var(--radius-lg);
  padding: var(--spacer-2xl);
  text-align: center;
  box-shadow: var(--shadow-md);
  border: 1px solid rgba(62, 60, 56, 0.18);
}

.empty-state p {
  margin: 0 0 var(--spacer-lg) 0;
  color: var(--gray-600);
  font-size: var(--text-base);
}

.btn-secondary {
  padding: var(--spacer-sm) var(--spacer-lg);
  background: rgba(236, 107, 0, 0.15);
  color: var(--color-dark);
  border: 2px solid rgba(236, 107, 0, 0.6);
  border-radius: var(--radius-md);
  cursor: pointer;
  text-decoration: none;
  font-weight: var(--fw-semibold);
  display: inline-block;
  transition: var(--transition-fast);
}

.btn-secondary:hover {
  background: rgba(236, 107, 0, 0.3);
  border-color: rgba(236, 107, 0, 0.75);
}

.btn-logout {
  padding: var(--spacer-sm) var(--spacer-md);
  background: rgba(236, 107, 0, 0.12);
  color: var(--color-dark);
  border: 2px solid rgba(236, 107, 0, 0.55);
  border-radius: var(--radius-md);
  font-weight: var(--fw-semibold);
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-logout:hover {
  background: rgba(236, 107, 0, 0.28);
  border-color: rgba(236, 107, 0, 0.75);
}

/* Responsive */
@media (max-width: 992px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-page {
    padding: var(--spacer-md);
  }

  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacer-lg);
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .repair-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacer-sm);
  }
}
</style>
