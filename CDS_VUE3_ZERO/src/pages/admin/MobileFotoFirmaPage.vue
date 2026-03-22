<template>
  <div class="mff-page">
    <!-- Buscador de OT -->
    <div class="mff-search-wrap">
      <input
        v-model="search"
        type="search"
        class="mff-search"
        placeholder="Buscar OT por codigo o cliente..."
        inputmode="search"
        autocomplete="off"
      />
    </div>

    <!-- Estado de carga / error -->
    <p v-if="loading" class="mff-state">Cargando OTs activas...</p>
    <p v-else-if="error" class="mff-state mff-state--error">{{ error }}</p>
    <p v-else-if="filtered.length === 0" class="mff-state">Sin OTs activas.</p>

    <!-- Lista de OTs -->
    <ul v-else class="mff-list">
      <li
        v-for="ot in filtered"
        :key="ot.id"
        class="mff-item"
        :class="{ 'mff-item--selected': selected?.id === ot.id }"
        @click="selectOt(ot)"
      >
        <div class="mff-item-head">
          <span class="mff-code">{{ ot.repair_code || ot.repair_number }}</span>
          <span class="mff-status" :class="`mff-status--${ot.status}`">{{ ot.status }}</span>
        </div>
        <div class="mff-item-body">
          <strong>{{ ot.client_name || ot.client?.name || '—' }}</strong>
          <span>{{ ot.device_brand || ot.device?.brand_other || '' }} {{ ot.device_model || ot.device?.model || '' }}</span>
        </div>
      </li>
    </ul>

    <!-- Panel de accion para la OT seleccionada -->
    <div v-if="selected" class="mff-action-panel">
      <div class="mff-action-head">
        <strong>{{ selected.repair_code || selected.repair_number }}</strong>
        <router-link :to="`/admin/repairs/${selected.id}`" class="mff-link-full">
          Ver OT completa
        </router-link>
      </div>

      <!-- Captura de foto directa -->
      <label class="mff-camera-btn">
        <input
          type="file"
          accept="image/*"
          capture="environment"
          class="mff-file-input"
          @change="onFileSelected"
        />
        <i class="fa-solid fa-camera"></i>
        <span>{{ uploading ? 'Subiendo...' : 'Tomar foto' }}</span>
      </label>

      <!-- Previa y tipo -->
      <div v-if="pendingFile" class="mff-preview-wrap">
        <img :src="previewUrl" class="mff-preview-img" alt="Vista previa" />
        <select v-model="photoType" class="mff-select">
          <option value="general">General</option>
          <option value="before">Antes</option>
          <option value="after">Despues</option>
          <option value="damage">Daño</option>
          <option value="component">Componente</option>
        </select>
        <button
          class="mff-upload-btn"
          :disabled="uploading"
          @click="uploadPhoto"
        >
          <i class="fa-solid fa-cloud-arrow-up"></i>
          {{ uploading ? 'Subiendo...' : 'Subir foto' }}
        </button>
        <button class="mff-cancel-btn" :disabled="uploading" @click="clearPending">
          Cancelar
        </button>
      </div>

      <!-- Firma digital -->
      <button class="mff-sig-toggle" @click="toggleSig">
        <i class="fa-solid fa-pen-nib"></i>
        <span>{{ showSig ? 'Ocultar firma' : 'Agregar firma del cliente' }}</span>
      </button>

      <div v-if="showSig" class="mff-sig-wrap">
        <p class="mff-sig-hint">El cliente firma con el dedo aquí</p>
        <canvas
          ref="sigCanvas"
          class="mff-sig-canvas"
          width="600"
          height="200"
          @touchstart.prevent="sigStart"
          @touchmove.prevent="sigMove"
          @touchend="sigEnd"
          @mousedown="sigStart"
          @mousemove="sigMove"
          @mouseup="sigEnd"
          @mouseleave="sigEnd"
        ></canvas>
        <div class="mff-sig-actions">
          <button class="mff-cancel-btn" @click="clearSig">
            <i class="fa-solid fa-eraser"></i> Limpiar
          </button>
          <button
            class="mff-upload-btn"
            :disabled="!sigHasContent || uploading"
            @click="uploadSig"
          >
            <i class="fa-solid fa-check"></i>
            {{ uploading ? 'Guardando...' : 'Guardar firma' }}
          </button>
        </div>
      </div>

      <p v-if="uploadMsg" class="mff-upload-msg" :class="{ 'mff-upload-msg--ok': uploadOk }">
        {{ uploadMsg }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import api from '@/services/api'

const repairs = ref([])
const loading = ref(false)
const error = ref('')
const search = ref('')

const selected = ref(null)
const pendingFile = ref(null)
const previewUrl = ref('')
const photoType = ref('general')
const uploading = ref(false)
const uploadMsg = ref('')
const uploadOk = ref(false)

// ── Firma ──
const sigCanvas = ref(null)
const showSig = ref(false)
const sigDrawing = ref(false)
const sigHasContent = ref(false)

watch(showSig, async (val) => {
  if (val) {
    await nextTick()
    initCanvas()
  }
})

function initCanvas() {
  const ctx = sigCanvas.value?.getContext('2d')
  if (!ctx) return
  ctx.strokeStyle = '#1a1a1a'
  ctx.lineWidth = 2.5
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
}

function getSigPos(e) {
  const rect = sigCanvas.value.getBoundingClientRect()
  const src = e.touches?.[0] ?? e
  return {
    x: (src.clientX - rect.left) * (sigCanvas.value.width / rect.width),
    y: (src.clientY - rect.top) * (sigCanvas.value.height / rect.height),
  }
}

function sigStart(e) {
  sigDrawing.value = true
  const ctx = sigCanvas.value.getContext('2d')
  const { x, y } = getSigPos(e)
  ctx.beginPath()
  ctx.moveTo(x, y)
}

function sigMove(e) {
  if (!sigDrawing.value) return
  const ctx = sigCanvas.value.getContext('2d')
  const { x, y } = getSigPos(e)
  ctx.lineTo(x, y)
  ctx.stroke()
  sigHasContent.value = true
}

function sigEnd() {
  sigDrawing.value = false
}

function clearSig() {
  const ctx = sigCanvas.value?.getContext('2d')
  if (!ctx) return
  ctx.clearRect(0, 0, sigCanvas.value.width, sigCanvas.value.height)
  sigHasContent.value = false
}

function toggleSig() {
  showSig.value = !showSig.value
  if (!showSig.value) clearSig()
}

async function uploadSig() {
  if (!sigCanvas.value || !selected.value) return
  sigCanvas.value.toBlob(async (blob) => {
    if (!blob) return
    uploading.value = true
    uploadMsg.value = ''
    try {
      const form = new FormData()
      form.append('file', blob, 'firma.png')
      form.append('photo_type', 'signature')
      form.append('repair_id', String(selected.value.id))
      await api.post(`/uploads/repair-photo/${selected.value.id}`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      uploadOk.value = true
      uploadMsg.value = 'Firma guardada correctamente.'
      showSig.value = false
      clearSig()
    } catch (e) {
      uploadOk.value = false
      uploadMsg.value = e?.response?.data?.detail || 'Error al guardar la firma.'
    } finally {
      uploading.value = false
    }
  }, 'image/png')
}

const filtered = computed(() => {
  if (!search.value.trim()) return repairs.value
  const q = search.value.toLowerCase()
  return repairs.value.filter(ot => {
    const code = String(ot.repair_code || ot.repair_number || '').toLowerCase()
    const client = String(ot.client_name || ot.client?.name || '').toLowerCase()
    return code.includes(q) || client.includes(q)
  })
})

async function loadRepairs() {
  loading.value = true
  error.value = ''
  try {
    const data = await api.get('/repairs/')
    repairs.value = data ?? []
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Error al cargar OTs'
  } finally {
    loading.value = false
  }
}

function selectOt(ot) {
  selected.value = selected.value?.id === ot.id ? null : ot
  clearPending()
}

function onFileSelected(e) {
  const file = e.target.files?.[0]
  if (!file) return
  pendingFile.value = file
  previewUrl.value = URL.createObjectURL(file)
  uploadMsg.value = ''
}

function clearPending() {
  pendingFile.value = null
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = ''
  }
  uploadMsg.value = ''
  photoType.value = 'general'
}

async function uploadPhoto() {
  if (!pendingFile.value || !selected.value) return
  uploading.value = true
  uploadMsg.value = ''
  try {
    const form = new FormData()
    form.append('file', pendingFile.value)
    form.append('photo_type', photoType.value)
    form.append('repair_id', String(selected.value.id))
    await api.post(`/uploads/repair-photo/${selected.value.id}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    uploadOk.value = true
    uploadMsg.value = 'Foto subida correctamente.'
    clearPending()
  } catch (e) {
    uploadOk.value = false
    uploadMsg.value = e?.response?.data?.detail || 'Error al subir la foto.'
  } finally {
    uploading.value = false
  }
}

onMounted(loadRepairs)
</script>

<style scoped>
.mff-page {
  padding: 1rem;
  max-width: 640px;
  margin: 0 auto;
}

/* Search */
.mff-search-wrap {
  margin-bottom: 1rem;
}
.mff-search {
  width: 100%;
  height: 3rem;
  padding: 0 1rem;
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-md);
  font-size: 1rem;
  color: var(--cds-text-normal);
  background: var(--cds-white);
}
.mff-search:focus {
  outline: none;
  border-color: var(--cds-primary);
}

/* State messages */
.mff-state {
  text-align: center;
  padding: 2rem;
  color: var(--cds-text-muted);
  font-size: 0.95rem;
}
.mff-state--error { color: var(--cds-danger, #dc2626); }

/* OT list */
.mff-list {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mff-item {
  padding: 0.85rem 1rem;
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-md);
  background: var(--cds-white);
  cursor: pointer;
  transition: border-color 0.15s;
}
.mff-item:active,
.mff-item--selected {
  border-color: var(--cds-primary);
  background: rgba(236, 107, 0, 0.04);
}

.mff-item-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}
.mff-code {
  font-weight: 700;
  font-size: 0.9rem;
  font-family: var(--cds-font-family-mono, monospace);
  color: var(--cds-primary);
}
.mff-status {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: var(--cds-radius-sm);
  background: var(--cds-light-1);
  color: var(--cds-text-muted);
  text-transform: uppercase;
}
.mff-status--en_progreso,
.mff-status--in_progress { background: #dbeafe; color: #1e40af; }
.mff-status--pendiente,
.mff-status--pending { background: #fef3c7; color: #92400e; }
.mff-status--listo,
.mff-status--done { background: #dcfce7; color: #166534; }

.mff-item-body {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  font-size: 0.875rem;
  color: var(--cds-text-muted);
}
.mff-item-body strong {
  color: var(--cds-text-normal);
  font-weight: 600;
}

/* Action panel */
.mff-action-panel {
  position: sticky;
  bottom: 0;
  background: var(--cds-white);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-lg) var(--cds-radius-lg) 0 0;
  padding: 1rem;
  box-shadow: 0 -4px 20px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.mff-action-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.mff-action-head strong {
  font-family: var(--cds-font-family-mono, monospace);
  font-size: 0.9rem;
  color: var(--cds-text-normal);
}
.mff-link-full {
  font-size: 0.85rem;
  color: var(--cds-primary);
  text-decoration: none;
  font-weight: 600;
}

/* Camera button */
.mff-camera-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  height: 3.5rem;
  background: var(--cds-dark);
  color: var(--cds-white);
  border-radius: var(--cds-radius-md);
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
}
.mff-camera-btn i { font-size: 1.4rem; }
.mff-file-input {
  display: none;
}

/* Preview */
.mff-preview-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.mff-preview-img {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: var(--cds-radius-md);
}
.mff-select {
  height: 2.75rem;
  padding: 0 0.75rem;
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-md);
  font-size: 1rem;
  color: var(--cds-text-normal);
  background: var(--cds-white);
}
.mff-upload-btn {
  height: 3rem;
  background: var(--cds-primary);
  color: var(--cds-white);
  border: none;
  border-radius: var(--cds-radius-md);
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}
.mff-upload-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.mff-cancel-btn {
  height: 2.75rem;
  background: none;
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-md);
  font-size: 0.9rem;
  color: var(--cds-text-muted);
  cursor: pointer;
}

.mff-upload-msg {
  font-size: 0.875rem;
  color: var(--cds-danger, #dc2626);
  text-align: center;
}
.mff-upload-msg--ok { color: #166534; }

/* Firma */
.mff-sig-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  height: 3rem;
  background: var(--cds-surface-2);
  color: var(--cds-text-normal);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-md);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
}
.mff-sig-toggle i { font-size: 1.1rem; color: var(--cds-primary); }

.mff-sig-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mff-sig-hint {
  margin: 0;
  font-size: 0.8rem;
  color: var(--cds-text-muted);
  text-align: center;
}

.mff-sig-canvas {
  width: 100%;
  height: 160px;
  border: 2px dashed var(--cds-border-card);
  border-radius: var(--cds-radius-md);
  background: var(--cds-white);
  touch-action: none;
  cursor: crosshair;
  display: block;
}

.mff-sig-actions {
  display: flex;
  gap: 0.5rem;
}
.mff-sig-actions .mff-cancel-btn { flex: 1; }
.mff-sig-actions .mff-upload-btn { flex: 2; }
</style>
