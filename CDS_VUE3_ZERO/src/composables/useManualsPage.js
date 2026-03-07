import { computed, onMounted, ref } from 'vue'
import api, { extractErrorMessage } from '@new/services/api'

function normalizeManual(entry) {
  return {
    id: Number(entry?.id || 0),
    instrument_id: Number(entry?.instrument_id || 0),
    title: String(entry?.title || ''),
    source: String(entry?.source || 'internal'),
    url: String(entry?.url || ''),
    file_path: String(entry?.file_path || ''),
    created_at: entry?.created_at || null,
    updated_at: entry?.updated_at || null
  }
}

function normalizeInstrument(entry) {
  return {
    id: Number(entry?.id || 0),
    name: String(entry?.name || ''),
    brand: String(entry?.brand || ''),
    model: String(entry?.model || '')
  }
}

function baseCreateForm() {
  return {
    instrument_id: '',
    title: '',
    source: 'internal',
    url: '',
    file_path: ''
  }
}

function baseDraft() {
  return {
    title: '',
    source: 'internal',
    url: ''
  }
}

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

function resolveUrl(path) {
  const value = String(path || '').trim()
  if (!value) return ''
  if (value.startsWith('http://') || value.startsWith('https://')) return value
  if (value.startsWith('/')) return `${API_HOST}${value}`
  return `${API_HOST}/${value}`
}

export function useManualsPage() {
  const manuals = ref([])
  const instruments = ref([])
  const loading = ref(false)
  const error = ref('')

  const showForm = ref(false)
  const form = ref(baseCreateForm())

  const editingId = ref(0)
  const draft = ref(baseDraft())

  const filteredManuals = computed(() => {
    return [...manuals.value].sort((a, b) => {
      const dateA = new Date(a.updated_at || a.created_at || 0).getTime()
      const dateB = new Date(b.updated_at || b.created_at || 0).getTime()
      return dateB - dateA
    })
  })

  function resetForm() {
    form.value = baseCreateForm()
  }

  function resetDraft() {
    editingId.value = 0
    draft.value = baseDraft()
  }

  function toggleForm() {
    showForm.value = !showForm.value
    if (!showForm.value) resetForm()
  }

  function formatDate(value) {
    if (!value) return '—'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '—'
    return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium', timeStyle: 'short' }).format(date)
  }

  function getInstrumentName(instrumentId) {
    const id = Number(instrumentId || 0)
    const instrument = instruments.value.find((item) => item.id === id)
    if (!instrument) return '—'

    const model = instrument.model || instrument.name
    const brand = instrument.brand ? `${instrument.brand} ` : ''
    return `${brand}${model}`.trim() || `Instrumento #${id}`
  }

  function getManualLink(manual) {
    if (manual?.url) return resolveUrl(manual.url)
    if (manual?.file_path) return resolveUrl(manual.file_path)
    return ''
  }

  async function loadInstruments() {
    try {
      const response = await api.get('/instruments/')
      const payload = Array.isArray(response?.data) ? response.data : []
      instruments.value = payload.map(normalizeInstrument)
    } catch {
      instruments.value = []
    }
  }

  async function loadManuals() {
    loading.value = true
    error.value = ''

    try {
      const response = await api.get('/manuals/')
      const payload = Array.isArray(response?.data) ? response.data : []
      manuals.value = payload.map(normalizeManual)
    } catch (requestError) {
      manuals.value = []
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function createManual() {
    error.value = ''

    const payload = {
      instrument_id: Number(form.value.instrument_id || 0),
      title: String(form.value.title || '').trim(),
      source: String(form.value.source || 'internal').trim() || 'internal',
      url: String(form.value.url || '').trim() || null,
      file_path: String(form.value.file_path || '').trim() || null
    }

    if (!payload.instrument_id || payload.title.length < 2) {
      error.value = 'Completa instrumento y titulo (min 2 caracteres).'
      return
    }

    loading.value = true

    try {
      await api.post('/manuals/', payload)
      showForm.value = false
      resetForm()
      await loadManuals()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  function startEdit(manual) {
    editingId.value = Number(manual?.id || 0)
    draft.value = {
      title: String(manual?.title || ''),
      source: String(manual?.source || 'internal'),
      url: String(manual?.url || '')
    }
  }

  async function saveManual(manual) {
    const id = Number(manual?.id || 0)
    if (!id) return

    loading.value = true
    error.value = ''

    try {
      await api.patch(`/manuals/${id}`, {
        title: String(draft.value.title || '').trim(),
        source: String(draft.value.source || 'internal').trim() || 'internal',
        url: String(draft.value.url || '').trim() || null
      })
      resetDraft()
      await loadManuals()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function deleteManual(manual) {
    const id = Number(manual?.id || 0)
    if (!id) return

    loading.value = true
    error.value = ''

    try {
      await api.delete(`/manuals/${id}`)
      if (editingId.value === id) resetDraft()
      await loadManuals()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  onMounted(async () => {
    await Promise.all([loadInstruments(), loadManuals()])
  })

  return {
    manuals: filteredManuals,
    instruments,
    loading,
    error,
    showForm,
    form,
    editingId,
    draft,
    formatDate,
    getInstrumentName,
    getManualLink,
    toggleForm,
    resetDraft,
    loadManuals,
    createManual,
    startEdit,
    saveManual,
    deleteManual
  }
}
