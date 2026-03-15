<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Gestión de Medios</h1>
        <p>Subir y organizar imágenes en Cloudinary.</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" :disabled="loadingCatalog" @click="loadCatalog">
          {{ loadingCatalog ? 'Cargando...' : 'Actualizar catálogo' }}
        </button>
        <button class="btn-secondary" :disabled="importing" @click="importFromCloudinary">
          {{ importing ? `Importando... (${importProgress})` : 'Importar desde Cloudinary' }}
        </button>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section class="summary-grid">
      <article class="summary-card">
        <span>Total registradas</span>
        <strong>{{ images.length }}</strong>
      </article>
      <article class="summary-card">
        <span>Instrumentos</span>
        <strong>{{ countByFolder('instrumentos') }}</strong>
      </article>
      <article class="summary-card">
        <span>Inventario</span>
        <strong>{{ countByFolder('inventario') }}</strong>
      </article>
    </section>

    <!-- SUBIR IMÁGENES -->
    <section class="panel-card">
      <h2>Subir imágenes</h2>

      <div class="upload-controls">
        <label>
          <span>Destino</span>
          <select v-model="destination">
            <option value="uploads">General</option>
            <option value="instrumentos">Instrumentos</option>
            <option value="inventario">Inventario</option>
          </select>
        </label>
      </div>

      <div
        class="drop-zone"
        :class="{ 'drop-zone--active': isDragging }"
        @dragenter.prevent="isDragging = true"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="onDrop"
        @click="fileInput.click()"
      >
        <i class="fa-solid fa-cloud-arrow-up"></i>
        <p>Arrastrá imágenes aquí o hacé clic para seleccionar</p>
        <span>Podés seleccionar múltiples archivos o una carpeta completa</span>
        <input ref="fileInput" type="file" multiple accept="image/*" @change="onFileSelect" />
        <input ref="folderInput" type="file" multiple accept="image/*" webkitdirectory @change="onFileSelect" />
      </div>

      <div class="upload-extra-actions">
        <button class="btn-secondary" type="button" @click="folderInput.click()">
          <i class="fa-solid fa-folder-open"></i> Seleccionar carpeta
        </button>
      </div>

      <p v-if="uploadValidationError" class="upload-validation-error">{{ uploadValidationError }}</p>

      <div v-if="queue.length" class="queue-list">
        <div v-for="item in queue" :key="`${item.name}-${item.size}`" class="queue-item">
          <span class="queue-name">{{ item.name }}</span>
          <span class="queue-size">{{ formatBytes(item.size) }}</span>
          <span class="queue-status" :class="`status--${item.status}`">{{ statusLabel(item.status) }}</span>
        </div>
      </div>

      <div v-if="queue.length" class="panel-actions">
        <button class="btn-primary" :disabled="uploading" @click="uploadAll">
          {{ uploading ? `Subiendo ${uploadProgress}/${queue.length}...` : `Subir ${queue.length} imagen(es)` }}
        </button>
        <button class="btn-secondary" :disabled="uploading" @click="clearQueue">Limpiar</button>
      </div>
    </section>

    <!-- SLOTS DEL SITIO (bindings) -->
    <section class="panel-card">
      <div class="panel-head">
        <h2>Slots del sitio ({{ bindings.length }})</h2>
        <button class="btn-secondary" @click="toggleBindingForm">
          {{ showBindingForm ? 'Cancelar' : '+ Asignar imagen a slot' }}
        </button>
      </div>

      <p class="catalog-hint">
        Un slot es un lugar fijo del sitio (ej: <code>home.hero.bg</code>). Asignás una imagen y el sitio la muestra automáticamente sin tocar código.
      </p>

      <!-- Formulario nuevo/editar binding -->
      <div v-if="showBindingForm" class="binding-form">
        <div class="binding-form-fields">
          <label>
            <span>Slot (clave única)</span>
            <input
              v-model.trim="bindingForm.slot_key"
              type="text"
              placeholder="ej: home.hero.bg"
              :readonly="isEditingBinding"
              :style="isEditingBinding ? 'background: rgba(62,60,56,.06); cursor: not-allowed;' : ''"
            />
          </label>
          <label>
            <span>Nombre legible (opcional)</span>
            <input v-model.trim="bindingForm.label" type="text" placeholder="ej: Imagen de fondo del hero" />
          </label>
        </div>

        <div class="binding-picker">
          <span class="binding-picker-label">Elegir imagen del catálogo</span>
          <input v-model.trim="pickerSearch" type="search" placeholder="Buscar..." class="picker-search" />
          <div class="picker-grid">
            <figure
              v-for="img in pickerFiltered"
              :key="img.public_id"
              class="picker-tile"
              :class="{ 'picker-tile--selected': bindingForm.asset_id === img.id }"
              @click="bindingForm.asset_id = img.id"
            >
              <img :src="thumb(img.secure_url)" :alt="shortName(img.public_id)" loading="lazy" />
              <figcaption>{{ shortName(img.public_id) }}</figcaption>
            </figure>
          </div>
        </div>

        <div class="panel-actions">
          <button
            class="btn-primary"
            :disabled="!bindingForm.slot_key || !bindingForm.asset_id || savingBinding"
            @click="saveBinding"
          >
            {{ savingBinding ? 'Guardando...' : 'Guardar slot' }}
          </button>
        </div>
      </div>

      <!-- Lista de bindings actuales -->
      <p v-if="loadingBindings" class="catalog-hint">Cargando slots...</p>
      <p v-else-if="!bindings.length" class="catalog-hint">No hay slots asignados todavía.</p>

      <div v-else class="bindings-list">
        <div v-for="b in bindings" :key="b.slot_key" class="binding-row">
          <img v-if="b.asset?.secure_url" :src="thumb(b.asset.secure_url)" :alt="b.slot_key" class="binding-thumb" />
          <div class="binding-info">
            <span class="binding-slot">{{ b.slot_key }}</span>
            <span v-if="b.label" class="binding-label">{{ b.label }}</span>
            <span class="binding-name">{{ shortName(b.asset?.public_id) }}</span>
          </div>
          <div class="binding-actions">
            <button class="btn-icon" title="Editar" @click="editBinding(b)">✏️</button>
            <button class="btn-icon btn-icon--danger" title="Quitar" @click="deleteBinding(b.slot_key)">✕</button>
          </div>
        </div>
      </div>
    </section>

    <!-- CATÁLOGO -->
    <section class="panel-card">
      <div class="panel-head">
        <h2>Catálogo ({{ filtered.length }})</h2>
        <div class="catalog-filters">
          <input v-model.trim="search" type="search" placeholder="Buscar por nombre..." />
          <select v-model="folderFilter">
            <option value="">Todas las carpetas</option>
            <option value="instrumentos">Instrumentos</option>
            <option value="inventario">Inventario</option>
            <option value="general">General</option>
          </select>
        </div>
      </div>

      <p v-if="loadingCatalog" class="catalog-hint">Cargando catálogo...</p>
      <p v-else-if="!images.length" class="catalog-hint">No hay imágenes registradas todavía. Usá la sección "Subir imágenes" — cada imagen que subas quedará registrada aquí automáticamente.</p>

      <div v-else class="image-grid">
        <figure v-for="img in filtered" :key="img.public_id" class="image-tile">
          <img :src="thumb(img.secure_url)" :alt="shortName(img.public_id)" loading="lazy" />
          <figcaption>
            <span class="tile-name">{{ shortName(img.public_id) }}</span>
            <span class="tile-meta">{{ formatBytes(img.bytes) }}</span>
          </figcaption>
        </figure>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api.js'
