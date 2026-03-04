<template>
  <AdminLayout title="Citas" subtitle="Gestión de citas y agendamientos">
    <section class="appointments-page">
      <header class="appointments-page__header">
        <div class="appointments-page__filters">
          <button
            type="button"
            class="appointments-page__filter"
            :class="{ 'appointments-page__filter--active': filter === 'all' }"
            data-testid="appointments-filter-all"
            @click="filter = 'all'"
          >
            Todas
          </button>
          <button
            type="button"
            class="appointments-page__filter appointments-page__filter--warning"
            :class="{ 'appointments-page__filter--active appointments-page__filter--warning-active': filter === 'pendiente' }"
            data-testid="appointments-filter-pending"
            @click="filter = 'pendiente'"
          >
            Pendientes
          </button>
          <button
            type="button"
            class="appointments-page__filter appointments-page__filter--success"
            :class="{ 'appointments-page__filter--active appointments-page__filter--success-active': filter === 'confirmado' }"
            data-testid="appointments-filter-confirmed"
            @click="filter = 'confirmado'"
          >
            Confirmadas
          </button>
          <button
            type="button"
            class="appointments-page__filter appointments-page__filter--secondary"
            :class="{ 'appointments-page__filter--active appointments-page__filter--secondary-active': filter === 'cancelado' }"
            data-testid="appointments-filter-cancelled"
            @click="filter = 'cancelado'"
          >
            Canceladas
          </button>
        </div>

        <button
          type="button"
          class="appointments-page__action"
          data-testid="appointments-refresh"
          @click="loadAppointments"
        >
          <i class="fa-solid fa-refresh"></i>
          <span>Actualizar</span>
        </button>
      </header>

      <section v-if="loading" class="appointments-page__loading">
        <div class="appointments-page__spinner" role="status">
          <span class="visually-hidden">Cargando...</span>
        </div>
      </section>

      <section
        v-else-if="filteredAppointments.length > 0"
        class="appointments-page__list"
        data-testid="appointments-list"
      >
        <article
          v-for="appointment in filteredAppointments"
          :key="appointment.id"
          class="appointments-page__card"
          :class="'appointments-page__card--' + appointment.estado"
          data-testid="appointment-row"
        >
          <div class="appointments-page__card-header">
            <div class="appointments-page__identity">
              <h2 class="appointments-page__name">{{ appointment.nombre }}</h2>
              <p class="appointments-page__meta">
                <i class="fa-solid fa-envelope"></i>
                <span>{{ appointment.email }}</span>
              </p>
              <p class="appointments-page__meta">
                <i class="fa-solid fa-phone"></i>
                <span>{{ appointment.telefono }}</span>
              </p>
            </div>

            <div class="appointments-page__status">
              <span class="appointments-page__status-badge" :class="getStatusBadgeClass(appointment.estado)">
                {{ getStatusLabel(appointment.estado) }}
              </span>
            </div>
          </div>

          <div class="appointments-page__card-body">
            <div class="appointments-page__datetime">
              <i class="fa-solid fa-calendar"></i>
              <strong>{{ formatDate(appointment.fecha) }}</strong>
              <span class="appointments-page__meta appointments-page__meta--inline">{{ formatTime(appointment.fecha) }}</span>
            </div>

            <p v-if="appointment.mensaje" class="appointments-page__message">
              <i class="fa-solid fa-comment"></i>
              <span>{{ appointment.mensaje }}</span>
            </p>
          </div>

          <div class="appointments-page__card-actions">
            <button
              v-if="appointment.estado === 'pendiente'"
              type="button"
              class="appointments-page__card-button appointments-page__card-button--success"
              data-testid="appointment-confirm"
              @click="confirmAppointment(appointment)"
            >
              <i class="fa-solid fa-check"></i>
              <span>Confirmar</span>
            </button>
            <button
              v-if="appointment.estado !== 'cancelado'"
              type="button"
              class="appointments-page__card-button appointments-page__card-button--danger"
              data-testid="appointment-cancel"
              @click="cancelAppointment(appointment)"
            >
              <i class="fa-solid fa-times"></i>
              <span>Cancelar</span>
            </button>
            <button
              type="button"
              class="appointments-page__card-button appointments-page__card-button--secondary"
              data-testid="appointment-delete"
              @click="deleteAppointment(appointment)"
            >
              <i class="fa-solid fa-trash"></i>
              <span>Eliminar</span>
            </button>
          </div>
        </article>
      </section>

      <section v-else class="appointments-page__empty" data-testid="appointments-empty">
        <i class="fa-solid fa-calendar-xmark"></i>
        <p>No hay citas {{ filter !== 'all' ? 'con estado "' + filter + '"' : '' }}</p>
      </section>
    </section>
  </AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/services/api'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'

