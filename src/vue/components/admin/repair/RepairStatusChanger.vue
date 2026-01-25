<template>
	<div class="status-changer">
		<div class="current-status">
			<span class="status-label">Estado actual:</span>
			<span class="status-badge" :style="{ backgroundColor: currentStatusColor }">
				{{ currentStatusName }}
			</span>
			<span class="status-progress">
				<div class="progress-bar">
					<div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
				</div>
				<span class="progress-text">{{ progressPercent }}%</span>
			</span>
		</div>

		<div v-if="!isTerminal && allowedTransitions.length > 0" class="status-actions">
			<label class="form-label">Cambiar estado a:</label>
			<div class="transitions-grid">
				<button
					v-for="transition in allowedTransitions"
					:key="transition.id"
					class="transition-btn"
					:class="{ 'btn-danger': transition.id === 10 }"
					:disabled="changing"
					@click="confirmTransition(transition)"
				>
					<i :class="transition.icon" class="me-2"></i>
					{{ transition.name }}
				</button>
			</div>
		</div>

		<div v-else-if="isTerminal" class="terminal-notice">
			<i class="fa-solid fa-lock me-2"></i>
			Estado terminal - No se permiten más cambios
		</div>

		<!-- Modal de confirmación -->
		<div v-if="showConfirmModal" class="confirm-overlay" @click.self="showConfirmModal = false">
			<div class="confirm-modal">
				<h5>Confirmar cambio de estado</h5>
				<p>
					¿Cambiar de <strong>{{ currentStatusName }}</strong> a
					<strong>{{ pendingTransition?.name }}</strong>?
				</p>
				<div class="mb-3">
					<label class="form-label">Nota (opcional):</label>
					<textarea v-model="transitionNote" class="form-control" rows="2" placeholder="Agregar comentario sobre el cambio..."></textarea>
				</div>
				<div class="d-flex gap-2 justify-content-end">
					<button class="btn btn-secondary" @click="showConfirmModal = false">Cancelar</button>
					<button class="btn btn-primary" :disabled="changing" @click="executeTransition">
						{{ changing ? 'Cambiando...' : 'Confirmar' }}
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { api } from '@/services/api'

const props = defineProps({
	repairId: { type: [Number, String], required: true },
	currentStatusId: { type: Number, required: true },
	statuses: { type: Array, default: () => [] }
})

const emit = defineEmits(['statusChanged'])

// Estado de la máquina de estados (mismo que backend)
const STATE_CONFIG = {
	1: { name: 'Ingreso', color: '#6c757d', progress: 0, icon: 'fa-solid fa-door-open', transitions: [2, 10] },
	2: { name: 'Diagnóstico', color: '#17a2b8', progress: 15, icon: 'fa-solid fa-stethoscope', transitions: [3, 10] },
	3: { name: 'Presupuesto', color: '#fd7e14', progress: 30, icon: 'fa-solid fa-file-invoice-dollar', transitions: [4, 10] },
	4: { name: 'Aprobado', color: '#28a745', progress: 40, icon: 'fa-solid fa-thumbs-up', transitions: [5, 10] },
	5: { name: 'En trabajo', color: '#ff8c42', progress: 60, icon: 'fa-solid fa-wrench', transitions: [6, 10] },
	6: { name: 'Listo', color: '#20c997', progress: 80, icon: 'fa-solid fa-check-circle', transitions: [7, 10] },
	7: { name: 'Entregado', color: '#198754', progress: 90, icon: 'fa-solid fa-hand-holding', transitions: [8] },
	8: { name: 'Noventena', color: '#4d77ff', progress: 95, icon: 'fa-solid fa-hourglass-half', transitions: [9] },
	9: { name: 'Archivado', color: '#6f42c1', progress: 100, icon: 'fa-solid fa-box-archive', transitions: [] },
	10: { name: 'Rechazado', color: '#dc3545', progress: 0, icon: 'fa-solid fa-ban', transitions: [9] }
}

