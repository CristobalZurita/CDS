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

    loading.value = true
    error.value = ''

    try {
      const payload = await fetchRepairDetailBundle(id)
      repair.value = payload.repair
      photos.value = payload.photos
      notes.value = payload.notes

      if (!repair.value) {
        error.value = 'No se encontro la reparacion solicitada.'
      }

      syncDraftFromRepair()
    } catch (requestError) {
      repair.value = null
      photos.value = []
      notes.value = []
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function updateStatus() {
    if (!repair.value) return

    updatingStatus.value = true
    error.value = ''

    try {
      await updateRepairStatus(repairId.value, statusDraft.value)
      await loadRepair()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      updatingStatus.value = false
    }
  }

  async function saveRepairFields() {
    if (!repair.value) return

    savingRepair.value = true
    error.value = ''

    try {
      await saveRepairDetailFields(repairId.value, editForm.value)
      await loadRepair()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      savingRepair.value = false
    }
  }

  async function archiveRepair() {
    if (!repair.value || isArchived.value) return

    performingAction.value = true
    error.value = ''

    try {
      await archiveRepairById(repairId.value)
      await loadRepair()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      performingAction.value = false
    }
  }

  async function reactivateRepair() {
    if (!repair.value || !isArchived.value) return

    performingAction.value = true
    error.value = ''

    try {
      await reactivateRepairById(repairId.value)
      await loadRepair()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      performingAction.value = false
    }
  }

  async function notifyClient() {
    if (!repair.value) return

    performingAction.value = true
    error.value = ''

    try {
      await notifyRepairClient(repairId.value)
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      performingAction.value = false
    }
  }

  async function requestSignature(type) {
    if (!repair.value) return

    performingAction.value = true
    error.value = ''
    signatureLink.value = ''

    try {
      signatureLink.value = await requestRepairSignatureLink(repairId.value, type)
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      performingAction.value = false
    }
  }

  async function requestPhotoUpload() {
    if (!repair.value) return

    performingAction.value = true
    error.value = ''
    photoUploadLink.value = ''

    try {
      photoUploadLink.value = await requestRepairPhotoUploadLink(repairId.value)
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      performingAction.value = false
    }
  }

  function onFileSelected(event) {
    photoDraft.value = setRepairPhotoDraftFile(photoDraft.value, event)
  }

  async function uploadPhoto() {
    if (!photoDraft.value.file || !repair.value) return

    uploadingPhoto.value = true
    error.value = ''

    try {
      photos.value = await uploadRepairPhoto(repairId.value, photoDraft.value.file, {
        photoType: photoDraft.value.type,
        caption: photoDraft.value.caption
      })

      photoDraft.value = createPhotoDraft()
    } catch (requestError) {
      error.value = requestError?.message || extractErrorMessage(requestError)
    } finally {
      uploadingPhoto.value = false
    }
  }

  async function addNote() {
    if (!repair.value) return

    const note = String(noteDraft.value.text || '').trim()
    if (!note) {
      error.value = 'La nota no puede estar vacia.'
      return
    }

    savingNote.value = true
    error.value = ''

    try {
      notes.value = await addRepairNote(repairId.value, {
        note,
        noteType: noteDraft.value.type
      })

      noteDraft.value = createNoteDraft()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      savingNote.value = false
    }
  }

  async function downloadClosurePdf() {
    if (!repair.value) return

    downloadingClosurePdf.value = true
    error.value = ''

    try {
      await downloadRepairClosurePdf(repairId.value, repair.value)
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      downloadingClosurePdf.value = false
    }
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
