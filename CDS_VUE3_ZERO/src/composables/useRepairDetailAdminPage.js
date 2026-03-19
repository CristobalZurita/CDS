import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { extractErrorMessage } from '@/services/api'
import {
  buildRepairDetailBundleState,
  createNoteDraft,
  createPhotoDraft,
  resolveRepairNoteSubmission,
  resolveRepairPriorityClass,
  resolveRepairPriorityLabel,
  resolveRepairStatusClass,
  resolveRepairStatusLabel,
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
  downloadRepairClosurePdf,
  fetchRepairDetailBundle,
  noteTypeClass,
  notifyRepairClient,
  REPAIR_DETAIL_STATUS_OPTIONS,
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
  const isTerminalStatus = computed(() => Number(repair.value?.status_id || 0) === 9)

  const statusLabel = computed(() => resolveRepairStatusLabel(repair.value))
  const statusClass = computed(() => resolveRepairStatusClass(repair.value))
  const priorityLabel = computed(() => resolveRepairPriorityLabel(repair.value))
  const priorityClass = computed(() => resolveRepairPriorityClass(repair.value))

  function applyRepairScreenState(nextState) {
    repair.value = nextState.repair
    photos.value = nextState.photos
    notes.value = nextState.notes
    statusDraft.value = nextState.statusDraft
    editForm.value = nextState.editForm
  }

  function resetRepairData() {
    applyRepairScreenState(buildRepairDetailBundleState(null))
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

  async function runFlaggedTask(flagRef, task, { resolveError = extractErrorMessage } = {}) {
    flagRef.value = true
    error.value = ''

    try {
      return await task()
    } catch (requestError) {
      error.value = resolveError(requestError)
      return null
    } finally {
      flagRef.value = false
    }
  }

  async function runReloadingTask(flagRef, task, options) {
    const result = await runFlaggedTask(flagRef, task, options)
    if (error.value) return result
    await loadRepair()
    return result
  }

  async function runSuccessfulTask(flagRef, task, { onSuccess, ...options } = {}) {
    const result = await runFlaggedTask(flagRef, task, options)
    if (error.value) return result
    onSuccess?.(result)
    return result
  }

  async function loadRepair() {
    const id = repairId.value
    if (!id) {
      error.value = 'ID de reparacion invalido.'
      return
    }

    const payload = await runFlaggedTask(loading, () => fetchRepairDetailBundle(id))
    if (error.value) {
      resetRepairData()
      return
    }

    applyRepairBundle(payload)
  }

  async function updateStatus() {
    if (!repair.value) return

    await runReloadingTask(updatingStatus, () => updateRepairStatus(repairId.value, statusDraft.value))
  }

  async function saveRepairFields() {
    if (!repair.value) return

    await runReloadingTask(savingRepair, () => saveRepairDetailFields(repairId.value, editForm.value))
  }

  async function archiveRepair() {
    if (!repair.value || isArchived.value) return

    await runReloadingTask(performingAction, () => archiveRepairById(repairId.value))
  }

  async function reactivateRepair() {
    if (!repair.value || !isArchived.value) return

    await runReloadingTask(performingAction, () => reactivateRepairById(repairId.value))
  }

  async function notifyClient() {
    if (!repair.value) return

    await runFlaggedTask(performingAction, () => notifyRepairClient(repairId.value))
  }

  async function requestSignature(type) {
    if (!repair.value) return

    signatureLink.value = ''
    await runSuccessfulTask(
      performingAction,
      () => requestRepairSignatureLink(repairId.value, type),
      { onSuccess: (nextLink) => { signatureLink.value = nextLink || '' } }
    )
  }

  async function requestPhotoUpload() {
    if (!repair.value) return

    photoUploadLink.value = ''
    await runSuccessfulTask(
      performingAction,
      () => requestRepairPhotoUploadLink(repairId.value),
      { onSuccess: (nextLink) => { photoUploadLink.value = nextLink || '' } }
    )
  }

  function onFileSelected(event) {
    photoDraft.value = setRepairPhotoDraftFile(photoDraft.value, event)
  }

  async function uploadPhoto() {
    if (!photoDraft.value.file || !repair.value) return

    await runSuccessfulTask(
      uploadingPhoto,
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

    await runSuccessfulTask(
      savingNote,
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

    await runFlaggedTask(downloadingClosurePdf, () => downloadRepairClosurePdf(repairId.value, repair.value))
  }

  function goToPurchaseRequests() {
    if (!repair.value) return
    router.push({ name: 'admin-purchase-requests', query: { repair_id: repairId.value } })
  }

  function goBack() {
    router.push({ name: 'admin-repairs' })
  }

  onMounted(loadRepair)

  return {
    repairId,
    repair,
    photos,
    notes,
    loading,
    error,
    statusOptions: REPAIR_DETAIL_STATUS_OPTIONS,
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
    goToPurchaseRequests,
    goBack
  }
}
