import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { extractErrorMessage } from '@/services/api'
import {
  buildRepairDetailVisibleStatusOptions,
  buildRepairDetailBundleState,
  createNoteDraft,
  createPhotoDraft,
  mergeRepairStatusCatalog,
  resolveRepairNoteSubmission,
  resolveRepairPriorityClass,
  resolveRepairPriorityLabel,
  resolveRepairStatusClass,
  resolveRepairStatusLabel,
  runRepairDetailReloadTask,
  runRepairDetailSuccessTask,
  runRepairDetailTask,
  setRepairPhotoDraftFile,
  toggleRepairNoteDraft,
  toggleRepairPhotoDraft,
  updateRepairNoteDraft,
  updateRepairPhotoDraft
} from '@/composables/repairDetailAdminState'
import {
  addRepairNote,
  archiveRepairById,
  baseRepairDetailEditForm,
  createRepairInvoice,
  createRepairWarranty,
  downloadRepairClosurePdf,
  fetchRepairDetailBundle,
  fetchRepairStatusOptions,
  noteTypeClass,
  notifyRepairClient,
  reactivateRepairById,
  requestRepairPhotoUploadLink,
  requestRepairSignatureLink,
  saveRepairDetailFields,
  updateRepairStatus,
  uploadRepairPhoto
} from '@/services/repairDetailAdminService'
import { formatDate, formatCurrency } from '@/utils/format'

