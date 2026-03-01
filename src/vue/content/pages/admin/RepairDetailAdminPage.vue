<template>
	<AdminLayout
		title="Detalle de Reparación"
		:subtitle="repair?.repair_number || ''"
		:context="contextHeader"
	>
		<!-- Loading -->
		<div v-if="loading" class="text-center py-5">
			<div class="spinner-border text-primary" role="status">
				<span class="visually-hidden">Cargando...</span>
			</div>
		</div>

		<div v-else-if="repair" class="repair-detail-admin">
			<!-- Sección Superior: Estado y Costos -->
			<div class="row mb-4">
				<div class="col-lg-8">
					<!-- Estado de la Reparación -->
					<RepairStatusChanger
						:repair-id="repairId"
						:current-status-id="repair.status_id"
						@status-changed="onStatusChanged"
					/>
				</div>
				<div class="col-lg-4 mt-3 mt-lg-0">
					<!-- Resumen de Costos -->
					<RepairCostSummary
						:repair-id="repairId"
						:repair="repair"
						:materials-cost="totalMaterialsCost"
						:components-count="componentsCount"
						:is-read-only="isTerminalStatus"
						@updated="loadRepair"
					/>
				</div>
			</div>

			<!-- Información General -->
			<div class="detail-card mb-4">
				<h5 class="card-title"><i class="fa-solid fa-info-circle me-2"></i>Información General</h5>
				<div class="row">
					<div class="col-md-4">
						<p><strong>Número:</strong> {{ repair.repair_code || repair.repair_number }}</p>
						<p><strong>Prioridad:</strong>
							<span class="badge" :class="getPriorityBadge(repair.priority)">
								{{ getPriorityLabel(repair.priority) }}
							</span>
						</p>
						<p><strong>Cliente:</strong> {{ repair.client?.name || '—' }}</p>
					</div>
					<div class="col-md-4">
						<p><strong>Modelo:</strong> {{ repair.device?.model || '—' }}</p>
						<p><strong>Serial:</strong> {{ repair.device?.serial_number || '—' }}</p>
					</div>
					<div class="col-md-4">
						<p><strong>Problema:</strong> {{ repair.problem_reported || '—' }}</p>
						<p><strong>Diagnóstico:</strong> {{ repair.diagnosis || '—' }}</p>
						<p><strong>Trabajo:</strong> {{ repair.work_performed || '—' }}</p>
					</div>
				</div>
			</div>

			<!-- Firmas -->
			<div class="detail-card mb-4">
				<div class="d-flex justify-content-between align-items-center mb-2">
					<h5 class="card-title mb-0"><i class="fa-solid fa-signature me-2"></i>Firmas</h5>
					<div class="d-flex gap-2">
						<button class="btn btn-sm btn-outline-primary" data-testid="signature-request-ingreso" @click="requestSignature('ingreso')">
							Solicitar firma ingreso
						</button>
						<button class="btn btn-sm btn-outline-primary" data-testid="signature-request-retiro" @click="requestSignature('retiro')">
							Solicitar firma retiro
						</button>
					</div>
				</div>
				<div v-if="signatureLink" class="alert alert-info">
					<strong>Link firma:</strong>
					<input class="form-control mt-2" data-testid="signature-link" :value="signatureLink" readonly />
				</div>
				<div class="row">
					<div class="col-md-6">
						<p><strong>Firma ingreso:</strong> {{ repair.signature_ingreso_path ? 'OK' : 'Pendiente' }}</p>
					</div>
					<div class="col-md-6">
						<p><strong>Firma retiro:</strong> {{ repair.signature_retiro_path ? 'OK' : 'Pendiente' }}</p>
					</div>
				</div>
			</div>

			<!-- Fotos desde cliente -->
			<div class="detail-card mb-4">
				<div class="d-flex justify-content-between align-items-center mb-2">
					<h5 class="card-title mb-0"><i class="fa-solid fa-image me-2"></i>Fotos cliente</h5>
					<button class="btn btn-sm btn-outline-primary" data-testid="photo-request" @click="requestPhotoUpload">
						Solicitar foto
					</button>
				</div>
				<div v-if="photoUploadLink" class="alert alert-info">
					<strong>Link foto:</strong>
					<input class="form-control mt-2" data-testid="photo-upload-link" :value="photoUploadLink" readonly />
				</div>
			</div>

			<!-- Materiales Utilizados -->
			<div class="mb-4">
				<RepairComponentsManager
					ref="componentsManagerRef"
					:repair-id="repairId"
					:is-read-only="isTerminalStatus"
					@update:total-cost="onMaterialsCostUpdate"
					@components-changed="onComponentsChanged"
				/>
			</div>

			<!-- Fotos -->
			<div class="detail-card mb-4">
				<div class="d-flex justify-content-between align-items-center mb-3">
					<h5 class="card-title mb-0"><i class="fa-solid fa-camera me-2"></i>Fotos</h5>
					<button class="btn btn-sm btn-primary" @click="showPhotoUpload = !showPhotoUpload">
						<i class="fa-solid fa-plus me-1"></i> Agregar Foto
					</button>
				</div>

				<!-- Upload Form -->
				<div v-if="showPhotoUpload" class="upload-form mb-3 p-3 border rounded">
					<div class="mb-2">
						<label class="form-label">Archivo de imagen</label>
						<input type="file" class="form-control" accept="image/*" @change="onFileSelected" />
					</div>
					<div class="mb-2">
						<label class="form-label">Descripción (opcional)</label>
						<input v-model="newPhotoCaption" type="text" class="form-control" placeholder="Ej: Daño en circuito" />
					</div>
					<div class="mb-2">
						<label class="form-label">Tipo</label>
						<select v-model="newPhotoType" class="form-select">
							<option value="general">General</option>
							<option value="before">Antes</option>
							<option value="after">Después</option>
							<option value="damage">Daño</option>
							<option value="component">Componente</option>
						</select>
					</div>
					<button class="btn btn-success" :disabled="!selectedFile || uploading" @click="uploadPhoto">
						<i class="fa-solid fa-upload me-1"></i>
						{{ uploading ? 'Subiendo...' : 'Subir Foto' }}
					</button>
					<button class="btn btn-outline-secondary ms-2" @click="showPhotoUpload = false">Cancelar</button>
				</div>

				<!-- Photos Grid -->
				<div v-if="photos.length > 0" class="photos-grid">
					<div v-for="photo in photos" :key="photo.id" class="photo-item">
						<img :src="photo.resolved_photo_url" :alt="photo.caption || 'Foto'" />
						<div class="photo-info">
							<span class="badge bg-secondary">{{ photo.photo_type }}</span>
							<small v-if="photo.caption">{{ photo.caption }}</small>
						</div>
					</div>
				</div>
				<p v-else class="text-muted">Sin fotos registradas.</p>
			</div>

			<!-- Notas -->
			<div class="detail-card mb-4">
				<div class="d-flex justify-content-between align-items-center mb-3">
					<h5 class="card-title mb-0"><i class="fa-solid fa-sticky-note me-2"></i>Notas</h5>
					<button class="btn btn-sm btn-primary" @click="showNoteForm = !showNoteForm">
						<i class="fa-solid fa-plus me-1"></i> Agregar Nota
					</button>
				</div>

				<!-- Note Form -->
				<div v-if="showNoteForm" class="note-form mb-3 p-3 border rounded">
					<div class="mb-2">
						<label class="form-label">Nota</label>
						<textarea v-model="newNote" class="form-control" rows="3" placeholder="Escribe una nota técnica o comentario..."></textarea>
					</div>
					<div class="mb-2">
						<label class="form-label">Tipo</label>
						<select v-model="newNoteType" class="form-select">
							<option value="internal">Interna (solo admin)</option>
							<option value="public">Pública (visible para cliente)</option>
							<option value="technical">Técnica</option>
						</select>
					</div>
					<button class="btn btn-success" :disabled="!newNote.trim() || savingNote" @click="addNote">
						<i class="fa-solid fa-save me-1"></i>
						{{ savingNote ? 'Guardando...' : 'Guardar Nota' }}
					</button>
					<button class="btn btn-outline-secondary ms-2" @click="showNoteForm = false">Cancelar</button>
				</div>

				<!-- Notes List -->
				<div v-if="notes.length > 0" class="notes-list">
					<div v-for="note in notes" :key="note.id" class="note-item">
						<div class="note-header">
							<span class="badge" :class="getNoteTypeBadge(note.note_type)">{{ note.note_type }}</span>
							<small class="text-muted">{{ formatDate(note.created_at) }}</small>
						</div>
						<p class="note-text">{{ note.note }}</p>
					</div>
				</div>
				<p v-else class="text-muted">Sin notas registradas.</p>
			</div>

			<!-- Acciones -->
			<div class="d-flex gap-2">
				<button class="btn btn-outline-primary" @click="notifyClient">
					<i class="fa-solid fa-paper-plane me-1"></i> Enviar al cliente
				</button>
				<button
					class="btn btn-outline-dark"
					:disabled="downloadingClosurePdf"
					@click="downloadClosurePdf"
				>
					<i class="fa-solid fa-file-pdf me-1"></i>
					{{ downloadingClosurePdf ? 'Generando PDF...' : 'Descargar Cierre OT' }}
				</button>
				<router-link
					:to="{ name: 'admin-purchase-requests', query: { repair_id: repairId } }"
					class="btn btn-outline-info"
				>
					<i class="fa-solid fa-cart-shopping me-1"></i> Compras OT
				</router-link>
				<button
					class="btn btn-outline-warning"
					:disabled="isArchived"
					@click="archiveRepair"
				>
					<i class="fa-solid fa-box-archive me-1"></i>
					{{ isArchived ? 'Archivado' : 'Archivar OT' }}
				</button>
				<router-link to="/admin/repairs" class="btn btn-outline-secondary">
					<i class="fa-solid fa-arrow-left me-1"></i> Volver
				</router-link>
			</div>
		</div>

		<!-- Not found -->
		<div v-else class="text-center py-5 text-muted">
			<i class="fa-solid fa-exclamation-triangle fa-3x mb-3"></i>
			<p>Reparación no encontrada</p>
		</div>
	</AdminLayout>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/services/api'
