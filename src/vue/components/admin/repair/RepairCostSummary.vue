<template>
	<div class="cost-summary">
		<div class="section-header">
			<h5 class="section-title">
				<i class="fa-solid fa-calculator me-2"></i>Resumen de Costos
			</h5>
		</div>

		<div class="cost-grid">
			<!-- Mano de Obra -->
			<div class="cost-item">
				<div class="cost-icon">
					<i class="fa-solid fa-user-gear"></i>
				</div>
				<div class="cost-details">
					<span class="cost-label">Mano de Obra</span>
					<span class="cost-value">${{ formatNumber(laborCost) }}</span>
				</div>
				<button
					v-if="!isReadOnly"
					class="btn btn-sm btn-outline-secondary edit-btn"
					@click="showLaborModal = true"
				>
					<i class="fa-solid fa-pencil"></i>
				</button>
			</div>

			<!-- Materiales -->
			<div class="cost-item">
				<div class="cost-icon materials">
					<i class="fa-solid fa-microchip"></i>
				</div>
				<div class="cost-details">
					<span class="cost-label">Materiales</span>
					<span class="cost-value">${{ formatNumber(materialsCost) }}</span>
				</div>
				<span class="cost-note" v-if="componentsCount > 0">
					{{ componentsCount }} item{{ componentsCount > 1 ? 's' : '' }}
				</span>
			</div>

			<!-- Otros Gastos -->
			<div class="cost-item" v-if="otherCosts > 0 || !isReadOnly">
				<div class="cost-icon other">
					<i class="fa-solid fa-receipt"></i>
				</div>
				<div class="cost-details">
					<span class="cost-label">Otros Gastos</span>
					<span class="cost-value">${{ formatNumber(otherCosts) }}</span>
				</div>
				<button
					v-if="!isReadOnly"
					class="btn btn-sm btn-outline-secondary edit-btn"
					@click="showOtherModal = true"
				>
					<i class="fa-solid fa-pencil"></i>
				</button>
			</div>

			<!-- Separador -->
			<div class="cost-divider"></div>

			<!-- Total Costo Real -->
			<div class="cost-item total-row">
				<div class="cost-icon total">
					<i class="fa-solid fa-sigma"></i>
				</div>
				<div class="cost-details">
					<span class="cost-label">Costo Total</span>
					<span class="cost-value total-value">${{ formatNumber(totalCost) }}</span>
				</div>
			</div>

			<!-- Precio Cotizado -->
			<div class="cost-item quoted-row" v-if="quotedPrice > 0">
				<div class="cost-icon quoted">
					<i class="fa-solid fa-file-invoice-dollar"></i>
				</div>
				<div class="cost-details">
					<span class="cost-label">Precio Cotizado</span>
					<span class="cost-value">${{ formatNumber(quotedPrice) }}</span>
				</div>
			</div>

			<!-- Margen -->
			<div class="cost-item margin-row" v-if="quotedPrice > 0">
				<div class="cost-icon" :class="marginClass">
					<i :class="marginIcon"></i>
				</div>
				<div class="cost-details">
					<span class="cost-label">Margen</span>
					<span class="cost-value" :class="marginClass">
						${{ formatNumber(margin) }} ({{ marginPercent }}%)
					</span>
				</div>
			</div>
		</div>

		<!-- Alerta de margen negativo -->
		<div v-if="margin < 0" class="margin-warning">
			<i class="fa-solid fa-triangle-exclamation me-2"></i>
			El costo real supera el precio cotizado
		</div>

		<!-- Modal Mano de Obra -->
		<div v-if="showLaborModal" class="modal-overlay" @click.self="showLaborModal = false">
			<div class="modal-content">
				<h5>Editar Mano de Obra</h5>
				<div class="mb-3">
					<label class="form-label">Costo de Mano de Obra ($)</label>
					<input
						v-model.number="editLaborCost"
						type="number"
						class="form-control"
						min="0"
						step="100"
					/>
				</div>
				<div class="d-flex gap-2 justify-content-end">
					<button class="btn btn-secondary" @click="showLaborModal = false">Cancelar</button>
					<button class="btn btn-primary" @click="saveLaborCost" :disabled="saving">
						{{ saving ? 'Guardando...' : 'Guardar' }}
					</button>
				</div>
			</div>
		</div>

		<!-- Modal Otros Gastos -->
		<div v-if="showOtherModal" class="modal-overlay" @click.self="showOtherModal = false">
			<div class="modal-content">
				<h5>Editar Otros Gastos</h5>
				<div class="mb-3">
					<label class="form-label">Otros Gastos ($)</label>
					<input
						v-model.number="editOtherCosts"
						type="number"
						class="form-control"
						min="0"
						step="100"
					/>
				</div>
				<div class="mb-3">
					<label class="form-label">Descripción (opcional)</label>
					<textarea
						v-model="editOtherNotes"
						class="form-control"
						rows="2"
						placeholder="Ej: Transporte, insumos especiales..."
					></textarea>
				</div>
				<div class="d-flex gap-2 justify-content-end">
					<button class="btn btn-secondary" @click="showOtherModal = false">Cancelar</button>
					<button class="btn btn-primary" @click="saveOtherCosts" :disabled="saving">
						{{ saving ? 'Guardando...' : 'Guardar' }}
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { api } from '@/services/api'