import { uploadImageWithMeta } from '@/services/uploadService.js'

// ─── Catálogo (desde BD) ───────────────────────────────────────────────────
const images = ref([])
const loadingCatalog = ref(false)
const error = ref(null)
const search = ref('')
const folderFilter = ref('')

const filtered = computed(() => {
  let list = images.value
  if (folderFilter.value) {
    list = list.filter(img => img.folder?.includes(folderFilter.value) || img.public_id?.includes(folderFilter.value))
  }
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(img => img.public_id?.toLowerCase().includes(q))
  }
  return list
})

function countByFolder(folder) {
  return images.value.filter(img => img.folder?.includes(folder) || img.public_id?.includes(folder)).length
}

async function loadCatalog() {
  loadingCatalog.value = true
  error.value = null
  try {
    const { data } = await api.get('/media/assets')
    images.value = data || []
  } catch {
    error.value = 'Error al cargar el catálogo. Verificá que el backend esté corriendo.'
  } finally {
    loadingCatalog.value = false
  }
}

// ─── Importación masiva desde Cloudinary ──────────────────────────────────
const importing = ref(false)
const importProgress = ref('')

async function importFromCloudinary() {
  if (importing.value) return
  importing.value = true
  importProgress.value = 'conectando...'
  error.value = null
  try {
    const { data } = await api.post('/media/assets/import-from-cloudinary')
    importProgress.value = ''
    await loadCatalog()
    const { inserted = 0, updated = 0, total = 0 } = data
    alert(`Importación completa: ${total} imágenes procesadas (${inserted} nuevas, ${updated} actualizadas).`)
  } catch {
    error.value = 'Error al importar desde Cloudinary. Verificá que el backend tenga acceso a Cloudinary.'
  } finally {
    importing.value = false
    importProgress.value = ''
  }
}