import { hydrateRepairPhotos, revokeHydratedRepairPhotos } from '@/services/secureMedia'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'
import RepairStatusChanger from '@/vue/components/admin/repair/RepairStatusChanger.vue'
import RepairComponentsManager from '@/vue/components/admin/repair/RepairComponentsManager.vue'
import RepairCostSummary from '@/vue/components/admin/repair/RepairCostSummary.vue'

const route = useRoute()
const repairId = route.params.id

const repair = ref(null)
const photos = ref([])
const notes = ref([])
const loading = ref(true)

// Components manager ref
const componentsManagerRef = ref(null)
const totalMaterialsCost = ref(0)
const componentsCount = ref(0)

// Estado terminal (no permite más cambios)
const isTerminalStatus = computed(() => {
	const statusId = repair.value?.status_id
	return statusId === 9 // Archivado
})
const isArchived = computed(() => Boolean(repair.value?.archived_at))
const contextHeader = computed(() => {
	if (!repair.value) return null
	return {
		clientName: repair.value.client?.name,
		clientCode: repair.value.client?.client_code,
		instrument: repair.value.device?.model,
		otCode: repair.value.repair_code || repair.value.repair_number
	}
})

// Photo upload state
const showPhotoUpload = ref(false)
const selectedFile = ref(null)
const newPhotoCaption = ref('')
const newPhotoType = ref('general')
const uploading = ref(false)

