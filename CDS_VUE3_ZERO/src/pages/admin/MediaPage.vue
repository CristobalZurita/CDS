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
    <p v-if="success" class="admin-success">{{ success }}</p>

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

    <MediaUploadPanel
      v-model:destination="destination"
      :queue="queue"
      :uploading="uploading"
      :upload-progress="uploadProgress"
      :upload-validation-error="uploadValidationError"
      :format-bytes="formatBytes"
      :queue-path="queuePath"
      :status-label="statusLabel"
      @files-selected="addToQueue"
      @upload-all="uploadAll"
      @clear-queue="clearQueue"
    />

    <MediaBindingsPanel
      :bindings="bindings"
      :loading-bindings="loadingBindings"
      :show-binding-form="showBindingForm"
      :saving-binding="savingBinding"
      :is-editing-binding="isEditingBinding"
      :picker-search="pickerSearch"
      :picker-filtered="pickerFiltered"
      :binding-form="bindingForm"
      :binding-pending-delete="bindingPendingDelete"
      :deleting-binding="deletingBinding"
      :thumb="thumb"
      :short-name="shortName"
      @toggle-binding-form="toggleBindingForm"
      @update-binding-field="updateBindingField"
      @update:picker-search="pickerSearch = $event"
      @select-asset="selectBindingAsset"
      @save-binding="saveBinding"
      @edit-binding="editBinding"
      @request-delete-binding="deleteBinding"
      @cancel-delete-binding="cancelDeleteBinding"
      @confirm-delete-binding="confirmDeleteBinding"
    />

    <MediaCatalogPanel
      v-model:search="search"
      v-model:folder-filter="folderFilter"
      :images="images"
      :filtered="filtered"
      :loading-catalog="loadingCatalog"
      :thumb="thumb"
      :short-name="shortName"
      :format-bytes="formatBytes"
    />
  </main>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import MediaBindingsPanel from '@/components/admin/MediaBindingsPanel.vue'
import MediaCatalogPanel from '@/components/admin/MediaCatalogPanel.vue'
import MediaUploadPanel from '@/components/admin/MediaUploadPanel.vue'
import api from '@/services/api.js'
import { resolveUploadPublicId, uploadImageWithMeta } from '@/services/uploadService.js'

// ─── Catálogo (desde BD) ───────────────────────────────────────────────────
const images = ref([])
const loadingCatalog = ref(false)
const error = ref(null)
const success = ref('')
const search = ref('')
const folderFilter = ref('')

function normalizeAssetGroup(img) {
  const source = String(img?.folder || img?.public_id || '').toLowerCase()
  if (source.startsWith('instrumentos/') || source.includes('/instrumentos/')) return 'instrumentos'
  if (source.startsWith('inventario/') || source.startsWith('inventario') || source.includes('/inventario/')) return 'inventario'
  if (source.startsWith('inventa') || String(img?.folder || img?.public_id || '').startsWith('INVENTARIO')) return 'inventario'
  return 'general'
}

const filtered = computed(() => {
  let list = images.value
  if (folderFilter.value) {
    list = list.filter(img => normalizeAssetGroup(img) === folderFilter.value)
  }
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(img => img.public_id?.toLowerCase().includes(q))
  }
  return list
})

function countByFolder(folder) {
  return images.value.filter(img => normalizeAssetGroup(img) === folder).length
}

async function loadCatalog() {
  loadingCatalog.value = true
  error.value = null
  success.value = ''
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
  success.value = ''
  try {
    const { data } = await api.post('/media/assets/import-from-cloudinary')
    importProgress.value = ''
    await loadCatalog()
    const { inserted = 0, updated = 0, total = 0 } = data
    success.value = `Importación completa: ${total} imágenes procesadas (${inserted} nuevas, ${updated} actualizadas).`
  } catch {
    error.value = 'Error al importar desde Cloudinary. Verificá que el backend tenga acceso a Cloudinary.'
  } finally {
    importing.value = false
    importProgress.value = ''
  }
}

// ─── Upload ────────────────────────────────────────────────────────────────
const destination = ref('uploads')
const queue = ref([])
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadValidationError = ref('')
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10 MB

function addToQueue(files) {
  const rechazados = []
  for (const file of files) {
    if (file.size > MAX_FILE_SIZE) {
      rechazados.push(`${file.name}: supera 10 MB`)
      continue
    }
    const relativePath = String(file.webkitRelativePath || '').replace(/\\/g, '/').replace(/^\/+/, '').replace(/^images\//i, '')
    const publicId = resolveUploadPublicId(file, destination.value, relativePath)
    const exists = queue.value.find(q => q.publicId === publicId || (q.name === file.name && q.size === file.size))
    if (!exists) {
      queue.value.push({
        file,
        name: file.name,
        size: file.size,
        relativePath,
        publicId,
        status: 'pending',
      })
    }
  }
  uploadValidationError.value = rechazados.length ? rechazados.join(' · ') : ''
}

async function uploadAll() {
  if (uploading.value) return
  uploading.value = true
  uploadProgress.value = 0
  error.value = null
  success.value = ''
  try {
    for (const item of queue.value) {
      if (item.status === 'done') { uploadProgress.value++; continue }
      item.status = 'uploading'
      try {
        const explicitPublicId = item.publicId || resolveUploadPublicId(item.file, destination.value, item.relativePath)
        const meta = await uploadImageWithMeta(item.file, destination.value, explicitPublicId)
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

watch(destination, (nextDestination) => {
  queue.value = queue.value.map((item) => {
    if (item.relativePath) return item
    return {
      ...item,
      publicId: resolveUploadPublicId(item.file, nextDestination),
    }
  })
})

// ─── Bindings ──────────────────────────────────────────────────────────────
const bindings = ref([])
const loadingBindings = ref(false)
const showBindingForm = ref(false)
const savingBinding = ref(false)
const pickerSearch = ref('')
const isEditingBinding = ref(false)
const bindingPendingDelete = ref('')
const deletingBinding = ref(false)

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
  success.value = ''
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

function updateBindingField({ field, value }) {
  if (!field) return
  bindingForm.value = {
    ...bindingForm.value,
    [field]: value,
  }
}

function selectBindingAsset(assetId) {
  bindingForm.value = {
    ...bindingForm.value,
    asset_id: assetId,
  }
}

function deleteBinding(slotKey) {
  bindingPendingDelete.value = slotKey
}

function cancelDeleteBinding() {
  if (deletingBinding.value) return
  bindingPendingDelete.value = ''
}

async function confirmDeleteBinding() {
  if (!bindingPendingDelete.value || deletingBinding.value) return
  deletingBinding.value = true
  success.value = ''
  try {
    await api.delete(`/media/bindings/${bindingPendingDelete.value}`)
    error.value = null
    await loadBindings()
    bindingPendingDelete.value = ''
  } catch {
    error.value = 'Error al quitar el slot.'
  } finally {
    deletingBinding.value = false
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

function queuePath(item) {
  if (item?.relativePath) return item.relativePath
  return item?.publicId || item?.name || ''
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

<style scoped src="./commonAdminPage.css"></style>
<style scoped src="./mediaPageShared.css"></style>
