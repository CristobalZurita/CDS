<template>
  <NeoDashActiveSection
    eyebrow="Client"
    title="Notificaciones"
    description="Avisos del portal que deben poder descartarse o revisarse con rapidez."
  >
    <template #actions>
      <button class="neo-dash-inline-link" type="button" @click="$emit('select-section', 'overview')">
        Volver al resumen
      </button>
    </template>

    <div class="neo-dash-mini-grid">
      <article class="neo-dash-mini-card">
        <span class="neo-dash-stat-label">Avisos visibles</span>
        <strong class="neo-dash-stat-value">{{ notifications.length }}</strong>
      </article>
      <article class="neo-dash-mini-card">
        <span class="neo-dash-stat-label">Ultimo movimiento</span>
        <strong class="neo-dash-stat-value">{{ latestLabel }}</strong>
      </article>
    </div>

    <div v-if="notifications.length > 0" class="neo-dash-list">
      <article v-for="notification in notifications" :key="notification.id" class="neo-dash-item">
        <div class="neo-dash-item-head">
          <div>
            <h3 class="neo-dash-item-title">{{ getNotificationIcon(notification.type) }}</h3>
            <p class="neo-dash-item-meta">{{ notification.type || 'info' }}</p>
            <p class="neo-dash-item-copy">{{ notification.message }}</p>
          </div>
          <span class="neo-dash-status">{{ formatTime(notification.date) }}</span>
        </div>
        <div class="neo-dash-inline-actions">
          <button class="neo-dash-inline-link" type="button" @click="dismissNotification(notification.id)">
            Cerrar
          </button>
        </div>
      </article>
    </div>
    <div v-else class="neo-dash-empty">
      <p class="neo-dash-empty-copy">No hay notificaciones nuevas.</p>
    </div>
  </NeoDashActiveSection>
</template>

<script setup>
import { computed } from 'vue'
import NeoDashActiveSection from './NeoDashActiveSection.vue'

const props = defineProps({
  notifications: { type: Array, default: () => [] },
  getNotificationIcon: { type: Function, required: true },
  formatTime: { type: Function, required: true },
  dismissNotification: { type: Function, required: true },
})

defineEmits(['select-section'])

const latestLabel = computed(() => {
  const first = Array.isArray(props.notifications) ? props.notifications[0] : null
  return first?.date ? props.formatTime(first.date) : 'Sin avisos'
})
</script>

<style src="./neoDashboardShared.css"></style>