// Note state
const showNoteForm = ref(false)
const newNote = ref('')
const newNoteType = ref('internal')
const savingNote = ref(false)
const signatureLink = ref('')
const photoUploadLink = ref('')
const downloadingClosurePdf = ref(false)

const archiveRepair = async () => {
	if (isArchived.value) return
	const ok = window.confirm('¿Archivar esta OT? Quedará en Archivo.')
	if (!ok) return
	try {
		const res = await api.post(`/repairs/${repairId}/archive`)
		repair.value = { ...repair.value, archived_at: res.data?.archived_at || new Date().toISOString() }
	} catch (e) {
		window.alert('No se pudo archivar la OT.')
	}
}

const notifyClient = async () => {
	try {
		await api.post(`/repairs/${repairId}/notify`)
		window.alert('Enviado al cliente.')
	} catch (e) {
		window.alert(e?.response?.data?.detail || 'No se pudo enviar.')
	}
}

const sanitizeFilePart = (value) => {
	const text = String(value || '').trim()
	if (!text) return 'OT'
	return text.replace(/[^a-zA-Z0-9._-]+/g, '_')
}

const downloadClosurePdf = async () => {
	downloadingClosurePdf.value = true
	try {
		const response = await api.get(`/repairs/${repairId}/closure-pdf`, {
			responseType: 'blob'
		})
		const blob = new Blob([response.data], { type: 'application/pdf' })
		const blobUrl = window.URL.createObjectURL(blob)
		const preferredCode = repair.value?.repair_code || repair.value?.repair_number || `OT_${repairId}`
		const link = document.createElement('a')
		link.href = blobUrl
		link.download = `CIERRE_${sanitizeFilePart(preferredCode)}.pdf`
		document.body.appendChild(link)
		link.click()
		document.body.removeChild(link)
		window.URL.revokeObjectURL(blobUrl)
	} catch (e) {
		window.alert(e?.response?.data?.detail || 'No se pudo generar el PDF de cierre OT.')
	} finally {
		downloadingClosurePdf.value = false
	}
}

