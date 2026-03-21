<template>
  <NeoDashActiveSection
    eyebrow="Entrada"
    title="Resumen operativo"
    description="Panorama rapido de reparaciones, compras, pagos y actividad reciente."
  >
    <template #actions>
      <button class="neo-dash-inline-link" type="button" @click="$emit('select-section', 'repairs')">
        <i class="fa-solid fa-screwdriver-wrench"></i>
        Reparaciones
      </button>
      <button class="neo-dash-inline-link" type="button" @click="$emit('select-section', 'payments')">
        <i class="fa-solid fa-money-check-dollar"></i>
        Pagos
      </button>
      <button class="neo-dash-inline-link" type="button" @click="$emit('select-section', 'purchases')">
        <i class="fa-solid fa-cart-shopping"></i>
        Compras
      </button>
    </template>

    <div class="neo-dash-stat-grid">
      <article class="neo-dash-mini-card">
        <span class="neo-dash-stat-label">Pendientes</span>
        <strong class="neo-dash-stat-value">{{ pendingRepairs }}</strong>
      </article>
      <article class="neo-dash-mini-card">
        <span class="neo-dash-stat-label">En proceso</span>
        <strong class="neo-dash-stat-value">{{ activeRepairs }}</strong>
      </article>
      <article class="neo-dash-mini-card">
        <span class="neo-dash-stat-label">Pagos OT</span>
        <strong class="neo-dash-stat-value">{{ pendingOtPayments }}</strong>
      </article>
      <article class="neo-dash-mini-card">
        <span class="neo-dash-stat-label">Carrito</span>
        <strong class="neo-dash-stat-value">{{ cartItemsCount }}</strong>
      </article>
    </div>

    <div class="neo-dash-overview-grid">
      <article class="neo-dash-card">
        <div class="neo-dash-item-head">
          <div>
            <h3 class="neo-dash-card-title">Reparaciones activas</h3>
            <p class="neo-dash-card-copy">Lo que necesita atencion ahora mismo.</p>
          </div>
          <span class="neo-dash-status in_progress">{{ activeRepairsList.length }}</span>
        </div>

        <div v-if="activeRepairsList.length > 0" class="neo-dash-list">
          <article
            v-for="repair in activeRepairsList.slice(0, 3)"
            :key="repair.id"
            class="neo-dash-item"
          >
            <div class="neo-dash-item-head">
              <div>
                <h4 class="neo-dash-item-title">{{ repair.instrument }}</h4>
                <p class="neo-dash-item-meta">
                  OT {{ repair.repair_code || repair.repair_number || repair.id }} · {{ formatDate(repair.date_in) }}
                </p>
              </div>
              <span class="neo-dash-status" :class="getStatusClass(repair.status_normalized || repair.status)">
                {{ getStatusLabel(repair.status_normalized || repair.status) }}
              </span>
            </div>
            <div class="neo-dash-progress">
              <div class="neo-dash-progress-track">
                <div class="neo-dash-progress-fill" :style="{ width: `${repair.progress}%` }"></div>
              </div>
              <p class="neo-dash-progress-copy">{{ repair.progress }}% completado</p>
            </div>
          </article>
        </div>
        <div v-else class="neo-dash-empty">
          <p class="neo-dash-empty-copy">No hay reparaciones activas en este momento.</p>
          <router-link class="neo-dash-link-btn neo-dash-link-btn--primary" to="/cotizador">
            Solicitar cotizacion
          </router-link>
        </div>
      </article>

      <article class="neo-dash-card">
        <div class="neo-dash-item-head">
          <div>
            <h3 class="neo-dash-card-title">Actividad reciente</h3>
            <p class="neo-dash-card-copy">Notificaciones y movimiento del portal.</p>
          </div>
          <span class="neo-dash-status">{{ notifications.length }}</span>
        </div>

        <div v-if="notifications.length > 0" class="neo-dash-list">
          <article
            v-for="notification in notifications.slice(0, 3)"
            :key="notification.id"
            class="neo-dash-item"
          >
            <div class="neo-dash-item-head">
              <div>
                <h4 class="neo-dash-item-title">{{ getNotificationIcon(notification.type) }}</h4>
                <p class="neo-dash-item-copy">{{ notification.message }}</p>
              </div>
            </div>
            <p class="neo-dash-item-meta">{{ formatTime(notification.date) }}</p>
          </article>
        </div>
        <div v-else class="neo-dash-empty">
          <p class="neo-dash-empty-copy">No hay notificaciones nuevas por ahora.</p>
        </div>
      </article>

      <article class="neo-dash-callout">
        <h3 class="neo-dash-callout-title">Siguiente mejor accion</h3>
        <p class="neo-dash-callout-copy">
          {{ overviewCallout }}
        </p>
        <div class="neo-dash-inline-actions">
          <button
            v-if="pendingOtPayments > 0"
            class="neo-dash-inline-link"
            type="button"
            @click="$emit('select-section', 'payments')"
          >
            Revisar pagos
          </button>
          <button
            v-else-if="pendingRepairs > 0 || activeRepairs > 0"
            class="neo-dash-inline-link"
            type="button"
            @click="$emit('select-section', 'repairs')"
          >
            Seguir reparaciones
          </button>
          <button
            v-else-if="cartItemsCount > 0 || pendingStoreRequests > 0"
            class="neo-dash-inline-link"
            type="button"
            @click="$emit('select-section', 'purchases')"
          >
            Continuar compra
          </button>
          <router-link v-else class="neo-dash-inline-link" to="/agendar">
            Agendar diagnóstico
          </router-link>
        </div>
        <div class="neo-dash-divider"></div>
        <div class="neo-dash-mini-grid">
          <article class="neo-dash-mini-card">
            <span class="neo-dash-stat-label">Completadas</span>
            <strong class="neo-dash-stat-value">{{ completedRepairs }}</strong>
          </article>
          <article class="neo-dash-mini-card">
            <span class="neo-dash-stat-label">Total invertido</span>
            <strong class="neo-dash-stat-value">{{ totalSpent }}</strong>
          </article>
        </div>
      </article>
    </div>
  </NeoDashActiveSection>
