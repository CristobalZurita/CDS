import { computed, onMounted, ref, watch } from 'vue'
import {
  countMediaAssetsByGroup,
  createMediaBindingForm,
  createMediaQueueItem,
  filterBindingPickerAssets,
  filterMediaAssets,
  importMediaAssetsFromCloudinary,
  listMediaAssets,
  listMediaBindings,
  MEDIA_MAX_FILE_SIZE,
  normalizeMediaAssetGroup,
  removeMediaBinding,
  saveMediaBinding,
  uploadMediaQueueItem,
} from '@/services/mediaAdminService.js'

export function useMediaAdminPage() {
  const images = ref([])
  const loadingCatalog = ref(false)
  const error = ref(null)
  const success = ref('')
  const search = ref('')
  const folderFilter = ref('')

  const importing = ref(false)
  const importProgress = ref('')

  const destination = ref('uploads')
  const queue = ref([])
  const uploading = ref(false)
  const uploadProgress = ref(0)
  const uploadValidationError = ref('')

  const bindings = ref([])
  const loadingBindings = ref(false)
  const showBindingForm = ref(false)
  const savingBinding = ref(false)
  const pickerSearch = ref('')
  const isEditingBinding = ref(false)
  const bindingPendingDelete = ref('')
  const deletingBinding = ref(false)
  const bindingForm = ref(createMediaBindingForm())

  const filtered = computed(() => filterMediaAssets(images.value, {
    folderFilter: folderFilter.value,
    search: search.value,
  }))

  const pickerFiltered = computed(() => filterBindingPickerAssets(
    images.value,
    pickerSearch.value,
    bindingForm.value.asset_id,
  ))

  function setError(message) {
    error.value = message
  }

  function clearStatus() {
    error.value = null
    success.value = ''
  }

  function countByFolder(folder) {
    return countMediaAssetsByGroup(images.value, folder)
  }

  async function loadCatalog() {
    loadingCatalog.value = true
    error.value = null
    success.value = ''
    try {
      images.value = await listMediaAssets()
    } catch {
      error.value = 'Error al cargar el catálogo. Verificá que el backend esté corriendo.'
    } finally {
      loadingCatalog.value = false
    }
  }

  async function importFromCloudinary() {
    if (importing.value) return
    importing.value = true
    importProgress.value = 'conectando...'
    error.value = null
    success.value = ''
    try {
      const data = await importMediaAssetsFromCloudinary()
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

  function addToQueue(files) {
    const rejected = []
    for (const file of files) {
      if (file.size > MEDIA_MAX_FILE_SIZE) {
        rejected.push(`${file.name}: supera 10 MB`)
        continue
      }

      const item = createMediaQueueItem(file, destination.value, file.webkitRelativePath)
      const exists = queue.value.find((entry) =>
        entry.publicId === item.publicId || (entry.name === item.name && entry.size === item.size)
      )
      if (!exists) {
        queue.value.push(item)
      }
    }
    uploadValidationError.value = rejected.length ? rejected.join(' · ') : ''
  }

  async function uploadAll() {
    if (uploading.value) return
    uploading.value = true
    uploadProgress.value = 0
    error.value = null
    success.value = ''
    try {
      for (const item of queue.value) {
        if (item.status === 'done') {
          uploadProgress.value += 1
          continue
        }

        item.status = 'uploading'
        try {
          const uploaded = await uploadMediaQueueItem(item, destination.value)
          item.status = uploaded?.secure_url ? 'done' : 'error'
        } catch {
          item.status = 'error'
        }
        uploadProgress.value += 1
      }
      await loadCatalog()
    } finally {
      uploading.value = false
    }
  }

  function clearQueue() {
    queue.value = queue.value.filter((item) => item.status === 'uploading')
  }

  async function loadBindings() {
    loadingBindings.value = true
    try {
      bindings.value = await listMediaBindings()
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
      await saveMediaBinding(bindingForm.value.slot_key, bindingForm.value)
      bindingForm.value = createMediaBindingForm()
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
      bindingForm.value = createMediaBindingForm()
      pickerSearch.value = ''
    }
  }

  function editBinding(binding) {
    bindingForm.value = {
      slot_key: binding.slot_key,
      label: binding.label || '',
      asset_id: binding.asset?.id || null,
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
      await removeMediaBinding(bindingPendingDelete.value)
      error.value = null
      await loadBindings()
      bindingPendingDelete.value = ''
    } catch {
      error.value = 'Error al quitar el slot.'
    } finally {
      deletingBinding.value = false
    }
  }

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
    const map = {
      pending: 'En cola',
      uploading: 'Subiendo...',
      done: '✓ Listo',
      error: '✗ Error',
    }
    return map[status] || status
  }

  watch(destination, (nextDestination) => {
    queue.value = queue.value.map((item) => {
      if (item.relativePath) return item
      return createMediaQueueItem(item.file, nextDestination)
    })
  })

  onMounted(() => {
    loadCatalog()
    loadBindings()
  })

  return {
    images,
    loadingCatalog,
    error,
    success,
    search,
    folderFilter,
    importing,
    importProgress,
    destination,
    queue,
    uploading,
    uploadProgress,
    uploadValidationError,
    bindings,
    loadingBindings,
    showBindingForm,
    savingBinding,
    pickerSearch,
    isEditingBinding,
    bindingPendingDelete,
    deletingBinding,
    bindingForm,
    filtered,
    pickerFiltered,
    countByFolder,
    loadCatalog,
    importFromCloudinary,
    addToQueue,
    uploadAll,
    clearQueue,
    loadBindings,
    saveBinding,
    toggleBindingForm,
    editBinding,
    updateBindingField,
    selectBindingAsset,
    deleteBinding,
    cancelDeleteBinding,
    confirmDeleteBinding,
    thumb,
    shortName,
    queuePath,
    formatBytes,
    statusLabel,
    normalizeAssetGroup,
    setError,
    clearStatus,
  }
}