const loadRepair = async () => {
	loading.value = true
	try {
		const [repairRes, photosRes, notesRes] = await Promise.all([
			api.get(`/repairs/${repairId}`).catch(() => null),
			api.get(`/repairs/${repairId}/photos`).catch(() => ({ data: [] })),
			api.get(`/repairs/${repairId}/notes`).catch(() => ({ data: [] }))
		])

		if (repairRes?.data) {
			repair.value = repairRes.data
		} else {
			// Try from list
			const listRes = await api.get('/repairs/')
			const found = (listRes.data || listRes || []).find(r => r.id == repairId)
			repair.value = found || null
		}

		const nextPhotos = await hydrateRepairPhotos(photosRes?.data || photosRes || [])
		revokeHydratedRepairPhotos(photos.value)
		photos.value = nextPhotos
		notes.value = notesRes?.data || notesRes || []
	} catch (error) {
		console.error('Error cargando reparación:', error)
	} finally {
		loading.value = false
	}
}

const requestSignature = async (type) => {
	signatureLink.value = ''
	try {
		const res = await api.post('/signatures/requests', {
			repair_id: Number(repairId),
			request_type: type,
			expires_minutes: 5
		})
		const token = res.data?.token || res.token
		if (token) {
			signatureLink.value = `${window.location.origin}/signature/${token}`
		}
	} catch (error) {
		console.error('Error solicitando firma:', error)
	}
}

const requestPhotoUpload = async () => {
	photoUploadLink.value = ''
	try {
		const res = await api.post('/photo-requests/', null, {
			params: { repair_id: Number(repairId), photo_type: 'client', expires_minutes: 10 }
		})
		const token = res.data?.token || res.token
		if (token) {
			photoUploadLink.value = `${window.location.origin}/photo-upload/${token}`
		}
	} catch (error) {
		console.error('Error solicitando foto:', error)
	}
}

const onFileSelected = (e) => {
	selectedFile.value = e.target.files[0] || null
}

