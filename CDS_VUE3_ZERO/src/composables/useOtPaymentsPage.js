import { onMounted, ref } from 'vue'
import api, { extractErrorMessage } from '@/services/api'

function resolveApiHost() {
  const base = String(import.meta.env.VITE_API_URL || '/api/v1')
  if (!base.includes('/api/')) return ''
  return base.split('/api/')[0]
}

function normalizeStatus(value) {
  return String(value || '').trim().toLowerCase()
}

export function useOtPaymentsPage() {
  const requests = ref([])
  const loading = ref(false)
  const error = ref('')
  const busyIds = ref(new Set())
  const forms = ref({})
  const filesByRequest = ref({})

  const isBusy = (requestId) => busyIds.value.has(Number(requestId))

  function setBusy(requestId, value) {
    const id = Number(requestId)
    const next = new Set(busyIds.value)
    if (value) {
      next.add(id)
    } else {
      next.delete(id)
    }
    busyIds.value = next
  }

  function canSubmitProof(status) {
    return ['pending_payment', 'requested', 'proof_submitted'].includes(normalizeStatus(status))
  }

  function ensureForm(request) {
    if (!forms.value[request.id]) {
      forms.value[request.id] = {
        amount: Number(request.requested_amount || request.total_items_amount || 0),
        deposit_reference: '',
        client_notes: ''
      }
    }
  }

  function toApiPath(path) {
    const value = String(path || '')
    if (!value) return '#'
    if (value.startsWith('http://') || value.startsWith('https://')) return value

    if (value.startsWith('/api/')) {
      return value
    }

    const host = resolveApiHost()
    if (!host) return value
    return `${host}${value.startsWith('/') ? '' : '/'}${value}`
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

  function formatDate(value) {
    if (!value) return 'SIN_FECHA'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return 'SIN_FECHA'
    return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium' }).format(date)
  }

  function onFileSelected(requestId, event) {
    const file = event?.target?.files?.[0] || null
    filesByRequest.value[requestId] = file
  }

  async function uploadProofImage(file) {
    if (!file) return null
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/uploads/images', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    return response?.data?.path || null
  }

  async function loadRequests() {
    loading.value = true
    error.value = ''

    try {
      const response = await api.get('/client/purchase-requests')
      requests.value = Array.isArray(response?.data) ? response.data : []
      requests.value.forEach(ensureForm)
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      requests.value = []
    } finally {
      loading.value = false
    }
  }

  async function submitProof(request) {
    setBusy(request.id, true)
    error.value = ''

    try {
      ensureForm(request)
      const form = forms.value[request.id]
      const file = filesByRequest.value[request.id] || null
      const proofPath = await uploadProofImage(file)

      await api.post(`/client/purchase-requests/${request.id}/deposit-proof`, {
        amount: Number(form.amount || request.requested_amount || request.total_items_amount || 0),
        deposit_reference: form.deposit_reference || null,
        client_notes: form.client_notes || null,
        proof_path: proofPath || null,
        deposited_at: new Date().toISOString()
      })

      filesByRequest.value[request.id] = null
      forms.value[request.id].deposit_reference = ''
      forms.value[request.id].client_notes = ''

      await loadRequests()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      setBusy(request.id, false)
    }
  }

  onMounted(loadRequests)

  return {
    requests,
    loading,
    error,
    forms,
    isBusy,
    canSubmitProof,
    toApiPath,
    formatCurrency,
    formatDate,
    onFileSelected,
    loadRequests,
    submitProof
  }
}
