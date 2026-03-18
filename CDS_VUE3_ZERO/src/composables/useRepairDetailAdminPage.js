import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { extractErrorMessage } from '@/services/api'
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

  const showPhotoUpload = ref(false)
  const selectedFile = ref(null)
  const newPhotoCaption = ref('')
  const newPhotoType = ref('general')

  const showNoteForm = ref(false)
  const newNote = ref('')
  const newNoteType = ref('internal')

  const signatureLink = ref('')
  const photoUploadLink = ref('')

  const isArchived = computed(() => Boolean(repair.value?.archived_at))
  const isTerminalStatus = computed(() => Number(repair.value?.status_id || 0) === 9)

  const statusLabel = computed(() => {
    const match = REPAIR_DETAIL_STATUS_OPTIONS.find((option) => option.id === Number(repair.value?.status_id || 0))
    return match?.label || String(repair.value?.status || 'Sin estado')
  })

  const statusClass = computed(() => {
    const statusId = Number(repair.value?.status_id || 0)
    if ([1, 2, 3].includes(statusId)) return 'status-pending'
    if ([4, 5, 6].includes(statusId)) return 'status-progress'
    if ([7, 8].includes(statusId)) return 'status-success'
    if (statusId === 9) return 'status-archived'
    return 'status-neutral'
  })

  const priorityLabel = computed(() => {
    const priority = Number(repair.value?.priority || 2)
    if (priority === 1) return 'Alta'
    if (priority === 3) return 'Baja'
    return 'Normal'
  })

  const priorityClass = computed(() => {
    const priority = Number(repair.value?.priority || 2)
    if (priority === 1) return 'priority-high'
    if (priority === 3) return 'priority-low'
    return 'priority-normal'
  })

  function syncDraftFromRepair() {
    if (!repair.value) {
      statusDraft.value = 1
      editForm.value = baseRepairDetailEditForm()
      return
    }

    statusDraft.value = Number(repair.value.status_id || 1)
    editForm.value = {
      diagnosis: String(repair.value.diagnosis || ''),
      work_performed: String(repair.value.work_performed || ''),
      parts_cost: Number(repair.value.parts_cost || 0),
      labor_cost: Number(repair.value.labor_cost || 0),
      additional_cost: Number(repair.value.additional_cost || 0),
      discount: Number(repair.value.discount || 0),
      total_cost: Number(repair.value.total_cost || 0),
      paid_amount: Number(repair.value.paid_amount || 0),
      payment_method: String(repair.value.payment_method || 'cash')
    }
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
    const file = event?.target?.files?.[0] || null
    selectedFile.value = file
  }

  async function uploadPhoto() {
    if (!selectedFile.value || !repair.value) return

    uploadingPhoto.value = true
    error.value = ''

    try {
      photos.value = await uploadRepairPhoto(repairId.value, selectedFile.value, {
        photoType: newPhotoType.value,
        caption: newPhotoCaption.value
      })

      selectedFile.value = null
      newPhotoCaption.value = ''
      newPhotoType.value = 'general'
      showPhotoUpload.value = false
    } catch (requestError) {
      error.value = requestError?.message || extractErrorMessage(requestError)
    } finally {
      uploadingPhoto.value = false
    }
  }

  async function addNote() {
    if (!repair.value) return

    const note = String(newNote.value || '').trim()
    if (!note) {
      error.value = 'La nota no puede estar vacia.'
      return
    }

    savingNote.value = true
    error.value = ''

    try {
      notes.value = await addRepairNote(repairId.value, {
        note,
        noteType: newNoteType.value
      })

      newNote.value = ''
      newNoteType.value = 'internal'
      showNoteForm.value = false
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
    showPhotoUpload,
    selectedFile,
    newPhotoCaption,
    newPhotoType,
    showNoteForm,
    newNote,
    newNoteType,
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
    onFileSelected,
    uploadPhoto,
    addNote,
    downloadClosurePdf,
    goToPurchaseRequests,
    goBack
  }
}
