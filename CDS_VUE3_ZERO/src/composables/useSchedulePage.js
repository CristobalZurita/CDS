import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@new/stores/auth'
import api, { extractErrorMessage } from '@new/services/api'

function normalizeAppointmentName(value) {
  const cleaned = String(value || '')
    .replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

  return cleaned || 'Cliente'
}

export function useSchedulePage() {
  const authStore = useAuthStore()
  const router = useRouter()

  const step = ref(1)
  const selectedDate = ref(null)
  const selectedTime = ref('')
  const agreeConditions = ref(false)
  const turnstileToken = ref('')
  const appointmentNumber = ref('')
  const isSubmitting = ref(false)
  const submissionError = ref('')

  const currentMonth = ref(new Date().getMonth())
  const currentYear = ref(new Date().getFullYear())

  const weekdays = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sab']
  const morningSlots = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30']
  const afternoonSlots = ['14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30']

  const monthYearString = computed(() => {
    const monthNames = [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    return `${monthNames[currentMonth.value]} ${currentYear.value}`
  })

  const calendarDays = computed(() => {
    const firstDay = new Date(currentYear.value, currentMonth.value, 1).getDay()
    const daysInMonth = new Date(currentYear.value, currentMonth.value + 1, 0).getDate()
    const days = []

    for (let i = 0; i < firstDay; i += 1) days.push(null)
    for (let i = 1; i <= daysInMonth; i += 1) days.push(i)

    return days
  })

  const dateSelected = computed(() => selectedDate.value !== null)
  const timeSelected = computed(() => String(selectedTime.value || '').length > 0)

  function previousMonth() {
    if (currentMonth.value === 0) {
      currentMonth.value = 11
      currentYear.value -= 1
      return
    }
    currentMonth.value -= 1
  }

  function nextMonth() {
    if (currentMonth.value === 11) {
      currentMonth.value = 0
      currentYear.value += 1
      return
    }
    currentMonth.value += 1
  }

  function isDateDisabled(day) {
    if (!day) return true
    const date = new Date(currentYear.value, currentMonth.value, day)
    const today = new Date()
    const todayAtMidnight = new Date(today.getFullYear(), today.getMonth(), today.getDate())
    return date < todayAtMidnight || date.getDay() === 0
  }

  function isSameDate(date, day) {
    if (!date || !day) return false
    return date.getFullYear() === currentYear.value &&
      date.getMonth() === currentMonth.value &&
      date.getDate() === day
  }

  function selectDate(day) {
    if (!day || isDateDisabled(day)) return
    selectedDate.value = new Date(currentYear.value, currentMonth.value, day)
  }

  function formatDate(date) {
    if (!date) return ''
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
    return new Intl.DateTimeFormat('es-CL', options).format(date)
  }

  function onVerify(token) {
    turnstileToken.value = token
    submissionError.value = ''
  }

  async function confirmAppointment() {
    if (!selectedDate.value || !selectedTime.value || !turnstileToken.value) return

    isSubmitting.value = true
    submissionError.value = ''

    try {
      const appointmentDate = new Date(selectedDate.value)
      const [hours, minutes] = selectedTime.value.split(':')
      appointmentDate.setHours(Number(hours), Number(minutes), 0, 0)

      const response = await api.post('/appointments/', {
        nombre: normalizeAppointmentName(authStore.user?.full_name),
        email: authStore.user?.email || '',
        telefono: authStore.user?.phone || '+56900000000',
        fecha: appointmentDate.toISOString(),
        mensaje: 'Cita de diagnóstico',
        turnstile_token: turnstileToken.value
      })

      appointmentNumber.value = String(response?.data?.id || `CIT-${Date.now().toString().slice(-8)}`)
      step.value = 4
    } catch (error) {
      submissionError.value = extractErrorMessage(error)
    } finally {
      isSubmitting.value = false
    }
  }

  function goHome() {
    router.push('/')
  }

  return {
    step,
    selectedDate,
    selectedTime,
    agreeConditions,
    turnstileToken,
    appointmentNumber,
    isSubmitting,
    submissionError,
    currentMonth,
    currentYear,
    weekdays,
    morningSlots,
    afternoonSlots,
    monthYearString,
    calendarDays,
    dateSelected,
    timeSelected,
    previousMonth,
    nextMonth,
    isDateDisabled,
    isSameDate,
    selectDate,
    formatDate,
    onVerify,
    confirmAppointment,
    goHome
  }
}