export function useRepairDetailAdminPage() {
  const route = useRoute()
  const router = useRouter()

  const repairId = computed(() => Number(route.params?.id || 0))

  const loading = ref(false)
  const error = ref('')
  const repair = ref(null)
  const photos = ref([])
  const notes = ref([])
  const warranty = ref(null)
  const invoice = ref(null)
  const statusCatalog = ref([])

  const statusDraft = ref(1)
  const editForm = ref(baseRepairDetailEditForm())

  const updatingStatus = ref(false)
  const savingRepair = ref(false)
  const performingAction = ref(false)
  const uploadingPhoto = ref(false)
  const savingNote = ref(false)
  const downloadingClosurePdf = ref(false)

  const photoDraft = ref(createPhotoDraft())
  const noteDraft = ref(createNoteDraft())

  const signatureLink = ref('')
  const photoUploadLink = ref('')

  const isArchived = computed(() => Boolean(repair.value?.archived_at))
  const isTerminalStatus = computed(() => {
    const statusCode = String(repair.value?.status_code || '').trim().toLowerCase()
    return ['archivado', 'rechazado'].includes(statusCode)
  })
  const canCreateWarranty = computed(() => {
    const statusCode = String(repair.value?.status_code || '').trim().toLowerCase()
    return Boolean(
      repair.value
      && !warranty.value
      && ['entregado', 'noventena', 'archivado'].includes(statusCode)
    )
  })
  const canCreateInvoice = computed(() => {
    const statusCode = String(repair.value?.status_code || '').trim().toLowerCase()
    return Boolean(
      repair.value
      && !invoice.value
      && ['listo', 'entregado', 'noventena', 'archivado'].includes(statusCode)
    )
  })

  const statusOptions = computed(() => buildRepairDetailVisibleStatusOptions(statusCatalog.value, repair.value))
  const statusLabel = computed(() => resolveRepairStatusLabel(repair.value, statusCatalog.value))
  const statusClass = computed(() => resolveRepairStatusClass(repair.value))
  const priorityLabel = computed(() => resolveRepairPriorityLabel(repair.value))
  const priorityClass = computed(() => resolveRepairPriorityClass(repair.value))

  function applyRepairScreenState(nextState) {
    repair.value = nextState.repair
    photos.value = nextState.photos
    notes.value = nextState.notes
    warranty.value = nextState.warranty
    invoice.value = nextState.invoice
    statusDraft.value = nextState.statusDraft
    editForm.value = nextState.editForm
  }

  function resetRepairData() {
    applyRepairScreenState(buildRepairDetailBundleState(null))
    statusCatalog.value = []
  }

  function applyRepairBundle(payload) {
    const nextState = buildRepairDetailBundleState(payload)
    applyRepairScreenState(nextState)

    if (!nextState.repair) {
      error.value = 'No se encontro la reparacion solicitada.'
      return
    }
  }

  function updateEditField({ field, value }) {
    if (!field) return
    editForm.value = {
      ...editForm.value,
      [field]: value
    }
  }

  function togglePhotoUpload() {
    photoDraft.value = toggleRepairPhotoDraft(photoDraft.value)
  }

  function updatePhotoField(payload) {
    photoDraft.value = updateRepairPhotoDraft(photoDraft.value, payload)
  }

  function toggleNoteForm() {
    noteDraft.value = toggleRepairNoteDraft(noteDraft.value)
  }

  function updateNoteField(payload) {
    noteDraft.value = updateRepairNoteDraft(noteDraft.value, payload)
  }

  async function loadRepair() {
    const id = repairId.value
    if (!id) {
      error.value = 'ID de reparacion invalido.'
      return
    }

    const payload = await runRepairDetailTask(loading, error, async () => {
      const [bundle, nextStatusCatalog] = await Promise.all([
        fetchRepairDetailBundle(id),
        fetchRepairStatusOptions().catch(() => [])
      ])

      return {
        bundle,
        statusCatalog: nextStatusCatalog
      }
    })
    if (error.value) {
      resetRepairData()
      return
    }

    applyRepairBundle(payload?.bundle)
    statusCatalog.value = mergeRepairStatusCatalog(payload?.statusCatalog, payload?.bundle?.repair)
  }

  async function updateStatus() {
    if (!repair.value) return

    await runRepairDetailReloadTask(
      updatingStatus,
      error,
      () => updateRepairStatus(repairId.value, statusDraft.value),
      loadRepair
    )
  }

  async function saveRepairFields() {
    if (!repair.value) return

    await runRepairDetailReloadTask(
      savingRepair,
      error,
      () => saveRepairDetailFields(repairId.value, editForm.value),
      loadRepair
    )
  }

  async function archiveRepair() {
    if (!repair.value || isArchived.value) return

    await runRepairDetailReloadTask(
      performingAction,
      error,
      () => archiveRepairById(repairId.value),
      loadRepair
    )
  }

  async function reactivateRepair() {
    if (!repair.value || !isArchived.value) return

    await runRepairDetailReloadTask(
      performingAction,
      error,
      () => reactivateRepairById(repairId.value),
      loadRepair
    )
  }

  async function notifyClient() {
    if (!repair.value) return

    await runRepairDetailTask(performingAction, error, () => notifyRepairClient(repairId.value))
  }

  async function requestSignature(type) {
    if (!repair.value) return

    signatureLink.value = ''
    await runRepairDetailSuccessTask(
      performingAction,
      error,
      () => requestRepairSignatureLink(repairId.value, type),
      { onSuccess: (nextLink) => { signatureLink.value = nextLink || '' } }
    )
  }

  async function requestPhotoUpload() {
    if (!repair.value) return

    photoUploadLink.value = ''
    await runRepairDetailSuccessTask(
      performingAction,
      error,
      () => requestRepairPhotoUploadLink(repairId.value),
      { onSuccess: (nextLink) => { photoUploadLink.value = nextLink || '' } }
    )
  }

  function onFileSelected(event) {
    photoDraft.value = setRepairPhotoDraftFile(photoDraft.value, event)
  }

  async function uploadPhoto() {
    if (!photoDraft.value.file || !repair.value) return

    await runRepairDetailSuccessTask(
      uploadingPhoto,
      error,
      () => uploadRepairPhoto(repairId.value, photoDraft.value.file, {
        photoType: photoDraft.value.type,
        caption: photoDraft.value.caption
      }),
      {
        resolveError: (requestError) => requestError?.message || extractErrorMessage(requestError),
        onSuccess: (nextPhotos) => {
          photos.value = nextPhotos || []
          photoDraft.value = createPhotoDraft()
        }
      }
    )
  }

  async function addNote() {
    if (!repair.value) return

    const noteSubmission = resolveRepairNoteSubmission(noteDraft.value)
    if (!noteSubmission.isValid) {
      error.value = noteSubmission.error
      return
    }

    await runRepairDetailSuccessTask(
      savingNote,
      error,
      () => addRepairNote(repairId.value, noteSubmission),
      {
        onSuccess: (nextNotes) => {
          notes.value = nextNotes || []
          noteDraft.value = createNoteDraft()
        }
      }
    )
  }

  async function downloadClosurePdf() {
    if (!repair.value) return

    await runRepairDetailTask(
      downloadingClosurePdf,
      error,
      () => downloadRepairClosurePdf(repairId.value, repair.value)
    )
  }

  function goToPurchaseRequests() {
    if (!repair.value) return
    router.push({ name: 'admin-purchase-requests', query: { repair_id: repairId.value } })
  }

  function goBack() {
    router.push({ name: 'admin-repairs' })
  }

  async function createWarranty() {
    if (!repair.value || !canCreateWarranty.value) return

    await runRepairDetailSuccessTask(
      performingAction,
      error,
      () => createRepairWarranty(repairId.value),
      {
        onSuccess: (nextWarranty) => {
          warranty.value = nextWarranty || null
        }
      }
    )
  }

  async function createInvoice() {
    if (!repair.value || !canCreateInvoice.value) return

    await runRepairDetailSuccessTask(
      performingAction,
      error,
      () => createRepairInvoice(repairId.value),
      {
        onSuccess: (nextInvoice) => {
          invoice.value = nextInvoice || null
        }
      }
    )
  }

  onMounted(loadRepair)

  return {
    repairId,
    repair,
    photos,
    notes,
    warranty,
    invoice,
    loading,
    error,
    statusOptions,
    statusDraft,
    editForm,
    updatingStatus,
    savingRepair,
    performingAction,
    uploadingPhoto,
    savingNote,
    downloadingClosurePdf,
    showPhotoUpload: computed(() => photoDraft.value.open),
    selectedFile: computed(() => photoDraft.value.file),
    newPhotoCaption: computed(() => photoDraft.value.caption),
    newPhotoType: computed(() => photoDraft.value.type),
    showNoteForm: computed(() => noteDraft.value.open),
    newNote: computed(() => noteDraft.value.text),
    newNoteType: computed(() => noteDraft.value.type),
    signatureLink,
    photoUploadLink,
    isArchived,
    isTerminalStatus,
    canCreateWarranty,
    canCreateInvoice,
    statusLabel,
    statusClass,
    priorityLabel,
    priorityClass,
    formatDate,
    formatCurrency,
    noteTypeClass,
    loadRepair,
    updateStatus,
    saveRepairFields,
    archiveRepair,
    reactivateRepair,
    notifyClient,
    requestSignature,
    requestPhotoUpload,
    updateEditField,
    togglePhotoUpload,
    onFileSelected,
    updatePhotoField,
    uploadPhoto,
    toggleNoteForm,
    updateNoteField,
    addNote,
    downloadClosurePdf,
    createWarranty,
    createInvoice,
    goToPurchaseRequests,
    goBack
  }
}
