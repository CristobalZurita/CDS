import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { extractErrorMessage } from '@/services/api'

const STATUS_OPTIONS = [
  { id: 1, label: 'Ingreso' },
  { id: 2, label: 'Diagnostico' },
  { id: 3, label: 'Presupuesto' },
  { id: 4, label: 'Aprobado' },
  { id: 5, label: 'En trabajo' },
  { id: 6, label: 'Listo' },
  { id: 7, label: 'Entregado' },
  { id: 8, label: 'Noventena' },
  { id: 9, label: 'Archivado' },
  { id: 10, label: 'Rechazado' }
]

function buildApiHost() {
  const rawBase = String(import.meta.env.VITE_API_URL || '/api/v1').trim()

  if (rawBase.startsWith('http://') || rawBase.startsWith('https://')) {
    const baseWithoutApi = rawBase.includes('/api/') ? rawBase.split('/api/')[0] : rawBase
    return baseWithoutApi.replace(/\/+$/, '')
  }

  if (typeof window !== 'undefined' && window.location?.origin) {
    return window.location.origin
  }

  return ''
}

const API_HOST = buildApiHost()

function toAbsoluteUrl(value) {
  const path = String(value || '').trim()
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  if (path.startsWith('/')) return `${API_HOST}${path}`
  return `${API_HOST}/${path}`
}

function normalizePhoto(entry) {
  const relative = entry?.photo_url || entry?.photo_download_url || ''
  return {
    id: Number(entry?.id || 0),
    photo_type: String(entry?.photo_type || 'general'),
    caption: String(entry?.caption || ''),
    created_at: entry?.created_at || null,
    resolved_photo_url: toAbsoluteUrl(relative)
  }
}

function normalizeNote(entry) {
  return {
    id: Number(entry?.id || 0),
    note: String(entry?.note || ''),
    note_type: String(entry?.note_type || 'internal'),
    created_at: entry?.created_at || null,
    user_id: entry?.user_id || null
  }
}

function normalizeRepair(entry) {
  if (!entry || typeof entry !== 'object') return null
  return {
    id: Number(entry?.id || 0),
    repair_code: String(entry?.repair_code || entry?.repair_number || ''),
    repair_number: String(entry?.repair_number || ''),
    status_id: Number(entry?.status_id || 0),
    status: String(entry?.status || ''),
    priority: Number(entry?.priority || 2),
    archived_at: entry?.archived_at || null,
    problem_reported: String(entry?.problem_reported || ''),
    diagnosis: String(entry?.diagnosis || ''),
    work_performed: String(entry?.work_performed || ''),
    parts_cost: Number(entry?.parts_cost || 0),
    labor_cost: Number(entry?.labor_cost || 0),
    additional_cost: Number(entry?.additional_cost || 0),
    discount: Number(entry?.discount || 0),
    total_cost: Number(entry?.total_cost || 0),
    paid_amount: Number(entry?.paid_amount || 0),
    payment_status: String(entry?.payment_status || ''),
    payment_method: String(entry?.payment_method || ''),
    signature_ingreso_path: String(entry?.signature_ingreso_path || ''),
    signature_retiro_path: String(entry?.signature_retiro_path || ''),
    client: entry?.client || null,
    device: entry?.device || null
  }
}