const appointments = ref([])
const loading = ref(false)
const filter = ref('all')

const filteredAppointments = computed(() => {
	if (filter.value === 'all') return appointments.value
	return appointments.value.filter(a => a.estado === filter.value)
})

const loadAppointments = async () => {
	loading.value = true
	try {
		const response = await api.get('/appointments/')
		appointments.value = response.data || response || []
	} catch (error) {
		console.error('Error cargando citas:', error)
		appointments.value = []
	} finally {
		loading.value = false
	}
}

const confirmAppointment = async (appointment) => {
	try {
		await api.patch(`/appointments/${appointment.id}`, { estado: 'confirmado' })
		await loadAppointments()
	} catch (error) {
		console.error('Error confirmando cita:', error)
		alert('Error al confirmar la cita')
	}
}

const cancelAppointment = async (appointment) => {
	if (!confirm(`¿Cancelar la cita de ${appointment.nombre}?`)) return
	try {
		await api.patch(`/appointments/${appointment.id}`, { estado: 'cancelado' })
		await loadAppointments()
	} catch (error) {
		console.error('Error cancelando cita:', error)
		alert('Error al cancelar la cita')
	}
}

const deleteAppointment = async (appointment) => {
	if (!confirm(`¿Eliminar permanentemente la cita de ${appointment.nombre}?`)) return
	try {
		await api.delete(`/appointments/${appointment.id}`)
		await loadAppointments()
	} catch (error) {
		console.error('Error eliminando cita:', error)
		alert('Error al eliminar la cita')
	}
}

const formatDate = (dateStr) => {
	const date = new Date(dateStr)
	return new Intl.DateTimeFormat('es-CL', {
		weekday: 'long',
		year: 'numeric',
		month: 'long',
		day: 'numeric'
	}).format(date)
}

const formatTime = (dateStr) => {
	const date = new Date(dateStr)
	return new Intl.DateTimeFormat('es-CL', {
		hour: '2-digit',
		minute: '2-digit'
	}).format(date)
}

const getStatusLabel = (status) => {
	const labels = {
		pendiente: 'Pendiente',
		confirmado: 'Confirmada',
		cancelado: 'Cancelada'
	}
	return labels[status] || status
}

const getStatusBadgeClass = (status) => {
	const classes = {
		pendiente: 'appointments-page__status-badge--warning',
		confirmado: 'appointments-page__status-badge--success',
		cancelado: 'appointments-page__status-badge--secondary'
	}
	return classes[status] || 'appointments-page__status-badge--secondary'
}

onMounted(() => {
	loadAppointments()
})
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.appointments-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-md);
}

.appointments-page__header,
.appointments-page__filters,
.appointments-page__card-header,
.appointments-page__card-actions {
  display: flex;
  gap: var(--spacer-sm);
  flex-wrap: wrap;
}

.appointments-page__header,
.appointments-page__card-header {
  justify-content: space-between;
  align-items: center;
}

.appointments-page__filter,
.appointments-page__action,
.appointments-page__card-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  min-height: 40px;
  padding: 0.65rem 0.95rem;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-base);
}