const uploadPhoto = async () => {
	if (!selectedFile.value) return
	uploading.value = true

	try {
		// 1. Upload file
		const formData = new FormData()
		formData.append('file', selectedFile.value)
		const uploadRes = await api.post('/uploads/images', formData, {
			headers: { 'Content-Type': 'multipart/form-data' }
		})
		const photoPath = uploadRes.data?.path || uploadRes?.path

		// 2. Register photo in repair
		await api.post(`/repairs/${repairId}/photos`, {
			photo_url: photoPath,
			photo_type: newPhotoType.value,
			caption: newPhotoCaption.value || null
		})

		// 3. Reload photos
		const photosRes = await api.get(`/repairs/${repairId}/photos`)
		const nextPhotos = await hydrateRepairPhotos(photosRes?.data || photosRes || [])
		revokeHydratedRepairPhotos(photos.value)
		photos.value = nextPhotos

		// Reset form
		selectedFile.value = null
		newPhotoCaption.value = ''
		newPhotoType.value = 'general'
		showPhotoUpload.value = false
	} catch (error) {
		console.error('Error subiendo foto:', error)
		alert('Error al subir la foto')
	} finally {
		uploading.value = false
	}
}

const addNote = async () => {
	if (!newNote.value.trim()) return
	savingNote.value = true

	try {
		await api.post(`/repairs/${repairId}/notes`, {
			note: newNote.value.trim(),
			note_type: newNoteType.value
		})

		// Reload notes
		const notesRes = await api.get(`/repairs/${repairId}/notes`)
		notes.value = notesRes?.data || notesRes || []

		// Reset form
		newNote.value = ''
		newNoteType.value = 'internal'
		showNoteForm.value = false
	} catch (error) {
		console.error('Error guardando nota:', error)
		alert('Error al guardar la nota')
	} finally {
		savingNote.value = false
	}
}

const getPriorityLabel = (p) => {
	const labels = { 1: 'Urgente', 2: 'Normal', 3: 'Baja' }
	return labels[p] || 'Normal'
}

const getPriorityBadge = (p) => {
	const badges = { 1: 'bg-danger', 2: 'bg-primary', 3: 'bg-secondary' }
	return badges[p] || 'bg-primary'
}

// Handlers para nuevos componentes
const onStatusChanged = async ({ newStatusId, repair: updatedRepair }) => {
	if (updatedRepair) {
		repair.value = updatedRepair
	} else {
		await loadRepair()
	}
}

const onMaterialsCostUpdate = (cost) => {
	totalMaterialsCost.value = cost
}

const onComponentsChanged = (components) => {
	componentsCount.value = components?.length || 0
}

const getNoteTypeBadge = (type) => {
	const badges = {
		internal: 'bg-secondary',
		public: 'bg-info',
		technical: 'bg-warning text-dark'
	}
	return badges[type] || 'bg-secondary'
}

const formatDate = (dateStr) => {
	if (!dateStr) return '—'
	return new Intl.DateTimeFormat('es-CL', {
		dateStyle: 'medium',
		timeStyle: 'short'
	}).format(new Date(dateStr))
}

onMounted(() => {
	loadRepair()
})
onBeforeUnmount(() => {
	revokeHydratedRepairPhotos(photos.value)
})
</script>

<style scoped lang="scss">
@import "@/scss/_theming.scss";

.detail-card {
	background: $vintage-beige;
	border-radius: 12px;
	padding: 1.25rem;
	box-shadow: 0 2px 8px rgba($color-black, 0.08);
}

.card-title {
	color: $brand-text;
	font-weight: 600;
	margin-bottom: 1rem;
}

.photos-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
	gap: 1rem;
}

.photo-item {
	border-radius: 8px;
	overflow: hidden;
	background: $color-white;
	box-shadow: 0 1px 4px rgba($color-black, 0.1);

	img {
		width: 100%;
		height: 120px;
		object-fit: cover;
	}

	.photo-info {
		padding: 0.5rem;
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}
}

.notes-list {
	display: flex;
	flex-direction: column;
	gap: 0.75rem;
}

.note-item {
	background: $color-white;
	border-radius: 8px;
	padding: 0.75rem 1rem;
	border-left: 3px solid $orange-pastel;

	.note-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}

	.note-text {
		margin: 0;
		color: $brand-text;
	}
}

.upload-form, .note-form {
	background: rgba($color-white, 0.5);
}
</style>
