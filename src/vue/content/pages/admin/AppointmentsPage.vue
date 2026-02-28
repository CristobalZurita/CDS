<template>
	<AdminLayout title="Citas" subtitle="Gestión de citas y agendamientos">
		<!-- Filtros -->
		<div class="appointments-filters mb-4">
			<div class="btn-group" role="group">
				<button
					type="button"
					class="btn"
					:class="filter === 'all' ? 'btn-primary' : 'btn-outline-primary'"
					data-testid="appointments-filter-all"
					@click="filter = 'all'"
				>
					Todas
				</button>
				<button
					type="button"
					class="btn"
					:class="filter === 'pendiente' ? 'btn-warning' : 'btn-outline-warning'"
					data-testid="appointments-filter-pending"
					@click="filter = 'pendiente'"
				>
					Pendientes
				</button>
				<button
					type="button"
					class="btn"
					:class="filter === 'confirmado' ? 'btn-success' : 'btn-outline-success'"
					data-testid="appointments-filter-confirmed"
					@click="filter = 'confirmado'"
				>
					Confirmadas
				</button>
				<button
					type="button"
					class="btn"
					:class="filter === 'cancelado' ? 'btn-secondary' : 'btn-outline-secondary'"
					data-testid="appointments-filter-cancelled"
					@click="filter = 'cancelado'"
				>
					Canceladas
				</button>
			</div>
			<button class="btn btn-outline-primary ms-3" data-testid="appointments-refresh" @click="loadAppointments">
				<i class="fa-solid fa-refresh me-1"></i> Actualizar
			</button>
		</div>

		<!-- Loading -->
		<div v-if="loading" class="text-center py-5">
			<div class="spinner-border text-primary" role="status">
				<span class="visually-hidden">Cargando...</span>
			</div>
		</div>

		<!-- Lista de citas -->
		<div v-else-if="filteredAppointments.length > 0" class="appointments-list" data-testid="appointments-list">
			<div
				v-for="appointment in filteredAppointments"
				:key="appointment.id"
				class="appointment-card"
				:class="'status-' + appointment.estado"
			>
				<div class="appointment-header">
					<div class="appointment-info">
						<h5 class="mb-1">{{ appointment.nombre }}</h5>
						<p class="mb-0 text-muted small">
							<i class="fa-solid fa-envelope me-1"></i> {{ appointment.email }}
						</p>
						<p class="mb-0 text-muted small">
							<i class="fa-solid fa-phone me-1"></i> {{ appointment.telefono }}
						</p>
					</div>
					<div class="appointment-status">
						<span class="badge" :class="getStatusBadgeClass(appointment.estado)">
							{{ getStatusLabel(appointment.estado) }}
						</span>
					</div>
				</div>

				<div class="appointment-body">
					<div class="appointment-datetime">
						<i class="fa-solid fa-calendar me-2"></i>
						<strong>{{ formatDate(appointment.fecha) }}</strong>
						<span class="ms-2 text-muted">{{ formatTime(appointment.fecha) }}</span>
					</div>
					<p v-if="appointment.mensaje" class="appointment-message mt-2 mb-0">
						<i class="fa-solid fa-comment me-1"></i> {{ appointment.mensaje }}
					</p>
				</div>

				<div class="appointment-actions">
					<button
						v-if="appointment.estado === 'pendiente'"
						class="btn btn-sm btn-success me-2"
						@click="confirmAppointment(appointment)"
					>
						<i class="fa-solid fa-check me-1"></i> Confirmar
					</button>
					<button
						v-if="appointment.estado !== 'cancelado'"
						class="btn btn-sm btn-outline-danger"
						@click="cancelAppointment(appointment)"
					>
						<i class="fa-solid fa-times me-1"></i> Cancelar
					</button>
					<button
						class="btn btn-sm btn-outline-secondary ms-2"
						@click="deleteAppointment(appointment)"
					>
						<i class="fa-solid fa-trash"></i>
					</button>
				</div>
			</div>
		</div>

		<!-- Empty state -->
		<div v-else class="text-center py-5 text-muted" data-testid="appointments-empty">
			<i class="fa-solid fa-calendar-xmark fa-3x mb-3"></i>
			<p>No hay citas {{ filter !== 'all' ? 'con estado "' + filter + '"' : '' }}</p>
		</div>
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
		pendiente: 'bg-warning text-dark',
		confirmado: 'bg-success',
		cancelado: 'bg-secondary'
	}
	return classes[status] || 'bg-secondary'
}

onMounted(() => {
	loadAppointments()
})
</script>

<style scoped lang="scss">
@import "/src/scss/_theming.scss";

.appointments-filters {
	display: flex;
	align-items: center;
	flex-wrap: wrap;
	gap: 1rem;
}

.appointments-list {
	display: flex;
	flex-direction: column;
	gap: 1rem;
}

.appointment-card {
	background: $vintage-beige;
	border-radius: 12px;
	padding: 1.25rem;
	border-left: 4px solid $text-muted;
	box-shadow: 0 2px 8px rgba($color-black, 0.08);
	transition: all 0.2s;

	&.status-pendiente {
		border-left-color: $color-warning;
	}

	&.status-confirmado {
		border-left-color: $color-green-700-legacy;
	}

	&.status-cancelado {
		border-left-color: $color-secondary-legacy;
		opacity: 0.7;
	}

	&:hover {
		box-shadow: 0 4px 12px rgba($color-black, 0.12);
	}
}

.appointment-header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 1rem;
}

.appointment-info h5 {
	color: $brand-text;
	font-weight: 600;
}

.appointment-datetime {
	font-size: 1rem;
	color: $brand-text;
}

.appointment-message {
	font-size: 0.9rem;
	color: $text-muted;
	font-style: italic;
}

.appointment-actions {
	margin-top: 1rem;
	padding-top: 1rem;
	border-top: 1px solid rgba($color-black, 0.08);
	display: flex;
	flex-wrap: wrap;
	gap: 0.5rem;
}

@media (max-width: 768px) {
	.appointments-filters {
		flex-direction: column;
		align-items: stretch;
	}

	.btn-group {
		width: 100%;
	}

	.appointment-header {
		flex-direction: column;
		gap: 0.5rem;
	}
}
</style>
