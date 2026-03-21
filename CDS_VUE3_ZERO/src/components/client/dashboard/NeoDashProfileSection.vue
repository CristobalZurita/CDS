<template>
  <NeoDashActiveSection
    eyebrow="Profile"
    title="Perfil y preferencias"
    description="Datos base del cliente, configuracion rápida y acceso a seguridad."
  >
    <template #actions>
      <router-link class="neo-dash-inline-link" to="/profile">Abrir perfil completo</router-link>
    </template>

    <div class="neo-dash-profile-grid">
      <article class="neo-dash-card">
        <div class="neo-dash-item-head">
          <div>
            <h3 class="neo-dash-card-title">{{ user?.fullName || 'Cliente' }}</h3>
            <p class="neo-dash-card-copy">Cliente desde {{ memberSince || '—' }}</p>
          </div>
          <span class="neo-dash-status">{{ userInitials }}</span>
        </div>

        <div class="neo-dash-list">
          <article class="neo-dash-mini-card">
            <span class="neo-dash-stat-label">Email</span>
            <strong class="neo-dash-stat-value">{{ user?.email || '—' }}</strong>
          </article>
          <article class="neo-dash-mini-card">
            <span class="neo-dash-stat-label">Telefono</span>
            <strong class="neo-dash-stat-value">{{ user?.phone || '—' }}</strong>
          </article>
          <article class="neo-dash-mini-card">
            <span class="neo-dash-stat-label">Direccion</span>
            <strong class="neo-dash-stat-value">{{ user?.address || '—' }}</strong>
          </article>
        </div>
      </article>

      <article class="neo-dash-callout">
        <h3 class="neo-dash-callout-title">Estadisticas del cliente</h3>
        <div class="neo-dash-mini-grid">
          <article class="neo-dash-mini-card">
            <span class="neo-dash-stat-label">Reparaciones</span>
            <strong class="neo-dash-stat-value">{{ totalRepairs }}</strong>
          </article>
          <article class="neo-dash-mini-card">
            <span class="neo-dash-stat-label">Total invertido</span>
            <strong class="neo-dash-stat-value">{{ totalSpent }}</strong>
          </article>
          <article class="neo-dash-mini-card">
            <span class="neo-dash-stat-label">Promedio</span>
            <strong class="neo-dash-stat-value">{{ avgRepairDays != null ? `${avgRepairDays} dias` : '—' }}</strong>
          </article>
        </div>
        <div class="neo-dash-divider"></div>
        <div class="neo-dash-chip-row">
          <span
            v-for="channel in activePreferenceLabels"
            :key="channel"
            class="neo-dash-chip neo-dash-chip--readonly"
          >
            {{ channel }}
          </span>
        </div>
        <div class="neo-dash-inline-actions">
          <router-link class="neo-dash-inline-link" to="/profile">Editar perfil</router-link>
          <router-link class="neo-dash-inline-link" to="/repairs">Ver historial</router-link>
        </div>
      </article>
    </div>
  </NeoDashActiveSection>
</template>

<script setup>
import { computed } from 'vue'
import NeoDashActiveSection from './NeoDashActiveSection.vue'

const props = defineProps({
  user: {
    type: Object,
    default: () => ({}),
  },
  preferences: {
    type: Object,
    default: () => ({}),
  },
  userInitials: {
    type: String,
    default: 'CL',
  },
  memberSince: {
    type: String,
    default: '—',
  },
  totalRepairs: {
    type: Number,
    default: 0,
  },
  totalSpent: {
    type: String,
    default: '—',
  },
  avgRepairDays: {
    type: [Number, null],
    default: null,
  },
})

const activePreferenceLabels = computed(() => {
  const labels = []
  if (props.preferences?.emailNotifications) labels.push('Email activo')
  if (props.preferences?.whatsappNotifications) labels.push('WhatsApp activo')
  if (props.preferences?.smsNotifications) labels.push('SMS activo')
  return labels.length ? labels : ['Sin preferencias definidas']
})
</script>

<style src="./neoDashboardShared.css"></style>
