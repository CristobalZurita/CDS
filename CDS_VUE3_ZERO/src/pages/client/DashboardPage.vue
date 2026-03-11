<template>
  <main v-if="isAdmin" class="redirect-notice">
    <p>Redirigiendo al panel de administración...</p>
  </main>
  <main v-else class="dashboard-page">
    <section class="dashboard-header">
      <div>
        <h1>Mi Panel de Control</h1>
        <p class="welcome-text">Bienvenido {{ userFirstName || 'cliente' }}</p>
      </div>

      <div class="header-actions">
        <router-link to="/cotizador-ia" class="btn-primary">
          + Nueva Cotizacion
        </router-link>
        <button class="btn-secondary" type="button" data-testid="dashboard-logout" @click="handleLogout">
          Cerrar sesion
        </button>
      </div>
    </section>

    <p v-if="loadingError" class="dashboard-error">{{ loadingError }}</p>

    <section class="stats-grid">
      <article class="stat-card">
        <span class="stat-title">Reparaciones pendientes</span>
        <strong class="stat-value">{{ pendingRepairs }}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-title">En proceso</span>
        <strong class="stat-value">{{ activeRepairs }}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-title">Completadas</span>
        <strong class="stat-value">{{ completedRepairs }}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-title">Total invertido</span>
        <strong class="stat-value">{{ totalSpent }}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-title">Pagos OT pendientes</span>
        <strong class="stat-value">{{ pendingOtPayments }}</strong>
      </article>
    </section>

    <section class="dashboard-grid">
      <article class="panel-card">
        <div class="panel-head">
          <h2>Reparaciones activas</h2>
          <button class="btn-inline" :disabled="isLoading" @click="loadDashboard">
            {{ isLoading ? 'Cargando...' : 'Actualizar' }}
          </button>
        </div>

        <div v-if="activeRepairsList.length > 0" class="repairs-list">
          <article
            v-for="repair in activeRepairsList"
            :key="repair.id"
            class="repair-card"
            data-testid="dashboard-repair-card"
          >
            <header class="repair-header">
              <div>
                <h3>{{ repair.instrument }}</h3>
                <p class="repair-id">OT: {{ repair.repair_code || repair.repair_number || repair.id }}</p>
              </div>
              <span class="repair-status" :class="getStatusClass(repair.status_normalized || repair.status)">
                {{ getStatusLabel(repair.status_normalized || repair.status) }}
              </span>
            </header>

            <p><strong>Falla:</strong> {{ repair.fault || 'Sin detalle' }}</p>
            <p><strong>Ingresado:</strong> {{ formatDate(repair.date_in) }}</p>
            <p v-if="repair.estimated_completion"><strong>Estimado:</strong> {{ formatDate(repair.estimated_completion) }}</p>

            <div class="repair-progress">
              <div class="progress-track">
                <div class="progress-fill" :style="{ width: `${repair.progress}%` }"></div>
              </div>
              <span class="progress-text">{{ repair.progress }}% completado</span>
            </div>

            <div class="repair-actions">
              <button class="btn-inline" data-testid="dashboard-repair-view" @click="viewRepair(repair)">
                Ver detalles
              </button>
            </div>
          </article>
        </div>

        <div v-else class="empty-state" data-testid="dashboard-empty-repairs">
          <p>No tienes reparaciones activas.</p>
          <router-link to="/cotizador-ia" class="btn-primary">Solicitar cotizacion</router-link>
        </div>
      </article>

      <article class="panel-card">
        <h2>Acciones rapidas</h2>
        <div class="quick-actions">
          <router-link to="/cotizador-ia" class="action-card">Nueva cotizacion</router-link>
          <router-link to="/agendar" class="action-card">Agendar cita</router-link>
          <router-link to="/ot-payments" class="action-card">Pagos OT</router-link>
          <router-link to="/repairs" class="action-card">Historial</router-link>
          <router-link to="/profile" class="action-card">Mi perfil</router-link>
        </div>

        <h2 class="notifications-title">Notificaciones</h2>
        <div v-if="notifications.length > 0" class="notifications-list">
          <article
            v-for="notification in notifications"
            :key="notification.id"
            class="notification-card"
            :class="notification.type"
            data-testid="dashboard-notification"
          >
            <div class="notification-main">
              <p class="notification-type">{{ getNotificationIcon(notification.type) }}</p>
              <p class="notification-message">{{ notification.message }}</p>
              <p class="notification-time">{{ formatTime(notification.date) }}</p>
            </div>
            <button
              class="notification-close"
              data-testid="dashboard-notification-dismiss"
              @click="dismissNotification(notification.id)"
            >
              Cerrar
            </button>
          </article>
        </div>
        <div v-else class="empty-state" data-testid="dashboard-empty-notifications">
          <p>No hay notificaciones nuevas.</p>
        </div>
      </article>
    </section>
  </main>