</template>

<script setup>
import { computed } from 'vue'
import NeoDashActiveSection from './NeoDashActiveSection.vue'

const props = defineProps({
  pendingRepairs: { type: Number, default: 0 },
  activeRepairs: { type: Number, default: 0 },
  completedRepairs: { type: Number, default: 0 },
  totalSpent: { type: String, default: '—' },
  pendingOtPayments: { type: Number, default: 0 },
  cartItemsCount: { type: Number, default: 0 },
  pendingStoreRequests: { type: Number, default: 0 },
  activeRepairsList: { type: Array, default: () => [] },
  notifications: { type: Array, default: () => [] },
  getStatusLabel: { type: Function, required: true },
  getStatusClass: { type: Function, required: true },
  formatDate: { type: Function, required: true },
  formatTime: { type: Function, required: true },
  getNotificationIcon: { type: Function, required: true },
})

defineEmits(['select-section'])

const overviewCallout = computed(() => {
  if (props.pendingOtPayments > 0) {
    return `Tienes ${props.pendingOtPayments} solicitud${props.pendingOtPayments === 1 ? '' : 'es'} con movimiento de pago pendiente.`
  }
  if (props.pendingRepairs > 0 || props.activeRepairs > 0) {
    return `Hay ${props.pendingRepairs + props.activeRepairs} reparacion${props.pendingRepairs + props.activeRepairs === 1 ? '' : 'es'} que requieren seguimiento.`
  }
  if (props.cartItemsCount > 0 || props.pendingStoreRequests > 0) {
    return 'Hay compras en curso que puedes revisar o completar desde el mismo panel.'
  }
  return 'El sistema esta despejado. Puedes cotizar, agendar o revisar tu historial cuando quieras.'
})
</script>

<style src="./neoDashboardShared.css"></style>
