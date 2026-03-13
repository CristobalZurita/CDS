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
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section class="summary-grid">
      <article class="summary-card">
        <span>Total en Cloudinary</span>
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
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="onDrop"
        @click="fileInput.click()"
      >
        <i class="fa-solid fa-cloud-arrow-up"></i>
        <p>Arrastrá imágenes aquí o hacé clic para seleccionar</p>
        <span>Podés seleccionar múltiples archivos</span>
        <input ref="fileInput" type="file" multiple accept="image/*" @change="onFileSelect" />
      </div>

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

      <p v-if="loadingCatalog" class="catalog-hint">Cargando catálogo desde Cloudinary...</p>
      <p v-else-if="!images.length" class="catalog-hint">No hay imágenes en el catálogo o Cloudinary no está conectado.</p>

      <div v-else class="image-grid">
        <figure v-for="img in filtered" :key="img.public_id" class="image-tile">
          <img :src="thumb(img.url)" :alt="shortName(img.public_id)" loading="lazy" />
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
import { uploadImage } from '@/services/uploadService.js'

const images = ref([])
const loadingCatalog = ref(false)
const error = ref(null)

const destination = ref('uploads')
const isDragging = ref(false)
const queue = ref([])
const uploading = ref(false)
const uploadProgress = ref(0)
const fileInput = ref(null)

const search = ref('')
const folderFilter = ref('')

const filtered = computed(() => {
  let list = images.value
  if (folderFilter.value) {
    list = list.filter(img => img.public_id?.includes(folderFilter.value))
  }
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(img => img.public_id?.toLowerCase().includes(q))
  }
  return list
})

function countByFolder(folder) {
  return images.value.filter(img => img.public_id?.includes(folder)).length
}

async function loadCatalog() {
  loadingCatalog.value = true
  error.value = null
  try {
    const { data } = await api.get('/images/catalog')
    images.value = data?.images || []
  } catch {
    error.value = 'Error al cargar el catálogo. Verificá que el backend esté corriendo y Cloudinary configurado.'
  } finally {
    loadingCatalog.value = false
  }
}

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
  for (const file of files) {
    const exists = queue.value.find(q => q.name === file.name && q.size === file.size)
    if (!exists) {
      queue.value.push({ file, name: file.name, size: file.size, status: 'pending' })
    }
  }
}

async function uploadAll() {
  uploading.value = true
  uploadProgress.value = 0
  for (const item of queue.value) {
    if (item.status === 'done') { uploadProgress.value++; continue }
    item.status = 'uploading'
    try {
      const url = await uploadImage(item.file, destination.value)
      item.status = url ? 'done' : 'error'
    } catch {
      item.status = 'error'
    }
    uploadProgress.value++
  }
  uploading.value = false
  await loadCatalog()
}

function clearQueue() {
  queue.value = queue.value.filter(i => i.status === 'uploading')
}

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

onMounted(loadCatalog)
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

.image-grid { display: grid; gap: .75rem; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }
.image-tile { margin: 0; display: grid; border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .6rem; overflow: hidden; background: rgba(62,60,56,.03); }
.image-tile img { width: 100%; aspect-ratio: 1; object-fit: cover; display: block; }
.image-tile figcaption { padding: .35rem .5rem; display: grid; gap: .15rem; }
.tile-name { font-size: var(--cds-text-xs); font-weight: var(--cds-font-semibold); color: var(--cds-dark); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.tile-meta { font-size: var(--cds-text-xs); color: var(--cds-text-muted); }

@media (max-width: 600px) {
  .summary-grid { grid-template-columns: 1fr; }
  .image-grid { grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); }
}
</style>
