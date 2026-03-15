<template>
  <main class="repairs-page">
    <section class="repairs-header">
      <div>
        <h1>Mis Reparaciones</h1>
        <p class="subtitle">Historial completo de tus reparaciones.</p>
      </div>

      <div class="header-actions">
        <router-link to="/cotizador" class="btn-primary">+ Nueva Cotizacion</router-link>
        <button class="btn-secondary" :disabled="isLoading" @click="loadRepairs">
          {{ isLoading ? 'Actualizando...' : 'Actualizar' }}
        </button>
      </div>
    </section>

    <section class="filters">
      <label>
        <span>Filtrar por estado</span>
        <select v-model="selectedStatus" data-testid="repairs-status-filter">
          <option value="">Todos</option>
          <option value="pending_quote">Ingreso / Diagnostico</option>
          <option value="in_progress">En proceso</option>
          <option value="completed">Completadas / Entregadas</option>
          <option value="cancelled">Rechazadas</option>
        </select>
      </label>
    </section>

    <p v-if="loadingError" class="repairs-error">{{ loadingError }}</p>

    <section v-if="filteredRepairs.length > 0" class="repairs-list">
      <article
        v-for="repair in filteredRepairs"
        :key="repair.id"
        class="repair-card"
        data-testid="repairs-card"
      >
        <header class="repair-card-header">
          <div>
            <h2>{{ repair.instrument }}</h2>
            <p class="repair-ticket">OT: {{ repair.repair_code || repair.repair_number || repair.id }}</p>
          </div>
          <span class="repair-status" :class="repair.status_normalized">
            {{ getStatusLabel(repair.status_normalized || repair.status) }}
          </span>
        </header>

        <div class="repair-details">
          <p><strong>Falla:</strong> {{ repair.fault || 'Sin detalle' }}</p>
          <p><strong>Ingresado:</strong> {{ formatDate(repair.date_in) }}</p>
          <p v-if="repair.date_out"><strong>Completado:</strong> {{ formatDate(repair.date_out) }}</p>
          <p v-if="repair.cost || repair.cost === 0"><strong>Costo:</strong> {{ formatPrice(repair.cost) }}</p>
        </div>

        <div v-if="shouldShowProgress(repair)" class="repair-progress">
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: `${repair.progress}%` }"></div>
          </div>
          <span>{{ repair.progress }}% completado</span>
        </div>

        <div class="repair-actions">
          <button class="btn-secondary" data-testid="repair-view" @click="viewRepair(repair)">
            Ver detalles
          </button>
        </div>
      </article>
    </section>

    <section v-else class="empty-state" data-testid="repairs-empty">
      <p>No hay reparaciones para el filtro actual.</p>
      <router-link to="/cotizador" class="btn-primary">Solicitar cotizacion</router-link>
    </section>
  </main>
</template>

<script setup>
import { useRepairsPage } from '@/composables/useRepairsPage'

const {
  selectedStatus,
  filteredRepairs,
  isLoading,
  loadingError,
  getStatusLabel,
  formatDate,
  formatPrice,
  shouldShowProgress,
  viewRepair,
  loadRepairs
} = useRepairsPage()
</script>

<style scoped src="./commonClientPage.css"></style>