function baseEditForm() {
  return {
    diagnosis: '',
    work_performed: '',
    parts_cost: 0,
    labor_cost: 0,
    additional_cost: 0,
    discount: 0,
    total_cost: 0,
    paid_amount: 0,
    payment_method: ''
  }
}

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
  const editForm = ref(baseEditForm())

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
    const match = STATUS_OPTIONS.find((option) => option.id === Number(repair.value?.status_id || 0))
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
      editForm.value = baseEditForm()
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

  function formatDate(value) {
    if (!value) return '—'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '—'
    return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium', timeStyle: 'short' }).format(date)
  }

  function formatCurrency(value) {
    const amount = Number(value || 0)
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  function noteTypeClass(noteType) {
    const key = String(noteType || '').toLowerCase()
    if (key === 'public') return 'note-public'
    if (key === 'technical') return 'note-technical'
    return 'note-internal'
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
      const [repairResponse, photosResponse, notesResponse] = await Promise.all([
        api.get(`/repairs/${id}`).catch(() => null),
        api.get(`/repairs/${id}/photos`).catch(() => ({ data: [] })),
        api.get(`/repairs/${id}/notes`).catch(() => ({ data: [] }))
      ])

      if (repairResponse?.data) {
        repair.value = normalizeRepair(repairResponse.data)
      } else {
        const listResponse = await api.get('/repairs/')
        const listPayload = Array.isArray(listResponse?.data) ? listResponse.data : []
        const found = listPayload.find((entry) => Number(entry?.id || 0) === id)
        repair.value = normalizeRepair(found)
      }

      const photosPayload = Array.isArray(photosResponse?.data) ? photosResponse.data : []
      photos.value = photosPayload.map(normalizePhoto)

      const notesPayload = Array.isArray(notesResponse?.data) ? notesResponse.data : []
      notes.value = notesPayload
        .map(normalizeNote)
        .sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime())

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
      await api.put(`/repairs/${repairId.value}`, {
        status_id: Number(statusDraft.value || 1)
      })
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
      const payload = {
        diagnosis: String(editForm.value.diagnosis || '').trim() || null,
        work_performed: String(editForm.value.work_performed || '').trim() || null,
        parts_cost: Number(editForm.value.parts_cost || 0),
        labor_cost: Number(editForm.value.labor_cost || 0),
        additional_cost: Number(editForm.value.additional_cost || 0),
        discount: Number(editForm.value.discount || 0),
        total_cost: Number(editForm.value.total_cost || 0),
        paid_amount: Number(editForm.value.paid_amount || 0),
        payment_method: String(editForm.value.payment_method || '').trim() || null
      }

      await api.put(`/repairs/${repairId.value}`, payload)
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
      await api.post(`/repairs/${repairId.value}/archive`)
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
      await api.post(`/repairs/${repairId.value}/reactivate`)
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
      await api.post(`/repairs/${repairId.value}/notify`)
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
      const response = await api.post('/signatures/requests', {
        repair_id: Number(repairId.value),
        request_type: String(type || 'ingreso'),
        expires_minutes: 5
      })

      const token = response?.data?.token || response?.token || ''
      if (token) {
        signatureLink.value = `${window.location.origin}/signature/${token}`
      }
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
      const response = await api.post('/photo-requests/', null, {
        params: {
          repair_id: Number(repairId.value),
          photo_type: 'client',
          expires_minutes: 10
        }
      })

      const token = response?.data?.token || response?.token || ''
      if (token) {
        photoUploadLink.value = `${window.location.origin}/photo-upload/${token}`
      }
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
      let photoPath = ''
      
      // Intentar upload directo a Cloudinary primero
      try {
        const signatureRes = await api.post('/uploads/signature?destination=uploads')
        const sig = signatureRes.data?.data
        
        if (sig) {
          const cloudForm = new FormData()
          cloudForm.append('file', selectedFile.value)
          cloudForm.append('api_key', sig.api_key)
          cloudForm.append('timestamp', sig.timestamp)
          cloudForm.append('signature', sig.signature)
          cloudForm.append('folder', sig.folder)
          
          const cloudRes = await fetch(
            `https://api.cloudinary.com/v1_1/${sig.cloud_name}/image/upload`,
            { method: 'POST', body: cloudForm }
          )
          
          if (cloudRes.ok) {
            const cloudData = await cloudRes.json()
            photoPath = cloudData.secure_url
          }
        }
      } catch (directErr) {
        // Fallback silencioso
      }
      
      // Fallback: upload tradicional si el directo falló
      if (!photoPath) {
        const formData = new FormData()
        formData.append('file', selectedFile.value)
        const uploadResponse = await api.post('/uploads/images', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        photoPath = uploadResponse?.data?.path || uploadResponse?.data?.public_path || ''
      }
      
      if (!photoPath) {
        throw new Error('No se recibio path de la imagen.')
      }

      await api.post(`/repairs/${repairId.value}/photos`, {
        photo_url: photoPath,
        photo_type: String(newPhotoType.value || 'general'),
        caption: String(newPhotoCaption.value || '').trim() || null
      })

      selectedFile.value = null
      newPhotoCaption.value = ''
      newPhotoType.value = 'general'
      showPhotoUpload.value = false

      const photosResponse = await api.get(`/repairs/${repairId.value}/photos`)
      const photosPayload = Array.isArray(photosResponse?.data) ? photosResponse.data : []
      photos.value = photosPayload.map(normalizePhoto)
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
      await api.post(`/repairs/${repairId.value}/notes`, {
        note,
        note_type: String(newNoteType.value || 'internal')
      })

      newNote.value = ''
      newNoteType.value = 'internal'
      showNoteForm.value = false

      const notesResponse = await api.get(`/repairs/${repairId.value}/notes`)
      const notesPayload = Array.isArray(notesResponse?.data) ? notesResponse.data : []
      notes.value = notesPayload
        .map(normalizeNote)
        .sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime())
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
      const response = await api.get(`/repairs/${repairId.value}/closure-pdf`, {
        responseType: 'blob'
      })

      const blob = new Blob([response.data], { type: 'application/pdf' })
      const blobUrl = window.URL.createObjectURL(blob)
      const code = String(repair.value.repair_code || repair.value.repair_number || `OT_${repairId.value}`)
      const filename = `CIERRE_${code.replace(/[^a-zA-Z0-9._-]+/g, '_')}.pdf`

      const link = document.createElement('a')
      link.href = blobUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(blobUrl)
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
    statusOptions: STATUS_OPTIONS,
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
