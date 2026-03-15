import { computed, ref } from 'vue'
import api, { extractErrorMessage } from '@/services/api'

function normalizeRepair(entry) {
  return {
    id: Number(entry?.id || 0),
    repair_code: String(entry?.repair_code || entry?.repair_number || ''),
    repair_number: String(entry?.repair_number || ''),
    status_id: Number(entry?.status_id || 0),
    problem_reported: String(entry?.problem_reported || ''),
    created_at: entry?.created_at || null
  }
}

function baseRepairForm() {
  return {
    device_id: '',
    problem_reported: '',
    priority: 2,
    paid_amount: 20000,
    payment_method: 'cash',
    group_with_ot: false,
    ot_parent_id: ''
  }
}

export function useRepairManagement({ selectedClientId, contextLoading, error, devices, onRepairCreated }) {
  const repairs = ref([])
  const repairForm = ref(baseRepairForm())
  const showRepairForm = ref(false)

  const sortedRepairs = computed(() => {
    return [...repairs.value].sort((a, b) => {
      const dateA = new Date(a.created_at || 0).getTime()
      const dateB = new Date(b.created_at || 0).getTime()
      return dateB - dateA
    })
  })

  function resetRepairForm() {
    repairForm.value = baseRepairForm()
  }

  function toggleRepairForm() {
    showRepairForm.value = !showRepairForm.value
    if (showRepairForm.value) resetRepairForm()
  }

  async function loadRepairs(clientId) {
    const response = await api.get(`/clients/${clientId}/repairs`).catch(() => ({ data: [] }))
    const payload = Array.isArray(response?.data) ? response.data : []
    repairs.value = payload.map(normalizeRepair)
  }

  async function createRepairForSelectedClient() {
    const clientId = Number(selectedClientId.value)
    if (!clientId) return

    error.value = ''

    const problemReported = String(repairForm.value.problem_reported || '').trim()
    if (!problemReported) {
      error.value = 'El problema reportado es obligatorio.'
      return
    }

    const payload = {
      client_id: clientId,
      device_id: repairForm.value.device_id ? Number(repairForm.value.device_id) : undefined,
      model: devices.value.find((d) => d.id === Number(repairForm.value.device_id))?.model || 'Equipo',
      problem_reported: problemReported,
      priority: Number(repairForm.value.priority || 2),
      paid_amount: Number(repairForm.value.paid_amount || 0),
      payment_method: String(repairForm.value.payment_method || 'cash')
    }

    if (repairForm.value.group_with_ot && repairForm.value.ot_parent_id) {
      payload.ot_parent_id = Number(repairForm.value.ot_parent_id)
    }

    contextLoading.value = true

    try {
      await api.post('/repairs/', payload)
      showRepairForm.value = false
      resetRepairForm()
      if (onRepairCreated) await onRepairCreated()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      contextLoading.value = false
    }
  }

  function clearRepairs() {
    repairs.value = []
  }

  return {
    repairs: sortedRepairs,
    repairForm,
    showRepairForm,
    loadRepairs,
    clearRepairs,
    resetRepairForm,
    toggleRepairForm,
    createRepairForSelectedClient
  }
}
