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
          <button class="btn-logout" type="button" @click="handleLogout">
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
            >
              <div class="repair-header">
                <div class="repair-info">
                  <h3>{{ repair.instrument }}</h3>
                  <p class="repair-id">Ticket: {{ repair.id }}</p>
                </div>
                <div class="repair-status" :class="repair.status">
                  {{ getStatusLabel(repair.status) }}
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
                <button @click="viewRepair(repair)" class="btn-link">Ver detalles →</button>
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
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
            >
              <div class="notification-icon">{{ getNotificationIcon(notification.type) }}</div>
              <div class="notification-content">
                <p class="notification-message">{{ notification.message }}</p>
                <p class="notification-time">{{ formatTime(notification.date) }}</p>
              </div>
              <button
                @click="dismissNotification(notification.id)"
                class="notification-close"
              >
                ✕
              </button>
            </div>
          </div>

          <div v-else class="empty-state">
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

<style lang="scss" scoped>
@import '@/scss/_core.scss';

.dashboard-page {
  min-height: 100vh;
  background: radial-gradient(circle at 20% 10%, rgba($color-secondary, 0.25) 0%, rgba($color-dark, 0.95) 45%, rgba($color-black, 0.98) 100%);
  padding: $spacer-xl $spacer-md;
}

.dashboard-container {
  max-width: $container-max-width;
  margin: 0 auto;
}

/* Header */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacer-xl;
  background: $color-light;
  padding: $spacer-xl;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-xl;
  border: 1px solid rgba($color-dark, 0.2);
}

.dashboard-header h1 {
  margin: 0 0 $spacer-sm 0;
  color: $text-color;
  font-size: $h2-size;
}

.welcome-text {
  margin: 0;
  color: $text-color-muted;
}

.header-actions {
  display: flex;
  gap: $spacer-md;
}

.btn-primary {
  padding: $spacer-sm $spacer-lg;
  background: linear-gradient(135deg, $color-primary, $color-secondary);
  color: $color-light;
  border: none;
  border-radius: $border-radius-md;
  font-weight: $fw-semibold;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: $spacer-sm;
  transition: $transition-fast;
  box-shadow: $shadow-lg;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: $shadow-xl;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: $spacer-lg;
  margin-bottom: $spacer-xl;
}

.stat-card {
  background: $color-light;
  border-radius: $border-radius-lg;
  padding: $spacer-lg;
  display: flex;
  gap: $spacer-md;
  box-shadow: $shadow-lg;
  transition: $transition-fast;
  border: 1px solid rgba($color-dark, 0.18);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: $shadow-md;
}

.stat-icon {
  font-size: $text-2xl;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: $border-radius-md;
}

.stat-icon.pending {
  background: rgba($color-accent, 0.25);
}

.stat-icon.active {
  background: rgba($color-primary, 0.25);
}

.stat-icon.completed {
  background: rgba($color-success, 0.2);
}

.stat-icon.total {
  background: rgba($color-primary-light, 0.25);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: $h3-size;
  font-weight: $fw-bold;
  color: $text-color;
  margin-bottom: $spacer-xs;
}

.stat-label {
  font-size: $text-sm;
  color: $text-color-muted;
}

/* Dashboard Content */
.dashboard-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $spacer-xl;
  margin-bottom: $spacer-xl;
}

.column h2 {
  margin: 0 0 $spacer-lg 0;
  color: $text-color;
  font-size: $h4-size;
}

.notifications-title {
  margin-top: $spacer-xl;
}

/* Repairs List */
.repairs-list {
  display: flex;
  flex-direction: column;
  gap: $spacer-lg;
}

.repair-card {
  background: $color-light;
  border-radius: $border-radius-lg;
  padding: $spacer-lg;
  box-shadow: $shadow-lg;
  border-left: 4px solid $color-primary;
  transition: $transition-fast;
}

.repair-card:hover {
  box-shadow: $shadow-md;
  transform: translateX(4px);
}

.repair-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacer-md;
  padding-bottom: $spacer-md;
  border-bottom: 1px solid rgba($color-dark, 0.12);
}

.repair-info h3 {
  margin: 0 0 $spacer-xs 0;
  color: $text-color;
  font-size: $text-lg;
}

.repair-id {
  margin: 0;
  color: $text-color-muted;
  font-size: $text-sm;
}

.repair-status {
  padding: $spacer-sm $spacer-md;
  border-radius: $border-radius-pill;
  font-size: $text-sm;
  font-weight: $fw-semibold;
  white-space: nowrap;
}

.repair-status.waiting,
.repair-status.waiting_parts {
  background: rgba($color-secondary, 0.18);
  color: $text-color;
}

.repair-status.in-progress,
.repair-status.in_progress {
  background: rgba($color-primary, 0.2);
  color: $text-color;
}

.repair-status.pending_quote,
.repair-status.quoted,
.repair-status.approved,
.repair-status.testing {
  background: rgba($color-primary-light, 0.25);
  color: $text-color;
}

.repair-status.completed,
.repair-status.delivered {
  background: rgba($color-success, 0.18);
  color: $text-color;
}

.repair-details {
  margin-bottom: $spacer-md;
  font-size: $text-base;
}