const props = defineProps({
	repairId: { type: [Number, String], required: true },
	repair: { type: Object, default: () => ({}) },
	materialsCost: { type: Number, default: 0 },
	componentsCount: { type: Number, default: 0 },
	isReadOnly: { type: Boolean, default: false }
})

const emit = defineEmits(['updated'])

// State
const showLaborModal = ref(false)
const showOtherModal = ref(false)
const editLaborCost = ref(0)
const editOtherCosts = ref(0)
const editOtherNotes = ref('')
const saving = ref(false)

// Computed from repair data
const laborCost = computed(() => props.repair?.labor_cost || 0)
const otherCosts = computed(() => props.repair?.other_costs || 0)
const quotedPrice = computed(() => props.repair?.quoted_price || 0)

const totalCost = computed(() => {
	return laborCost.value + props.materialsCost + otherCosts.value
})

const margin = computed(() => {
	if (!quotedPrice.value) return 0
	return quotedPrice.value - totalCost.value
})

const marginPercent = computed(() => {
	if (!quotedPrice.value || quotedPrice.value === 0) return 0
	return Math.round((margin.value / quotedPrice.value) * 100)
})

const marginClass = computed(() => {
	if (margin.value < 0) return 'negative'
	if (margin.value > 0) return 'positive'
	return 'neutral'
})

const marginIcon = computed(() => {
	if (margin.value < 0) return 'fa-solid fa-arrow-trend-down'
	if (margin.value > 0) return 'fa-solid fa-arrow-trend-up'
	return 'fa-solid fa-minus'
})

// Methods
const formatNumber = (num) => {
	return new Intl.NumberFormat('es-CL').format(num || 0)
}

const saveLaborCost = async () => {
	saving.value = true
	try {
		await api.put(`/repairs/${props.repairId}`, {
			labor_cost: editLaborCost.value
		})
		emit('updated')
		showLaborModal.value = false
	} catch (error) {
		console.error('Error guardando mano de obra:', error)
		alert(error.response?.data?.detail || 'Error al guardar')
	} finally {
		saving.value = false
	}
}

const saveOtherCosts = async () => {
	saving.value = true
	try {
		await api.put(`/repairs/${props.repairId}`, {
			other_costs: editOtherCosts.value,
			other_costs_notes: editOtherNotes.value || null
		})
		emit('updated')
		showOtherModal.value = false
	} catch (error) {
		console.error('Error guardando otros gastos:', error)
		alert(error.response?.data?.detail || 'Error al guardar')
	} finally {
		saving.value = false
	}
}

