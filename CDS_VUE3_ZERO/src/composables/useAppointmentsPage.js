import { computed, onMounted, ref } from 'vue'
import api, { extractErrorMessage } from '@new/services/api'

function normalizeAppointment(entry) {
  return {
    id: entry?.id,
    nombre: String(entry?.nombre || ''),
    email: String(entry?.email || ''),
    telefono: String(entry?.telefono || ''),
    fecha: entry?.fecha || null,
    mensaje: String(entry?.mensaje || ''),
    estado: String(entry?.estado || 'pendiente').toLowerCase()
  }
}

export function useAppointmentsPage() {
  const appointments = ref([])
  const loading = ref(false)
  const error = ref('')
  const filter = ref('all')

  const filteredAppointments = computed(() => {
    if (filter.value === 'all') return appointments.value
    return appointments.value.filter((item) => item.estado === filter.value)
  })

  function formatDate(value) {
    if (!value) return '—'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '—'
    return new Intl.DateTimeFormat('es-CL', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(date)
  }

  function formatTime(value) {
    if (!value) return '—'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '—'
    return new Intl.DateTimeFormat('es-CL', { hour: '2-digit', minute: '2-digit' }).format(date)
  }

  function getStatusLabel(status) {
    const labels = {
      pendiente: 'Pendiente',
      confirmado: 'Confirmada',
      cancelado: 'Cancelada'
    }
    return labels[status] || status
  }

  async function loadAppointments() {
    loading.value = true
    error.value = ''

    try {
      const response = await api.get('/appointments/')
      const payload = Array.isArray(response?.data) ? response.data : []
      appointments.value = payload.map(normalizeAppointment)
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      appointments.value = []
    } finally {
      loading.value = false
    }
  }

  async function updateStatus(appointment, estado) {
    loading.value = true
    error.value = ''

    try {
      await api.patch(`/appointments/${appointment.id}`, { estado })
      await loadAppointments()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function confirmAppointment(appointment) {
    await updateStatus(appointment, 'confirmado')
  }

  async function cancelAppointment(appointment) {
    await updateStatus(appointment, 'cancelado')
  }

  async function deleteAppointment(appointment) {
    loading.value = true
    error.value = ''

    try {
      await api.delete(`/appointments/${appointment.id}`)
      await loadAppointments()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  onMounted(loadAppointments)

  return {
    appointments,
    loading,
    error,
    filter,
    filteredAppointments,
    formatDate,
    formatTime,
    getStatusLabel,
    loadAppointments,
    confirmAppointment,
    cancelAppointment,
    deleteAppointment
  }
}
