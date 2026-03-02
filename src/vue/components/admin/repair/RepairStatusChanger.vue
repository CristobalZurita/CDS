<template>
	<div class="status-changer">
		<div class="current-status">
			<span class="status-label">Estado actual:</span>
			<span class="status-badge" :class="currentStatusClass" data-testid="repair-current-status">
				{{ currentStatusName }}
			</span>
			<span class="status-progress">
				<div class="progress-bar">
					<div class="progress-fill" :class="getProgressClass(progressPercent)"></div>
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
					:data-testid="`repair-transition-${transition.id}`"
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
					<button class="btn btn-secondary" data-testid="repair-status-cancel" @click="showConfirmModal = false">Cancelar</button>
					<button class="btn btn-primary" data-testid="repair-status-confirm" :disabled="changing" @click="executeTransition">
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
	1: { name: 'Ingreso', color: 'var(--status-color-1)', progress: 0, icon: 'fa-solid fa-door-open', transitions: [2, 10] },
	2: { name: 'Diagnóstico', color: 'var(--status-color-2)', progress: 15, icon: 'fa-solid fa-stethoscope', transitions: [3, 10] },
	3: { name: 'Presupuesto', color: 'var(--status-color-3)', progress: 30, icon: 'fa-solid fa-file-invoice-dollar', transitions: [4, 10] },
	4: { name: 'Aprobado', color: 'var(--status-color-4)', progress: 40, icon: 'fa-solid fa-thumbs-up', transitions: [5, 10] },
	5: { name: 'En trabajo', color: 'var(--status-color-5)', progress: 60, icon: 'fa-solid fa-wrench', transitions: [6, 10] },
	6: { name: 'Listo', color: 'var(--status-color-6)', progress: 80, icon: 'fa-solid fa-check-circle', transitions: [7, 10] },
	7: { name: 'Entregado', color: 'var(--status-color-7)', progress: 90, icon: 'fa-solid fa-hand-holding', transitions: [8] },
	8: { name: 'Noventena', color: 'var(--status-color-8)', progress: 95, icon: 'fa-solid fa-hourglass-half', transitions: [9] },
	9: { name: 'Archivado', color: 'var(--status-color-9)', progress: 100, icon: 'fa-solid fa-box-archive', transitions: [] },
	10: { name: 'Rechazado', color: 'var(--status-color-10)', progress: 0, icon: 'fa-solid fa-ban', transitions: [9] }
}

// State
const showConfirmModal = ref(false)
const pendingTransition = ref(null)
const transitionNote = ref('')
const changing = ref(false)

// Computed
const currentConfig = computed(() => STATE_CONFIG[props.currentStatusId] || STATE_CONFIG[1])
const currentStatusName = computed(() => currentConfig.value.name)
const currentStatusClass = computed(() => `status-${props.currentStatusId}`)
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

const getProgressClass = (progress) => {
	const normalized = Math.max(0, Math.min(100, Math.round(Number(progress) || 0)))
	return `progress-${normalized}`
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