// Watch para inicializar valores de edición
watch(() => props.repair, (repair) => {
	if (repair) {
		editLaborCost.value = repair.labor_cost || 0
		editOtherCosts.value = repair.other_costs || 0
		editOtherNotes.value = repair.other_costs_notes || ''
	}
}, { immediate: true })
</script>

<style scoped lang="scss">
@use "@/scss/_theming.scss" as *;

.cost-summary {
	background: $vintage-beige;
	border-radius: 12px;
	padding: 1.25rem;
	box-shadow: 0 2px 8px rgba($black, 0.08);
}

.section-header {
	margin-bottom: 1rem;
}

.section-title {
	color: $brand-text;
	font-weight: 600;
	margin: 0;
}

.cost-grid {
	display: flex;
	flex-direction: column;
	gap: 0.75rem;
}

.cost-item {
	display: flex;
	align-items: center;
	gap: 0.75rem;
	padding: 0.75rem;
	background: $white;
	border-radius: 8px;
	transition: all 0.2s ease;

	&:hover {
		box-shadow: 0 2px 8px rgba($black, 0.1);
	}
}

.cost-icon {
	width: 40px;
	height: 40px;
	border-radius: 10px;
	display: flex;
	align-items: center;
	justify-content: center;
	background: rgba($brand-primary, 0.1);
	color: $brand-primary;
	font-size: 1.1em;

	&.materials {
		background: rgba($status-info-legacy, 0.1);
		color: $status-info-legacy;
	}

	&.other {
		background: rgba($status-secondary-legacy, 0.1);
		color: $status-secondary-legacy;
	}

	&.total {
		background: $brand-primary;
		color: $white;
	}

	&.quoted {
		background: rgba($status-teal-legacy, 0.1);
		color: $status-teal-legacy;
	}

	&.positive {
		background: rgba($status-success-legacy, 0.1);
		color: $status-success-legacy;
	}

	&.negative {
		background: rgba($status-danger-legacy, 0.1);
		color: $status-danger-legacy;
	}

	&.neutral {
		background: rgba($status-secondary-legacy, 0.1);
		color: $status-secondary-legacy;
	}
}

.cost-details {
	flex: 1;
	display: flex;
	flex-direction: column;
}

.cost-label {
	font-size: 0.85em;
	color: $text-muted;
}

.cost-value {
	font-weight: 600;
	font-size: 1.1em;
	color: $brand-text;

	&.total-value {
		color: $brand-primary;
		font-size: 1.25em;
	}

	&.positive {
		color: $status-success-legacy;
	}

	&.negative {
		color: $status-danger-legacy;
	}
}

.cost-note {
	font-size: 0.8em;
	color: $text-muted;
	background: $light-2;
	padding: 0.25rem 0.5rem;
	border-radius: 4px;
}

.edit-btn {
	opacity: 0.6;
	transition: opacity 0.2s;

	&:hover {
		opacity: 1;
	}
}

.cost-divider {
	height: 1px;
	background: linear-gradient(90deg, transparent, rgba($black, 0.1), transparent);
	margin: 0.5rem 0;
}

.total-row {
	background: lighten($brand-primary, 42%);
	border: 2px solid rgba($brand-primary, 0.2);
}

.quoted-row {
	background: rgba($status-teal-legacy, 0.05);
}

.margin-row {
	background: rgba($light-1, 0.8);
}

.margin-warning {
	margin-top: 1rem;
	padding: 0.75rem;
	background: rgba($status-danger-legacy, 0.1);
	border: 1px solid rgba($status-danger-legacy, 0.3);
	border-radius: 8px;
	color: $status-danger-legacy;
	font-weight: 500;
	text-align: center;
}

.modal-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba($black, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
}

.modal-content {
	background: $white;
	padding: 1.5rem;
	border-radius: 12px;
	max-width: 400px;
	width: 90%;
	box-shadow: 0 10px 40px rgba($black, 0.2);

	h5 {
		margin-bottom: 1rem;
		color: $brand-text;
	}
}
</style>
