import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { extractErrorMessage } from '@/services/api'
import {
  buildRepairDetailVisibleStatusOptions,
  buildRepairDetailBundleState,
  createClaimDraft,
  createNoteDraft,
  createPaymentDraft,
  createPhotoDraft,
  mergeRepairStatusCatalog,
  resolveRepairClaimSubmission,
  resolveRepairNoteSubmission,
  resolveRepairPaymentSubmission,
  resolveRepairPriorityClass,
  resolveRepairPriorityLabel,
  resolveRepairStatusClass,
  resolveRepairStatusLabel,
  runRepairDetailReloadTask,
  runRepairDetailSuccessTask,
  runRepairDetailTask,
  setRepairPhotoDraftFile,
  toggleRepairClaimDraft,
  toggleRepairPaymentDraft,
  toggleRepairNoteDraft,
  toggleRepairPhotoDraft,
  updateRepairClaimDraft,
  updateRepairNoteDraft,
  updateRepairPaymentDraft,
  updateRepairPhotoDraft
} from '@/composables/repairDetailAdminState'
import {
  addRepairNote,
  archiveRepairById,
  baseRepairDetailEditForm,
  cancelRepairSignatureRequest,
  createRepairInvoice,
  createWarrantyClaim,
  createRepairWarranty,
  downloadRepairClosurePdf,
  fetchRepairDetailBundle,
  fetchRepairStatusOptions,
  noteTypeClass,
  notifyRepairClient,
  recordInvoicePayment,
  reactivateRepairById,
  requestRepairPhotoUploadLink,
  requestRepairSignatureLink,
  saveRepairDetailFields,
  updateRepairStatus,
  uploadRepairPhoto
} from '@/services/repairDetailAdminService'
import { openSignatureRequestStream } from '@/services/tokenRequestService'
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
  const audit = ref([])
  const warranty = ref(null)
  const invoice = ref(null)
  const claims = ref([])
  const payments = ref([])
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
  const claimDraft = ref(createClaimDraft())
  const paymentDraft = ref(createPaymentDraft())

  const signatureLink = ref('')
  const photoUploadLink = ref('')
  const signatureRequest = ref(null)
  const photoUploadRequest = ref(null)

  let stopSignatureStream = () => {}

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
  const canSubmitWarrantyClaim = computed(() => {
    if (!warranty.value?.id) return false
    if (!warranty.value.is_active) return false
    return Number(warranty.value.claims_used || 0) < Number(warranty.value.max_claims || 0)
  })
  const canRecordInvoicePayment = computed(() => {
    if (!invoice.value?.id) return false
    if (String(invoice.value.status || '').toLowerCase() === 'void') return false
    return Number(invoice.value.amount_due || 0) > 0
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
    audit.value = nextState.audit
    warranty.value = nextState.warranty
    invoice.value = nextState.invoice
    claims.value = nextState.claims
    payments.value = nextState.payments
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

    if (signatureRequest.value) {
      const signaturePath = signatureRequest.value.request_type === 'retiro'
        ? nextState.repair?.signature_retiro_path
        : nextState.repair?.signature_ingreso_path

      if (signaturePath) {
        signatureRequest.value = {
          ...signatureRequest.value,
          status: 'signed',
          url: ''
        }
        signatureLink.value = ''
        stopSignatureStream()
        stopSignatureStream = () => {}
      }
    }
  }

  function resetSignatureStream() {
    stopSignatureStream()
    stopSignatureStream = () => {}
  }

  function connectSignatureStream(token) {
    resetSignatureStream()

    if (!token) return

    stopSignatureStream = openSignatureRequestStream(token, {
      onEvent: async (eventName) => {
        if (eventName === 'signature_received') {
          signatureRequest.value = signatureRequest.value
            ? { ...signatureRequest.value, status: 'signed', url: '' }
            : null
          signatureLink.value = ''
          resetSignatureStream()
          await loadRepair()
          return
        }

        if (eventName === 'signature_cancelled') {
          signatureRequest.value = signatureRequest.value
            ? { ...signatureRequest.value, status: 'cancelled', url: '' }
            : null
          signatureLink.value = ''
          resetSignatureStream()
        }
      },
      onError: () => {
        stopSignatureStream = () => {}
      }
    })
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

  function toggleClaimForm() {
    claimDraft.value = toggleRepairClaimDraft(claimDraft.value)
  }

  function updateClaimField(payload) {
    claimDraft.value = updateRepairClaimDraft(claimDraft.value, payload)
  }

  function togglePaymentForm() {
    paymentDraft.value = toggleRepairPaymentDraft(paymentDraft.value)
  }

  function updatePaymentField(payload) {
    paymentDraft.value = updateRepairPaymentDraft(paymentDraft.value, payload)
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
      {
        onSuccess: (nextRequest) => {
          signatureRequest.value = nextRequest || null
          signatureLink.value = nextRequest?.url || ''
          connectSignatureStream(nextRequest?.token || '')
        }
      }
    )
  }

  async function requestPhotoUpload() {
    if (!repair.value) return

    photoUploadLink.value = ''
    await runRepairDetailSuccessTask(
      performingAction,
      error,
      () => requestRepairPhotoUploadLink(repairId.value),
      {
        onSuccess: (nextRequest) => {
          photoUploadRequest.value = nextRequest || null
          photoUploadLink.value = nextRequest?.url || ''
        }
      }
    )
  }

  async function cancelSignature() {
    const requestId = Number(signatureRequest.value?.id || 0)
    if (!requestId) return

    await runRepairDetailSuccessTask(
      performingAction,
      error,
      () => cancelRepairSignatureRequest(requestId),
      {
        onSuccess: () => {
          signatureRequest.value = signatureRequest.value
            ? { ...signatureRequest.value, status: 'cancelled', url: '' }
            : null
          signatureLink.value = ''
          resetSignatureStream()
        }
      }
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

  async function submitWarrantyClaim() {
    if (!warranty.value?.id || !canSubmitWarrantyClaim.value) return

    const claimSubmission = resolveRepairClaimSubmission(claimDraft.value)
    if (!claimSubmission.isValid) {
      error.value = claimSubmission.error
      return
    }

    await runRepairDetailReloadTask(
      performingAction,
      error,
      () => createWarrantyClaim(warranty.value.id, claimSubmission),
      async () => {
        claimDraft.value = createClaimDraft()
        await loadRepair()
      }
    )
  }

  async function submitInvoicePayment() {
    if (!invoice.value?.id || !canRecordInvoicePayment.value) return

    const paymentSubmission = resolveRepairPaymentSubmission(paymentDraft.value)
    if (!paymentSubmission.isValid) {
      error.value = paymentSubmission.error
      return
    }

    await runRepairDetailReloadTask(
      performingAction,
      error,
      () => recordInvoicePayment(invoice.value.id, paymentSubmission),
      async () => {
        paymentDraft.value = createPaymentDraft()
        await loadRepair()
      }
    )
  }

  onMounted(loadRepair)
  onBeforeUnmount(() => {
    resetSignatureStream()
  })

  return {
    repairId,
    repair,
    photos,
    notes,
    audit,
    warranty,
    invoice,
    claims,
    payments,
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
    showClaimForm: computed(() => claimDraft.value.open),
    claimProblemDescription: computed(() => claimDraft.value.problemDescription),
    claimFaultType: computed(() => claimDraft.value.faultType),
    showPaymentForm: computed(() => paymentDraft.value.open),
    paymentAmount: computed(() => paymentDraft.value.amount),
    paymentMethod: computed(() => paymentDraft.value.paymentMethod),
    paymentTransactionId: computed(() => paymentDraft.value.transactionId),
    signatureLink,
    photoUploadLink,
    signatureRequest,
    photoUploadRequest,
    isArchived,
    isTerminalStatus,
    canCreateWarranty,
    canCreateInvoice,
    canSubmitWarrantyClaim,
    canRecordInvoicePayment,
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
    cancelSignature,
    updateEditField,
    togglePhotoUpload,
    onFileSelected,
    updatePhotoField,
    uploadPhoto,
    toggleNoteForm,
    updateNoteField,
    addNote,
    toggleClaimForm,
    updateClaimField,
    submitWarrantyClaim,
    togglePaymentForm,
    updatePaymentField,
    submitInvoicePayment,
    downloadClosurePdf,
    createWarranty,
    createInvoice,
    goToPurchaseRequests,
    goBack
  }
}
