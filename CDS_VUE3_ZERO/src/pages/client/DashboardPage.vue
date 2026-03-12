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

<style scoped src="./commonClientPage.css"></style>