// ─── Upload ────────────────────────────────────────────────────────────────
const destination = ref('uploads')
const isDragging = ref(false)
const queue = ref([])
const uploading = ref(false)
const uploadProgress = ref(0)
const fileInput = ref(null)
const folderInput = ref(null)
const uploadValidationError = ref('')
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10 MB

function onDrop(e) {
  isDragging.value = false
  const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'))
  addToQueue(files)
}

function onFileSelect(e) {
  const files = Array.from(e.target.files).filter(f => f.type.startsWith('image/'))
  addToQueue(files)
  e.target.value = ''
}

function addToQueue(files) {
  const rechazados = []
  for (const file of files) {
    if (file.size > MAX_FILE_SIZE) {
      rechazados.push(`${file.name}: supera 10 MB`)
      continue
    }
    const exists = queue.value.find(q => q.name === file.name && q.size === file.size)
    if (!exists) {
      queue.value.push({ file, name: file.name, size: file.size, status: 'pending' })
    }
  }
  uploadValidationError.value = rechazados.length ? rechazados.join(' · ') : ''
}

async function uploadAll() {
  if (uploading.value) return
  uploading.value = true
  uploadProgress.value = 0
  error.value = null
  try {
    for (const item of queue.value) {
      if (item.status === 'done') { uploadProgress.value++; continue }
      item.status = 'uploading'
      try {
        const meta = await uploadImageWithMeta(item.file, destination.value)
        if (meta?.secure_url) {
          // Registrar en BD
          await api.post('/media/assets', meta).catch(() => {})
          item.status = 'done'
        } else {
          item.status = 'error'
        }
      } catch {
        item.status = 'error'
      }
      uploadProgress.value++
    }
    await loadCatalog()
  } finally {
    uploading.value = false
  }
}

function clearQueue() {
  queue.value = queue.value.filter(i => i.status === 'uploading')
}

// ─── Bindings ──────────────────────────────────────────────────────────────
const bindings = ref([])
const loadingBindings = ref(false)
const showBindingForm = ref(false)
const savingBinding = ref(false)
const pickerSearch = ref('')
const isEditingBinding = ref(false)

const bindingForm = ref({ slot_key: '', label: '', asset_id: null })

const pickerFiltered = computed(() => {
  const q = pickerSearch.value.toLowerCase()
  const base = q
    ? images.value.filter(img => img.public_id?.toLowerCase().includes(q))
    : images.value
  const limited = base.slice(0, 40)
  const selectedId = bindingForm.value.asset_id
  if (!selectedId) return limited

  const selected = images.value.find(img => img.id === selectedId)
  if (!selected) return limited
  if (limited.some(img => img.id === selected.id)) return limited

  return [selected, ...limited.slice(0, 39)]
})

async function loadBindings() {
  loadingBindings.value = true
  try {
    const { data } = await api.get('/media/bindings')
    bindings.value = data || []
  } catch {
    error.value = 'Error al cargar los slots del sitio.'
  } finally {
    loadingBindings.value = false
  }
}

async function saveBinding() {
  if (!bindingForm.value.slot_key || !bindingForm.value.asset_id) return
  savingBinding.value = true
  try {
    await api.put(`/media/bindings/${bindingForm.value.slot_key}`, {
      asset_id: bindingForm.value.asset_id,
      label: bindingForm.value.label || null,
    })
    bindingForm.value = { slot_key: '', label: '', asset_id: null }
    showBindingForm.value = false
    isEditingBinding.value = false
    error.value = null
    await loadBindings()
  } catch {
    error.value = 'Error al guardar el slot.'
  } finally {
    savingBinding.value = false
  }
}

function toggleBindingForm() {
  showBindingForm.value = !showBindingForm.value
  if (!showBindingForm.value) {
    isEditingBinding.value = false
    bindingForm.value = { slot_key: '', label: '', asset_id: null }
    pickerSearch.value = ''
  }
}

function editBinding(b) {
  bindingForm.value = {
    slot_key: b.slot_key,
    label: b.label || '',
    asset_id: b.asset?.id || null,
  }
  isEditingBinding.value = true
  showBindingForm.value = true
}

async function deleteBinding(slotKey) {
  if (!confirm(`¿Quitar el slot "${slotKey}"?`)) return
  try {
    await api.delete(`/media/bindings/${slotKey}`)
    error.value = null
    await loadBindings()
  } catch {
    error.value = 'Error al quitar el slot.'
  }
}

