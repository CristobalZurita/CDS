<template>
  <NeoDashActiveSection
    eyebrow="Repair / OT"
    title="Mis reparaciones"
    description="Seguimiento unificado de OTs activas, historial y estados del taller."
  >
    <template #actions>
      <router-link class="neo-dash-inline-link" to="/repairs">Ver historial completo</router-link>
      <router-link class="neo-dash-inline-link" to="/cotizador">Nueva cotizacion</router-link>
    </template>

    <div class="neo-dash-chip-row">
      <button
        v-for="filter in filters"
        :key="filter.key"
        type="button"
        class="neo-dash-chip"
        :class="{ 'neo-dash-chip--active': filter.key === selectedStatus }"
        @click="$emit('update:selected-status', filter.key)"
      >
        {{ filter.label }}
      </button>
    </div>

    <p v-if="loadingError" class="neo-dash-error">{{ loadingError }}</p>
    <p v-else-if="isLoading" class="neo-dash-note">Cargando reparaciones...</p>

    <div v-else-if="repairs.length > 0" class="neo-dash-list">
      <article v-for="repair in repairs" :key="repair.id" class="neo-dash-item">
        <div class="neo-dash-item-head">
          <div>
            <h3 class="neo-dash-item-title">{{ repair.instrument }}</h3>
            <p class="neo-dash-item-meta">
              OT {{ repair.repair_code || repair.repair_number || repair.id }} · {{ formatDate(repair.date_in) }}
            </p>
          </div>
          <span class="neo-dash-status" :class="repair.status_normalized">
            {{ getStatusLabel(repair.status_normalized || repair.status) }}
          </span>
        </div>

        <p class="neo-dash-item-copy"><strong>Falla:</strong> {{ repair.fault || 'Sin detalle' }}</p>
        <p v-if="repair.cost || repair.cost === 0" class="neo-dash-item-meta">
          <strong>Costo:</strong> {{ formatPrice(repair.cost) }}
        </p>

        <div v-if="shouldShowProgress(repair)" class="neo-dash-progress">
          <div class="neo-dash-progress-track">
            <div class="neo-dash-progress-fill" :style="{ width: `${repair.progress}%` }"></div>
          </div>
          <p class="neo-dash-progress-copy">{{ repair.progress }}% completado</p>
        </div>

        <div class="neo-dash-inline-actions">
          <button class="neo-dash-inline-link" type="button" @click="viewRepair(repair)">
            Ver detalle
          </button>
        </div>
      </article>
    </div>

    <div v-else class="neo-dash-empty">
      <p class="neo-dash-empty-copy">No hay reparaciones para el filtro actual.</p>
      <router-link class="neo-dash-link-btn neo-dash-link-btn--primary" to="/cotizador">
        Solicitar cotizacion
      </router-link>
    </div>
  </NeoDashActiveSection>
</template>

<script setup>
import NeoDashActiveSection from './NeoDashActiveSection.vue'

defineProps({
  selectedStatus: { type: String, default: '' },
  repairs: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false },
  loadingError: { type: String, default: '' },
  getStatusLabel: { type: Function, required: true },
  formatDate: { type: Function, required: true },
  formatPrice: { type: Function, required: true },
  shouldShowProgress: { type: Function, required: true },
  viewRepair: { type: Function, required: true },
})

defineEmits(['update:selected-status'])

const filters = [
  { key: '', label: 'Todas' },
  { key: 'pending_quote', label: 'Ingreso' },
  { key: 'in_progress', label: 'En proceso' },
  { key: 'completed', label: 'Completadas' },
  { key: 'cancelled', label: 'Rechazadas' },
]
</script>

<style src="./neoDashboardShared.css"></style>