</template>

<script setup>
import { useDashboardPage } from '@/composables/useDashboardPage'
import { useAuthStore } from '@/stores/auth'
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const isAdmin = computed(() => authStore.isAdmin)

// ADITIVO: Redirigir admins directo al panel de administración
onMounted(() => {
  if (isAdmin.value) {
    router.replace('/admin')
  }
})

const {
  isLoading,
  loadingError,
  userFirstName,
  pendingRepairs,
  activeRepairs,
  completedRepairs,
  totalSpent,
  pendingOtPayments,
  activeRepairsList,
  notifications,
  getStatusLabel,
  getStatusClass,
  formatDate,
  formatTime,
  getNotificationIcon,
  dismissNotification,
  viewRepair,
  handleLogout,
  loadDashboard
} = useDashboardPage()
</script>

<style scoped>
.redirect-notice {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--cds-bg, #f5f5f5);
  color: var(--cds-text-normal, #333);
  font-size: 1.25rem;
}

.dashboard-page {
  padding: 1rem;
  display: grid;
  gap: 1rem;
}

.dashboard-header,
.panel-card,
.stat-card {
  background: var(--cds-white);
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
  border-radius: 0.9rem;
}

.dashboard-header {
  padding: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: space-between;
  align-items: center;
}

.dashboard-header h1 {
  margin: 0;
  font-size: var(--cds-text-3xl);
}

.welcome-text {
  margin: 0.3rem 0 0;
  color: var(--cds-text-muted);
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.btn-primary,
.btn-secondary,
.btn-inline,
.action-card,
.notification-close {
  min-height: 44px;
  padding: 0.65rem 0.9rem;
  border-radius: 0.55rem;
  font-size: var(--cds-text-base);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.btn-primary {
  border: 1px solid var(--cds-primary);
  background: var(--cds-primary);
  color: var(--cds-white);
}

.btn-admin {
  border: 1px solid var(--cds-dark);
  background: var(--cds-dark);
  color: var(--cds-white);
  min-height: 44px;
  padding: 0.65rem 0.9rem;
  border-radius: 0.55rem;
  font-size: var(--cds-text-base);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.btn-admin:hover {
  background: color-mix(in srgb, var(--cds-dark) 80%, black);
}

.btn-secondary,
.btn-inline,
.action-card,
.notification-close {
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  background: var(--cds-white);
  color: var(--cds-text-normal);
}

.btn-inline,
.notification-close {
  cursor: pointer;
}

.dashboard-error {
  margin: 0;
  border: 1px solid #f4c7c3;
  background: #fef3f2;
  color: #b42318;
  border-radius: 0.6rem;
  padding: 0.75rem;
}

.stats-grid {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.stat-card {
  padding: 0.9rem;
  display: grid;
  gap: 0.3rem;
}

.stat-title {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.stat-value {
  font-size: var(--cds-text-2xl);
  color: var(--cds-text-normal);
}

.dashboard-grid {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.panel-card {
  padding: 1rem;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  align-items: center;
}

.panel-card h2 {
  margin: 0;
  font-size: var(--cds-text-xl);
}

.repairs-list,
.quick-actions,
.notifications-list {
  margin-top: 0.75rem;
  display: grid;
  gap: 0.6rem;
}

.repair-card {
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  border-radius: 0.75rem;
  padding: 0.8rem;
  display: grid;
  gap: 0.45rem;
}

.repair-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.45rem;
}

.repair-header h3 {
  margin: 0;
  font-size: var(--cds-text-lg);
}

.repair-id {
  margin: 0.2rem 0 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.repair-status {
  border-radius: 999px;
  padding: 0.28rem 0.65rem;
  font-size: var(--cds-text-sm);
  border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, white);
  background: color-mix(in srgb, var(--cds-primary) 12%, white);
}

.repair-progress {
  display: grid;
  gap: 0.25rem;
}

.progress-track {
  width: 100%;
  height: 8px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--cds-light) 70%, white);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--cds-primary);
}

.progress-text {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.repair-actions {
  display: flex;
  justify-content: flex-end;
}

.empty-state {
  margin-top: 0.75rem;
  border: 1px dashed color-mix(in srgb, var(--cds-light) 70%, white);
  border-radius: 0.75rem;
  padding: 0.9rem;
  display: grid;
  gap: 0.5rem;
  justify-items: start;
}

.empty-state p {
  margin: 0;
}

.notifications-title {
  margin-top: 1rem;
}

.notification-card {
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  border-radius: 0.75rem;
  padding: 0.65rem;
  display: flex;
  gap: 0.5rem;
  justify-content: space-between;
}

.notification-main {
  display: grid;
  gap: 0.2rem;
}

.notification-type,
.notification-message,
.notification-time {
  margin: 0;
}

.notification-type {
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
}

.notification-time {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

@media (min-width: 740px) {
  .stats-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .dashboard-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
