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
                  <div class="progress-fill" :style="{ width: repair.progress + '%' }"></div>
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
          <h2 style="margin-top: 2rem">Notificaciones</h2>

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

const router = useRouter()
const authStore = useAuthStore()

// Mock Data
const activeRepairsList = ref([
  {
    id: 'REP-2025-001',
    instrument: 'Moog Minimoog Model D',
    fault: 'Filtro no responde',
    status: 'in-progress',
    date_in: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    estimated_completion: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
    progress: 65
  },
  {
    id: 'REP-2025-002',
    instrument: 'Roland TR-808',
    fault: 'Controlador MIDI sin respuesta',
    status: 'waiting',
    date_in: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    estimated_completion: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000),
    progress: 20
  }
])

const notifications = ref([
  {
    id: 1,
    type: 'update',
    message: 'Tu reparación REP-2025-001 ha avanzado a 65%',
    date: new Date(Date.now() - 2 * 60 * 60 * 1000)
  },
  {
    id: 2,
    type: 'info',
    message: 'Recordatorio: Tu cita está programada para mañana a las 14:00',
    date: new Date(Date.now() - 5 * 60 * 60 * 1000)
  },
  {
    id: 3,
    type: 'warning',
    message: 'Tu instrumento está en almacenamiento desde hace 25 días',
    date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000)
  }
])

// Computed
const userFirstName = computed(() => {
  return authStore.user?.first_name || 'Cliente'
})

const pendingRepairs = computed(() => {
  return activeRepairsList.value.filter(r => r.status === 'waiting').length
})

const activeRepairs = computed(() => {
  return activeRepairsList.value.filter(r => r.status === 'in-progress').length
})

const completedRepairs = computed(() => 75) // Mock value

const totalSpent = computed(() => {
  return '2.450.000'
}) // Mock value

// Methods
const getStatusLabel = (status) => {
  const labels = {
    'pending': '⏳ Pendiente',
    'waiting': '⌛ En Espera',
    'in-progress': '🔧 En Proceso',
    'completed': '✓ Completada',
    'cancelled': '✕ Cancelada'
  }
  return labels[status] || status
}

const getNotificationIcon = (type) => {
  const icons = {
    'update': '🔄',
    'info': 'ℹ️',
    'warning': '⚠️',
    'error': '❌',
    'success': '✓'
  }
  return icons[type] || '📬'
}

const formatDate = (date) => {
  return new Intl.DateTimeFormat('es-CL', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date)
}

const formatTime = (date) => {
  const now = new Date()
  const diff = now - date

  if (diff < 60 * 1000) return 'Hace unos segundos'
  if (diff < 60 * 60 * 1000) return `Hace ${Math.floor(diff / 60 / 1000)} minutos`
  if (diff < 24 * 60 * 60 * 1000) return `Hace ${Math.floor(diff / 60 / 60 / 1000)} horas`
  return formatDate(date)
}

const viewRepair = (repair) => {
  router.push(`/repairs/${repair.id}`)
}

const dismissNotification = (id) => {
  notifications.value = notifications.value.filter(n => n.id !== id)
}

onMounted(() => {
  // Aquí iría la lógica para cargar datos reales del backend
  console.log('Dashboard loaded')
})
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem 1rem;
}

.dashboard-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dashboard-header h1 {
  margin: 0 0 0.5rem 0;
  color: #2d3748;
  font-size: 2rem;
}

.welcome-text {
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

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  font-size: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 10px;
}

.stat-icon.pending {
  background: #fed7d7;
}

.stat-icon.active {
  background: #bee3f8;
}

.stat-icon.completed {
  background: #c6f6d5;
}

.stat-icon.total {
  background: #feebc8;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #718096;
}

/* Dashboard Content */
.dashboard-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.column h2 {
  margin: 0 0 1.5rem 0;
  color: #2d3748;
  font-size: 1.3rem;
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

.repair-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.repair-info h3 {
  margin: 0 0 0.25rem 0;
  color: #2d3748;
  font-size: 1.1rem;
}

.repair-id {
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

.repair-status.waiting {
  background: #fed7d7;
  color: #742a2a;
}

.repair-status.in-progress {
  background: #bee3f8;
  color: #2c5282;
}

.repair-status.completed {
  background: #c6f6d5;
  color: #22543d;
}

.repair-details {
  margin-bottom: 1rem;
  font-size: 0.95rem;
}

.repair-details p {
  margin: 0.5rem 0;
  color: #4a5568;
}

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

.repair-actions {
  text-align: right;
}

.btn-link {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  text-decoration: none;
  font-weight: 600;
  padding: 0;
  transition: all 0.2s;
}

.btn-link:hover {
  color: #764ba2;
}

/* Quick Actions */
.quick-actions {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

.action-card {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  gap: 1rem;
  text-decoration: none;
  color: #2d3748;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.2s;
  border-left: 4px solid transparent;
}

.action-card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
  transform: translateX(4px);
  border-left-color: #667eea;
}

.action-icon {
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 50px;
}

.action-text h4 {
  margin: 0 0 0.25rem 0;
  color: #2d3748;
  font-size: 0.95rem;
}

.action-text p {
  margin: 0;
  color: #718096;
  font-size: 0.85rem;
}

/* Notifications */
.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.notification-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  gap: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #e2e8f0;
}

.notification-card.update {
  border-left-color: #4299e1;
  background: #ebf8ff;
}

.notification-card.info {
  border-left-color: #3182ce;
  background: #ebf8ff;
}

.notification-card.warning {
  border-left-color: #ed8936;
  background: #fffaf0;
}

.notification-card.error {
  border-left-color: #f56565;
  background: #fff5f5;
}

.notification-card.success {
  border-left-color: #48bb78;
  background: #f0fff4;
}

.notification-icon {
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
}

.notification-content {
  flex: 1;
}

.notification-message {
  margin: 0 0 0.25rem 0;
  color: #2d3748;
  font-size: 0.95rem;
}

.notification-time {
  margin: 0;
  color: #a0aec0;
  font-size: 0.8rem;
}

.notification-close {
  background: none;
  border: none;
  color: #cbd5e0;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0;
  transition: color 0.2s;
}

.notification-close:hover {
  color: #4a5568;
}

/* Empty State */
.empty-state {
  background: white;
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.empty-state p {
  margin: 0 0 1.5rem 0;
  color: #718096;
  font-size: 1rem;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: #edf2f7;
  color: #4a5568;
  border: 2px solid #cbd5e0;
  border-radius: 8px;
  cursor: pointer;
  text-decoration: none;
  font-weight: 600;
  display: inline-block;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #e2e8f0;
  border-color: #a0aec0;
}

/* Responsive */
@media (max-width: 1024px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-page {
    padding: 1rem;
  }

  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1.5rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .repair-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>

