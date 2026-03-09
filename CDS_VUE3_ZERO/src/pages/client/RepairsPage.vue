<template>
  <main class="repairs-page">
    <section class="repairs-header">
      <div>
        <h1>Mis Reparaciones</h1>
        <p class="subtitle">Historial completo de tus reparaciones.</p>
      </div>

      <div class="header-actions">
        <router-link to="/cotizador-ia" class="btn-primary">+ Nueva Cotizacion</router-link>
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
      <router-link to="/cotizador-ia" class="btn-primary">Solicitar cotizacion</router-link>
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

<style scoped>
.repairs-page {
  padding: 1rem;
  display: grid;
  gap: 1rem;
}

.repairs-header,
.filters,
.repair-card,
.empty-state {
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
  border-radius: 0.9rem;
  background: var(--cds-white);
}

.repairs-header,
.filters,
.empty-state {
  padding: 0.9rem;
}

.repairs-header {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: space-between;
  align-items: center;
}

.repairs-header h1 {
  margin: 0;
  font-size: var(--cds-text-3xl);
}

.subtitle {
  margin: 0.3rem 0 0;
  color: var(--cds-text-muted);
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.btn-primary,
.btn-secondary {
  min-height: 44px;
  padding: 0.65rem 0.9rem;
  border-radius: 0.55rem;
  font-size: var(--cds-text-base);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  border: 1px solid var(--cds-primary);
  background: var(--cds-primary);
  color: var(--cds-white);
}

.btn-secondary {
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  background: var(--cds-white);
  color: var(--cds-text-normal);
  cursor: pointer;
}

.filters label {
  display: grid;
  gap: 0.35rem;
}

.filters span {
  font-size: var(--cds-text-sm);
}

.filters select {
  min-height: 44px;
  border-radius: 0.55rem;
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  padding: 0.65rem 0.8rem;
  font-size: var(--cds-text-base);
}

.repairs-error {
  margin: 0;
  border: 1px solid #f4c7c3;
  background: #fef3f2;
  color: #b42318;
  border-radius: 0.6rem;
  padding: 0.75rem;
}

.repairs-list {
  display: grid;
  gap: 0.7rem;
}

.repair-card {
  padding: 0.9rem;
  display: grid;
  gap: 0.6rem;
}

.repair-card-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.5rem;
}

.repair-card-header h2 {
  margin: 0;
  font-size: var(--cds-text-lg);
}

.repair-ticket {
  margin: 0.2rem 0 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.repair-status {
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, white);
  background: color-mix(in srgb, var(--cds-primary) 12%, white);
  padding: 0.3rem 0.7rem;
  font-size: var(--cds-text-sm);
  align-self: flex-start;
}

.repair-details {
  display: grid;
  gap: 0.25rem;
}

.repair-details p {
  margin: 0;
}

.repair-progress {
  display: grid;
  gap: 0.3rem;
}

.progress-track {
  height: 8px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--cds-light) 70%, white);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--cds-primary);
}

.repair-progress span {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.repair-actions {
  display: flex;
  justify-content: flex-end;
}

.empty-state {
  display: grid;
  gap: 0.5rem;
}

.empty-state p {
  margin: 0;
}
</style>
