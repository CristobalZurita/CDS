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
          <StatusBadge
            :label="getStatusLabel(appointment.estado)"
            :variant="appointmentStatusVariant(appointment.estado)"
            size="sm"
            rounded
          />
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
import { StatusBadge } from '@/components/composite'
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

function appointmentStatusVariant(status) {
  if (status === 'confirmado') return 'success'
  if (status === 'cancelado') return 'neutral'
  return 'warning'
}
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped src="./appointmentsPageShared.css"></style>
