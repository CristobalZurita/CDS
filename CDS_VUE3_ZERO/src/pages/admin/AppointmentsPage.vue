<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Citas</h1>
        <p>Gestion de citas y agendamientos.</p>
      </div>
      <button class="btn-secondary" data-testid="appointments-refresh" :disabled="loading" @click="loadAppointments">
        {{ loading ? 'Actualizando...' : 'Actualizar' }}
      </button>
    </header>

    <section class="filter-row">
      <button class="chip" :class="{ active: filter === 'all' }" data-testid="appointments-filter-all" @click="filter = 'all'">Todas</button>
      <button class="chip warning" :class="{ active: filter === 'pendiente' }" data-testid="appointments-filter-pending" @click="filter = 'pendiente'">Pendientes</button>
      <button class="chip success" :class="{ active: filter === 'confirmado' }" data-testid="appointments-filter-confirmed" @click="filter = 'confirmado'">Confirmadas</button>
      <button class="chip neutral" :class="{ active: filter === 'cancelado' }" data-testid="appointments-filter-cancelled" @click="filter = 'cancelado'">Canceladas</button>
    </section>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section v-if="loading" class="empty-state">Cargando citas...</section>

    <section v-else-if="filteredAppointments.length > 0" class="cards-grid" data-testid="appointments-list">
      <article
        v-for="appointment in filteredAppointments"
        :key="appointment.id"
        class="appointment-card"
        :class="`status-${appointment.estado}`"
        data-testid="appointment-row"
      >
        <header class="appointment-head">
          <div>
            <h2>{{ appointment.nombre }}</h2>
            <p>{{ appointment.email }}</p>
            <p>{{ appointment.telefono }}</p>
          </div>
          <span class="status-badge">{{ getStatusLabel(appointment.estado) }}</span>
        </header>

        <div class="appointment-body">
          <p><strong>Fecha:</strong> {{ formatDate(appointment.fecha) }}</p>
          <p><strong>Hora:</strong> {{ formatTime(appointment.fecha) }}</p>
          <p v-if="appointment.mensaje"><strong>Mensaje:</strong> {{ appointment.mensaje }}</p>
        </div>

        <div class="appointment-actions">
          <button
            v-if="appointment.estado === 'pendiente'"
            class="btn-success"
            data-testid="appointment-confirm"
            :disabled="loading"
            @click="confirmAppointment(appointment)"
          >
            Confirmar
          </button>
          <button
            v-if="appointment.estado !== 'cancelado'"
            class="btn-danger"
            data-testid="appointment-cancel"
            :disabled="loading"
            @click="cancelAppointment(appointment)"
          >
            Cancelar
          </button>
          <button
            class="btn-secondary"
            data-testid="appointment-delete"
            :disabled="loading"
            @click="deleteAppointment(appointment)"
          >
            Eliminar
          </button>
        </div>
      </article>
    </section>

    <section v-else class="empty-state" data-testid="appointments-empty">
      No hay citas para el filtro actual.
    </section>
  </main>
</template>

<script setup>
import { useAppointmentsPage } from '@/composables/useAppointmentsPage'

const {
  loading,
  error,
  filter,
  filteredAppointments,
  formatDate,
  formatTime,
  getStatusLabel,
  loadAppointments,
  confirmAppointment,
  cancelAppointment,
  deleteAppointment
} = useAppointmentsPage()
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped>
/* Botones extra de esta página */
.btn-success { min-height: 44px; padding: .65rem .9rem; border-radius: .55rem; font-size: var(--cds-text-base); border: 1px solid #16a34a; background: #16a34a; color: #fff; cursor: pointer; }
/* Filter chips */
.filter-row { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); padding: .9rem; display: flex; flex-wrap: wrap; gap: .5rem; }
.chip { min-height: 44px; padding: .65rem .9rem; border-radius: .55rem; font-size: var(--cds-text-base); border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); background: var(--cds-white); color: var(--cds-text-normal); cursor: pointer; }
.chip.active { border-color: var(--cds-primary); background: color-mix(in srgb, var(--cds-primary) 14%, white); }
.chip.warning.active { border-color: #ca8a04; background: #fef9c3; }
.chip.success.active { border-color: #15803d; background: #dcfce7; }
.chip.neutral.active { border-color: #4b5563; background: #e5e7eb; }
/* Cards de cita */
.cards-grid { display: grid; gap: .7rem; }
.appointment-card { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); padding: .9rem; display: grid; gap: .6rem; border-left: 4px solid var(--cds-primary); }
.appointment-card.status-pendiente { border-left-color: #ca8a04; }
.appointment-card.status-confirmado { border-left-color: #16a34a; }
.appointment-card.status-cancelado { border-left-color: #4b5563; }
.appointment-head { display: flex; flex-wrap: wrap; gap: .6rem; justify-content: space-between; }
.appointment-head h2 { margin: 0; font-size: var(--cds-text-lg); }
.appointment-head p { margin: .2rem 0 0; color: var(--cds-text-muted); }
.status-badge { border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, white); background: color-mix(in srgb, var(--cds-primary) 12%, white); border-radius: 999px; padding: .3rem .7rem; font-size: var(--cds-text-sm); align-self: flex-start; }
.appointment-body p { margin: 0; }
.appointment-actions { display: flex; flex-wrap: wrap; gap: .5rem; }
/* Empty state específico (override del común) */
.empty-state { border: none; display: grid; place-items: center; min-height: 160px; text-align: center; }
</style>
