import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { extractErrorMessage } from '@/services/api'
import {
  buildRepairDetailScreenDrafts,
  createNoteDraft,
  createPhotoDraft,
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

  function resetRepairData() {
    repair.value = null
    photos.value = []
    notes.value = []
  }

  function applyRepairBundle(payload) {
    repair.value = payload?.repair || null
    photos.value = Array.isArray(payload?.photos) ? payload.photos : []
    notes.value = Array.isArray(payload?.notes) ? payload.notes : []

    if (!repair.value) {
      error.value = 'No se encontro la reparacion solicitada.'
    }

    syncDraftFromRepair()
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

  function syncDraftFromRepair() {
    if (!repair.value) {
      statusDraft.value = 1
      editForm.value = baseRepairDetailEditForm()
      return
    }

    const nextDrafts = buildRepairDetailScreenDrafts(repair.value)
    statusDraft.value = nextDrafts.statusDraft
    editForm.value = nextDrafts.editForm
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
    const nextLink = await runFlaggedTask(performingAction, () => requestRepairSignatureLink(repairId.value, type))
    if (!error.value) {
      signatureLink.value = nextLink || ''
    }
  }

  async function requestPhotoUpload() {
    if (!repair.value) return

    photoUploadLink.value = ''
    const nextLink = await runFlaggedTask(performingAction, () => requestRepairPhotoUploadLink(repairId.value))
    if (!error.value) {
      photoUploadLink.value = nextLink || ''
    }
  }

  function onFileSelected(event) {
    photoDraft.value = setRepairPhotoDraftFile(photoDraft.value, event)
  }

  async function uploadPhoto() {
    if (!photoDraft.value.file || !repair.value) return

    const nextPhotos = await runFlaggedTask(
      uploadingPhoto,
      () => uploadRepairPhoto(repairId.value, photoDraft.value.file, {
        photoType: photoDraft.value.type,
        caption: photoDraft.value.caption
      }),
      { resolveError: (requestError) => requestError?.message || extractErrorMessage(requestError) }
    )

    if (!error.value) {
      photos.value = nextPhotos || []
      photoDraft.value = createPhotoDraft()
    }
  }

  async function addNote() {
    if (!repair.value) return

    const note = String(noteDraft.value.text || '').trim()
    if (!note) {
      error.value = 'La nota no puede estar vacia.'
      return
    }

    const nextNotes = await runFlaggedTask(savingNote, () => addRepairNote(repairId.value, {
        note,
        noteType: noteDraft.value.type
      }))

    if (!error.value) {
      notes.value = nextNotes || []
      noteDraft.value = createNoteDraft()
    }
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