// ─── Helpers ───────────────────────────────────────────────────────────────
function thumb(url) {
  if (!url) return ''
  return url.replace('/upload/', '/upload/w_200,c_limit,q_auto/')
}

function shortName(publicId) {
  return publicId?.split('/').pop() || publicId || ''
}

function formatBytes(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1048576).toFixed(1)} MB`
}

function statusLabel(status) {
  const map = { pending: 'En cola', uploading: 'Subiendo...', done: '✓ Listo', error: '✗ Error' }
  return map[status] || status
}

onMounted(() => {
  loadCatalog()
  loadBindings()
})
</script>

<style scoped>
.admin-page { padding: 1rem; display: grid; gap: 1rem; }
.admin-header, .summary-card, .panel-card { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); }
.admin-header { padding: .9rem; display: flex; flex-wrap: wrap; gap: .75rem; justify-content: space-between; align-items: center; }
.admin-header h1 { margin: 0; font-size: var(--cds-text-3xl); }
.admin-header p { margin: .3rem 0 0; color: var(--cds-text-muted); }
.admin-error { color: #c0392b; padding: .5rem .9rem; background: #fdf3f2; border-radius: .5rem; font-size: var(--cds-text-sm); }

.btn-primary, .btn-secondary { min-height: 44px; padding: .65rem .9rem; border-radius: .55rem; font-size: var(--cds-text-base); border: 1px solid transparent; cursor: pointer; font-weight: var(--cds-font-semibold); }
.btn-primary { border-color: var(--cds-primary); background: var(--cds-primary); color: var(--cds-white); }
.btn-secondary { border-color: color-mix(in srgb, var(--cds-light) 65%, white); background: var(--cds-white); color: var(--cds-text-normal); }
.btn-primary:disabled, .btn-secondary:disabled { opacity: .55; cursor: not-allowed; }
.header-actions { display: flex; gap: .5rem; flex-wrap: wrap; }

.summary-grid { display: grid; gap: .7rem; grid-template-columns: repeat(3, minmax(0, 1fr)); }
.summary-card { padding: .9rem; display: grid; gap: .25rem; }
.summary-card span { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.summary-card strong { font-size: var(--cds-text-2xl); font-weight: var(--cds-font-semibold); color: var(--cds-dark); }

.panel-card { padding: .9rem; display: grid; gap: .75rem; }
.panel-card h2 { margin: 0; font-size: var(--cds-text-xl); }
.panel-head { display: flex; flex-wrap: wrap; gap: .6rem; justify-content: space-between; align-items: center; }
.panel-actions { display: flex; gap: .5rem; flex-wrap: wrap; }

.upload-controls label { display: grid; gap: .3rem; font-size: var(--cds-text-sm); font-weight: var(--cds-font-semibold); color: var(--cds-dark); width: fit-content; }
.upload-controls select { min-height: 44px; border: 1.5px solid rgba(62,60,56,.25); border-radius: .5rem; padding: .5rem .75rem; font-size: var(--cds-text-base); background: var(--cds-white); color: var(--cds-dark); }

.drop-zone { border: 2px dashed color-mix(in srgb, var(--cds-primary) 40%, transparent); border-radius: .75rem; padding: 2rem 1rem; text-align: center; cursor: pointer; display: grid; gap: .4rem; justify-items: center; transition: background .15s; }
.drop-zone:hover, .drop-zone--active { background: color-mix(in srgb, var(--cds-primary) 6%, white); }
.drop-zone i { font-size: 2rem; color: var(--cds-primary); }
.drop-zone p { margin: 0; font-size: var(--cds-text-base); font-weight: var(--cds-font-semibold); color: var(--cds-dark); }
.drop-zone span { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.drop-zone input { display: none; }

.upload-extra-actions { display: flex; gap: .5rem; flex-wrap: wrap; }
.upload-validation-error { margin: 0; color: #c0392b; font-size: var(--cds-text-sm); font-weight: var(--cds-font-semibold); }

.queue-list { display: grid; gap: .35rem; }
.queue-item { display: flex; align-items: center; gap: .75rem; padding: .5rem .75rem; background: rgba(62,60,56,.04); border-radius: .45rem; font-size: var(--cds-text-sm); }
.queue-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--cds-dark); }
.queue-size { color: var(--cds-text-muted); white-space: nowrap; }
.queue-status { white-space: nowrap; font-weight: var(--cds-font-semibold); }
.status--pending { color: var(--cds-text-muted); }
.status--uploading { color: var(--cds-primary); }
.status--done { color: #2e7d32; }
.status--error { color: #c0392b; }

.catalog-filters { display: flex; gap: .5rem; flex-wrap: wrap; }
.catalog-filters input, .catalog-filters select { min-height: 40px; border: 1.5px solid rgba(62,60,56,.25); border-radius: .5rem; padding: .4rem .75rem; font-size: var(--cds-text-sm); background: var(--cds-white); color: var(--cds-dark); }
.catalog-hint { margin: 0; color: var(--cds-text-muted); font-size: var(--cds-text-base); }
.catalog-hint code { background: rgba(62,60,56,.08); padding: .1em .4em; border-radius: .3rem; font-size: .9em; }

.image-grid { display: grid; gap: .75rem; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }
.image-tile { margin: 0; display: grid; border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .6rem; overflow: hidden; background: rgba(62,60,56,.03); }
.image-tile img { width: 100%; aspect-ratio: 1; object-fit: cover; display: block; }
.image-tile figcaption { padding: .35rem .5rem; display: grid; gap: .15rem; }
.tile-name { font-size: var(--cds-text-xs); font-weight: var(--cds-font-semibold); color: var(--cds-dark); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.tile-meta { font-size: var(--cds-text-xs); color: var(--cds-text-muted); }

/* Bindings */
.binding-form { display: grid; gap: .75rem; padding: .9rem; background: rgba(62,60,56,.03); border-radius: .6rem; border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); }
.binding-form-fields { display: grid; gap: .5rem; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); }
.binding-form-fields label { display: grid; gap: .3rem; font-size: var(--cds-text-sm); font-weight: var(--cds-font-semibold); color: var(--cds-dark); }
.binding-form-fields input { min-height: 44px; border: 1.5px solid rgba(62,60,56,.25); border-radius: .5rem; padding: .5rem .75rem; font-size: var(--cds-text-base); background: var(--cds-white); color: var(--cds-dark); }
.binding-picker { display: grid; gap: .5rem; }
.binding-picker-label { font-size: var(--cds-text-sm); font-weight: var(--cds-font-semibold); color: var(--cds-dark); }
.picker-search { min-height: 40px; border: 1.5px solid rgba(62,60,56,.25); border-radius: .5rem; padding: .4rem .75rem; font-size: var(--cds-text-sm); background: var(--cds-white); color: var(--cds-dark); width: 100%; max-width: 320px; }
.picker-grid { display: grid; gap: .5rem; grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); max-height: 260px; overflow-y: auto; padding: .25rem; border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .5rem; }
.picker-tile { margin: 0; cursor: pointer; border: 2px solid transparent; border-radius: .45rem; overflow: hidden; background: rgba(62,60,56,.03); transition: border-color .15s; }
.picker-tile:hover { border-color: color-mix(in srgb, var(--cds-primary) 40%, transparent); }
.picker-tile--selected { border-color: var(--cds-primary); }
.picker-tile img { width: 100%; aspect-ratio: 1; object-fit: cover; display: block; }
.picker-tile figcaption { padding: .2rem .3rem; font-size: var(--cds-text-xs); color: var(--cds-dark); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.bindings-list { display: grid; gap: .4rem; }
.binding-row { display: flex; align-items: center; gap: .75rem; padding: .5rem .75rem; background: rgba(62,60,56,.03); border-radius: .45rem; border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); }
.binding-thumb { width: 48px; height: 48px; object-fit: cover; border-radius: .35rem; flex-shrink: 0; }
.binding-info { flex: 1; display: grid; gap: .1rem; min-width: 0; }
.binding-slot { font-size: var(--cds-text-sm); font-weight: var(--cds-font-semibold); color: var(--cds-dark); font-family: monospace; }
.binding-label { font-size: var(--cds-text-xs); color: var(--cds-text-muted); }
.binding-name { font-size: var(--cds-text-xs); color: var(--cds-text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.binding-actions { display: flex; gap: .35rem; flex-shrink: 0; }
.btn-icon { min-height: 36px; min-width: 36px; padding: .3rem .5rem; border-radius: .4rem; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); background: var(--cds-white); cursor: pointer; font-size: var(--cds-text-sm); }
.btn-icon--danger { border-color: #fcc; color: #c0392b; }
.btn-icon--danger:hover { background: #fdf3f2; }

@media (max-width: 600px) {
  .summary-grid { grid-template-columns: 1fr; }
  .image-grid { grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); }
  .picker-grid { grid-template-columns: repeat(auto-fill, minmax(72px, 1fr)); }
}
</style>
