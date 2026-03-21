<template>
  <header class="neo-dash-top-shell">
    <div class="neo-dash-clock-shell">
      <div class="neo-dash-clock-block">
        <p class="neo-dash-eyebrow">Portal cliente CDS</p>
        <div class="neo-dash-clock-line">
          <strong class="neo-dash-clock-time">{{ clockTime }}</strong>
          <div class="neo-dash-clock-meta-stack">
            <span class="neo-dash-clock-day">{{ clockWeekday }}</span>
            <span class="neo-dash-clock-date">{{ clockDate }}</span>
          </div>
        </div>
      </div>
      <div class="neo-dash-clock-side">
        <div class="neo-dash-clock-actions">
          <button class="neo-dash-quick-circle" type="button" @click="$emit('open-sections')">
            <i class="fa-solid fa-grip"></i>
            <span>menu</span>
          </button>
          <button class="neo-dash-quick-circle" type="button" :disabled="isRefreshing" @click="$emit('refresh')">
            <i class="fa-solid fa-rotate-right"></i>
            <span>{{ isRefreshing ? 'sync' : 'refresh' }}</span>
          </button>
        </div>
        <article class="neo-dash-pulse-shell">
          <div class="neo-dash-pulse-copy">
            <p class="neo-dash-spotlight-label">Pulso actual</p>
            <h2 class="neo-dash-spotlight-title">{{ spotlightTitle }}</h2>
            <p class="neo-dash-spotlight-text">{{ spotlightCopy }}</p>
          </div>
          <div class="neo-dash-spotlight-metrics">
            <span class="neo-dash-spotlight-pill">
              <strong>{{ pendingRepairs + activeRepairs }}</strong>
              OTs
            </span>
            <span class="neo-dash-spotlight-pill">
              <strong>{{ pendingOtPayments + notificationsCount }}</strong>
              avisos
            </span>
          </div>
        </article>
      </div>
    </div>

    <div class="neo-dash-top-head">
      <div class="neo-dash-shell-badges">
        <span class="neo-dash-shell-badge" :style="{ '--neo-section-accent': activeSectionMeta?.accent || '#4d4a47' }">
          <i :class="activeSectionMeta?.icon || 'fa-solid fa-wave-square'"></i>
          {{ activeSectionMeta?.label || 'Resumen' }}
        </span>
        <span class="neo-dash-shell-badge">
          <i class="fa-solid fa-circle"></i>
          {{ greetingLine }}
        </span>
      </div>
      <div class="neo-dash-top-copy">
        <h1 class="neo-dash-title">Hola, {{ userFirstName || 'cliente' }}</h1>
        <p class="neo-dash-lead">{{ activeSectionMeta?.title || 'Mi panel de control' }}</p>
        <p class="neo-dash-meta">{{ activeSectionMeta?.description || '' }}</p>
      </div>
      <div class="neo-dash-actions">
        <router-link class="neo-dash-link-btn neo-dash-link-btn--primary" to="/cotizador">
          <i class="fa-solid fa-plus"></i>
          Nueva cotizacion
        </router-link>
        <router-link class="neo-dash-link-btn neo-dash-link-btn--secondary" to="/agendar">
          <i class="fa-solid fa-calendar-check"></i>
          Agendar
        </router-link>
        <button class="neo-dash-btn neo-dash-btn--secondary" type="button" @click="$emit('logout')">
          <i class="fa-solid fa-right-from-bracket"></i>
          Cerrar sesion
        </button>
      </div>
    </div>

    <div class="neo-dash-summary-strip">
      <div class="neo-dash-metrics">
        <span class="neo-dash-metric-pill neo-dash-metric-pill--green">
          <i class="fa-solid fa-screwdriver-wrench"></i>
          <strong>{{ pendingRepairs }}</strong>
          OTs pendientes
        </span>
        <span class="neo-dash-metric-pill neo-dash-metric-pill--red">
          <i class="fa-solid fa-money-check-dollar"></i>
          <strong>{{ pendingOtPayments }}</strong>
          pagos
        </span>
        <span class="neo-dash-metric-pill neo-dash-metric-pill--violet">
          <i class="fa-solid fa-bell"></i>
          <strong>{{ notificationsCount }}</strong>
          avisos
        </span>
        <span class="neo-dash-metric-pill neo-dash-metric-pill--blue">
          <i class="fa-solid fa-cart-shopping"></i>
          <strong>{{ cartItemsCount }}</strong>
          carrito
        </span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
  userFirstName: {
    type: String,
    default: 'cliente',
  },
  activeSectionMeta: {
    type: Object,
    default: () => ({}),
  },
  pendingRepairs: {
    type: Number,
    default: 0,
  },
  activeRepairs: {
    type: Number,
    default: 0,
  },
  pendingOtPayments: {
    type: Number,
    default: 0,
  },
  notificationsCount: {
    type: Number,
    default: 0,
  },
  cartItemsCount: {
    type: Number,
    default: 0,
  },
  isRefreshing: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['logout', 'open-sections', 'refresh'])

const now = ref(new Date())
let clockTimer = null

const clockTime = computed(() => {
  return new Intl.DateTimeFormat('es-CL', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(now.value)
})

const clockWeekday = computed(() => {
  return new Intl.DateTimeFormat('es-CL', {
    weekday: 'long',
  }).format(now.value)
})

const clockDate = computed(() => {
  return new Intl.DateTimeFormat('es-CL', {
    day: 'numeric',
    month: 'long',
  }).format(now.value)
})

const greetingLine = computed(() => {
  return `${clockWeekday.value} · ${clockDate.value}`
})

const spotlightTitle = computed(() => {
  if (props.pendingOtPayments > 0) return 'Hay pagos que requieren movimiento'
  if (props.pendingRepairs > 0) return 'Tienes reparaciones esperando avance'
  if (props.activeRepairs > 0) return 'Tus reparaciones siguen activas'
  if (props.cartItemsCount > 0) return 'Hay una compra lista para continuar'
  if (props.notificationsCount > 0) return 'Hay actividad nueva en tu panel'
  return 'El panel está al día'
})

const spotlightCopy = computed(() => {
  if (props.pendingOtPayments > 0) return 'Prioriza comprobantes y solicitudes asociadas para mantener el flujo del taller al día.'
  if (props.pendingRepairs > 0) return 'Revisa ingresos y cotizaciones para no perder trazabilidad del estado real de tus equipos.'
  if (props.activeRepairs > 0) return 'Desde aquí puedes seguir progreso, tiempos y próximos pasos sin salir del contexto principal.'
  if (props.cartItemsCount > 0) return 'Tu carrito y las solicitudes de tienda ya están integradas al mismo panel operativo.'
  if (props.notificationsCount > 0) return 'Los avisos recientes quedan concentrados para que no dependas de navegar varias páginas.'
  return 'Puedes usar el panel como entrada única para cotizar, agendar y revisar historial.'
})

onMounted(() => {
  clockTimer = window.setInterval(() => {
    now.value = new Date()
  }, 30000)
})

onUnmounted(() => {
  if (clockTimer) window.clearInterval(clockTimer)
})
</script>

<style src="./neoDashboardShared.css"></style>