.repair-details p {
  margin: $spacer-sm 0;
  color: $text-color-muted;
}

.repair-progress {
  margin-bottom: $spacer-md;
}

.progress-bar {
  height: 8px;
  background: rgba($color-dark, 0.15);
  border-radius: $border-radius-sm;
  overflow: hidden;
  margin-bottom: $spacer-sm;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, $color-primary-light, $color-secondary);
  transition: $transition-base;

  @for $i from 0 through 100 {
    &.progress-#{$i} {
      width: #{$i}%;
    }
  }
}

.progress-text {
  font-size: $text-sm;
  color: $text-color-muted;
}

.repair-actions {
  text-align: right;
}

.btn-link {
  background: none;
  border: none;
  color: $color-primary;
  cursor: pointer;
  text-decoration: none;
  font-weight: $fw-semibold;
  padding: 0;
  transition: $transition-fast;
}

.btn-link:hover {
  color: $color-secondary;
}

/* Quick Actions */
.quick-actions {
  display: grid;
  grid-template-columns: 1fr;
  gap: $spacer-md;
  margin-bottom: $spacer-xl;
}

.action-card {
  background: $color-light;
  border-radius: $border-radius-lg;
  padding: $spacer-md;
  display: flex;
  gap: $spacer-md;
  text-decoration: none;
  color: $text-color;
  box-shadow: $shadow-lg;
  transition: $transition-fast;
  border-left: 4px solid transparent;
  border: 1px solid rgba($color-dark, 0.18);
}

.action-card:hover {
  box-shadow: $shadow-xl;
  transform: translateX(4px);
  border-left-color: $color-primary;
}

.action-icon {
  font-size: $h2-size;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 50px;
}

.action-text h4 {
  margin: 0 0 $spacer-xs 0;
  color: $text-color;
  font-size: $text-base;
}

.action-text p {
  margin: 0;
  color: $text-color-muted;
  font-size: $text-sm;
}

/* Notifications */
.notifications-list {
  display: flex;
  flex-direction: column;
  gap: $spacer-md;
}

.notification-card {
  background: $color-light;
  border-radius: $border-radius-lg;
  padding: $spacer-md;
  display: flex;
  gap: $spacer-md;
  box-shadow: $shadow-lg;
  border-left: 4px solid rgba($color-dark, 0.3);
}

.notification-card.update {
  border-left-color: $color-primary-light;
  background: rgba($color-primary-light, 0.12);
}

.notification-card.info {
  border-left-color: $color-secondary;
  background: rgba($color-secondary, 0.12);
}

.notification-card.warning {
  border-left-color: $color-primary;
  background: rgba($color-primary, 0.12);
}

.notification-card.error {
  border-left-color: $color-danger;
  background: rgba($color-danger, 0.12);
}

.notification-card.success {
  border-left-color: $color-success;
  background: rgba($color-success, 0.12);
}

.notification-icon {
  font-size: $text-2xl;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
}

.notification-content {
  flex: 1;
}

.notification-message {
  margin: 0 0 $spacer-xs 0;
  color: $text-color;
  font-size: $text-base;
}

.notification-time {
  margin: 0;
  color: $text-color-muted;
  font-size: $text-xs;
}

.notification-close {
  background: none;
  border: none;
  color: $text-color-muted;
  cursor: pointer;
  font-size: $text-xl;
  padding: 0;
  transition: $transition-fast;
}

.notification-close:hover {
  color: $text-color;
}

/* Empty State */
.empty-state {
  background: $color-light;
  border-radius: $border-radius-lg;
  padding: $spacer-xxl;
  text-align: center;
  box-shadow: $shadow-lg;
  border: 1px solid rgba($color-dark, 0.18);
}

.empty-state p {
  margin: 0 0 $spacer-lg 0;
  color: $text-color-muted;
  font-size: $text-base;
}

.btn-secondary {
  padding: $spacer-sm $spacer-lg;
  background: rgba($color-primary, 0.15);
  color: $text-color;
  border: 2px solid rgba($color-primary, 0.6);
  border-radius: $border-radius-md;
  cursor: pointer;
  text-decoration: none;
  font-weight: $fw-semibold;
  display: inline-block;
  transition: $transition-fast;
}

.btn-secondary:hover {
  background: rgba($color-primary, 0.3);
  border-color: rgba($color-primary, 0.75);
}

.btn-logout {
  padding: $spacer-sm $spacer-md;
  background: rgba($color-primary, 0.12);
  color: $text-color;
  border: 2px solid rgba($color-primary, 0.55);
  border-radius: $border-radius-md;
  font-weight: $fw-semibold;
  cursor: pointer;
  transition: $transition-fast;
}

.btn-logout:hover {
  background: rgba($color-primary, 0.28);
  border-color: rgba($color-primary, 0.75);
}

/* Responsive */
@include media-breakpoint-down(lg) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@include media-breakpoint-down(md) {
  .dashboard-page {
    padding: $spacer-md;
  }

  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: $spacer-lg;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .repair-header {
    flex-direction: column;
    align-items: flex-start;
    gap: $spacer-sm;
  }
}
</style>