// State
const showConfirmModal = ref(false)
const pendingTransition = ref(null)
const transitionNote = ref('')
const changing = ref(false)

// Computed
const currentConfig = computed(() => STATE_CONFIG[props.currentStatusId] || STATE_CONFIG[1])
const currentStatusName = computed(() => currentConfig.value.name)
const currentStatusColor = computed(() => currentConfig.value.color)
const progressPercent = computed(() => currentConfig.value.progress)
const isTerminal = computed(() => props.currentStatusId === 9)

const allowedTransitions = computed(() => {
	const transitions = currentConfig.value.transitions || []
	return transitions.map(id => ({
		id,
		name: STATE_CONFIG[id]?.name || `Estado ${id}`,
		icon: STATE_CONFIG[id]?.icon || 'fa-solid fa-arrow-right'
	}))
})

// Methods
const confirmTransition = (transition) => {
	pendingTransition.value = transition
	transitionNote.value = ''
	showConfirmModal.value = true
}

const executeTransition = async () => {
	if (!pendingTransition.value) return

	changing.value = true
	try {
		const res = await api.put(`/repairs/${props.repairId}`, {
			status_id: pendingTransition.value.id,
			status_notes: transitionNote.value || null
		})

		emit('statusChanged', {
			newStatusId: pendingTransition.value.id,
			repair: res.data || res
		})

		showConfirmModal.value = false
		pendingTransition.value = null
		transitionNote.value = ''
	} catch (error) {
		console.error('Error cambiando estado:', error)
		alert(error.response?.data?.detail || 'Error al cambiar estado')
	} finally {
		changing.value = false
	}
}
</script>

<style scoped lang="scss">
@import "/src/scss/_theming.scss";

.status-changer {
	background: $vintage-beige;
	border-radius: 12px;
	padding: 1.25rem;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.current-status {
	display: flex;
	align-items: center;
	gap: 1rem;
	flex-wrap: wrap;
	margin-bottom: 1rem;
}

.status-label {
	font-weight: 500;
	color: $brand-text;
}

.status-badge {
	padding: 0.5rem 1rem;
	border-radius: 20px;
	color: white;
	font-weight: 600;
	font-size: 0.9em;
}

.status-progress {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	flex: 1;
	min-width: 150px;

	.progress-bar {
		flex: 1;
		height: 8px;
		background: #e0e0e0;
		border-radius: 4px;
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		background: linear-gradient(90deg, $brand-primary, lighten($brand-primary, 10%));
		transition: width 0.3s ease;
	}

	.progress-text {
		font-weight: 600;
		color: $brand-primary;
		min-width: 40px;
	}
}

.status-actions {
	border-top: 1px solid rgba(0, 0, 0, 0.1);
	padding-top: 1rem;
}

.transitions-grid {
	display: flex;
	flex-wrap: wrap;
	gap: 0.5rem;
}

.transition-btn {
	padding: 0.5rem 1rem;
	border: 2px solid $brand-primary;
	background: white;
	color: $brand-primary;
	border-radius: 8px;
	font-weight: 500;
	cursor: pointer;
	transition: all 0.2s ease;

	&:hover {
		background: $brand-primary;
		color: white;
	}

	&.btn-danger {
		border-color: #dc3545;
		color: #dc3545;

		&:hover {
			background: #dc3545;
			color: white;
		}
	}

	&:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
}

.terminal-notice {
	padding: 1rem;
	background: rgba(0, 0, 0, 0.05);
	border-radius: 8px;
	color: #666;
	text-align: center;
}

.confirm-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
}

.confirm-modal {
	background: white;
	padding: 1.5rem;
	border-radius: 12px;
	max-width: 400px;
	width: 90%;
	box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);

	h5 {
		margin-bottom: 1rem;
		color: $brand-text;
	}
}
</style>