.appointments-page__filter,
.appointments-page__action {
  border: 1px solid var(--color-primary);
  background: transparent;
  color: var(--color-primary);
}

.appointments-page__filter--active,
.appointments-page__action:hover {
  background: var(--color-primary);
  color: var(--color-white);
}

.appointments-page__filter--warning {
  border-color: var(--color-warning);
  color: var(--color-warning);
}

.appointments-page__filter--warning-active {
  background: var(--color-warning);
  color: var(--color-dark);
}

.appointments-page__filter--success {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.appointments-page__filter--success-active {
  background: var(--color-primary);
  color: var(--color-white);
}

.appointments-page__filter--secondary {
  border-color: var(--color-dark);
  color: var(--color-dark);
}

.appointments-page__filter--secondary-active {
  background: var(--color-dark);
  color: var(--color-white);
}

.appointments-page__loading,
.appointments-page__empty {
  display: grid;
  place-items: center;
  gap: var(--spacer-sm);
  min-height: 240px;
  padding: var(--spacer-lg);
  background: var(--color-white);
  border: 1px solid var(--color-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  color: var(--color-dark);
  text-align: center;
}

.appointments-page__spinner {
  width: 52px;
  height: 52px;
  border: 4px solid color-mix(in srgb, var(--color-primary) 20%, var(--color-white) 80%);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: appointments-spin 0.8s linear infinite;
}

.appointments-page__list {
  display: grid;
  gap: var(--spacer-md);
}

.appointments-page__card {
  padding: var(--spacer-md);
  background: var(--color-white);
  border: 1px solid var(--color-light);
  border-left: 4px solid var(--color-primary);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.appointments-page__card--pendiente {
  border-left-color: var(--color-warning);
}

.appointments-page__card--confirmado {
  border-left-color: var(--color-primary);
}

.appointments-page__card--cancelado {
  border-left-color: var(--color-dark);
}

.appointments-page__identity {
  display: grid;
  gap: 0.35rem;
}

.appointments-page__name {
  margin: 0;
  color: var(--color-dark);
  font-size: var(--text-lg);
  font-weight: 700;
}

.appointments-page__meta,
.appointments-page__message {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin: 0;
  color: var(--color-dark);
  opacity: 0.72;
  font-size: var(--text-sm);
}

.appointments-page__meta--inline {
  opacity: 0.72;
}

.appointments-page__status-badge {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-size: var(--text-xs);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.appointments-page__status-badge--warning {
  background: var(--color-warning);
  color: var(--color-dark);
}

.appointments-page__status-badge--success {
  background: var(--color-primary);
  color: var(--color-white);
}

.appointments-page__status-badge--secondary {
  background: var(--color-dark);
  color: var(--color-white);
}

.appointments-page__card-body {
  display: grid;
  gap: 0.65rem;
  margin-top: var(--spacer-sm);
}

.appointments-page__datetime {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  flex-wrap: wrap;
  color: var(--color-dark);
}

.appointments-page__card-actions {
  margin-top: var(--spacer-md);
}

.appointments-page__card-button {
  border: 0;
  color: var(--color-white);
}

.appointments-page__card-button:hover,
.appointments-page__filter:hover,
.appointments-page__action:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.appointments-page__card-button--success {
  background: var(--color-primary);
}

.appointments-page__card-button--danger {
  background: var(--color-danger);
}

.appointments-page__card-button--secondary {
  background: var(--color-dark);
}

.appointments-page__empty i {
  font-size: 2.5rem;
}

@keyframes appointments-spin {
  to {
    transform: rotate(360deg);
  }
}

@include media-breakpoint-down(md) {
  .appointments-page__header,
  .appointments-page__filters,
  .appointments-page__card-header,
  .appointments-page__card-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .appointments-page__status {
    width: 100%;
  }

  .appointments-page__filter,
  .appointments-page__action,
  .appointments-page__card-button {
    width: 100%;
  }
}
</style>
