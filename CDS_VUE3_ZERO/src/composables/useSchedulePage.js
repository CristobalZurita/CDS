import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api, { extractErrorMessage } from '@/services/api'

function normalizeAppointmentName(value) {
  const cleaned = String(value || '')
    .replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

  return cleaned || 'Cliente'
}

function normalizeScheduleContact(source) {
  return {
    fullName: String(source?.full_name || source?.fullName || '').trim(),
    email: String(source?.email || '').trim(),
    phone: String(source?.phone || source?.telefono || '').trim(),
  }
}

function formatAppointmentNumber(value) {
  const raw = String(value || '').trim()
  if (!raw) return `CIT-${Date.now().toString().slice(-8)}`
  if (raw.toUpperCase().startsWith('CIT-')) return raw.toUpperCase()
  return `CIT-${raw.padStart(6, '0')}`
}

export function useSchedulePage() {
  const authStore = useAuthStore()
  const router = useRouter()

  const step = ref(1)
  const selectedDate = ref(null)
  const selectedTime = ref('')
  const occupiedSlots = ref([])
  const agreeConditions = ref(false)
  const turnstileToken = ref('')
  const turnstileRenderKey = ref(0)
  const appointmentNumber = ref('')
  const isSubmitting = ref(false)
  const isLoadingAvailability = ref(false)
  const submissionError = ref('')
  const availabilityError = ref('')
  const contactDetails = ref(normalizeScheduleContact(authStore.user))

  const currentMonth = ref(new Date().getMonth())
  const currentYear = ref(new Date().getFullYear())

  const weekdays = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sab']
  const morningSlots = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30']
  const afternoonSlots = ['14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30']
  const allSlots = [...morningSlots, ...afternoonSlots]

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
  const contactDetailsComplete = computed(() => {
    const email = String(contactDetails.value.email || '').trim()
    const phone = String(contactDetails.value.phone || '').trim()
    return Boolean(email && phone)
  })
  const timeSelected = computed(() => {
    return String(selectedTime.value || '').length > 0 && !isTimeSlotUnavailable(selectedTime.value)
  })

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
    return date < todayAtMidnight || [0, 6].includes(date.getDay())
  }

  function isSameDate(date, day) {
    if (!date || !day) return false
    return date.getFullYear() === currentYear.value &&
      date.getMonth() === currentMonth.value &&
      date.getDate() === day
  }

  function selectDate(day) {
    if (!day || isDateDisabled(day)) return
    const nextDate = new Date(currentYear.value, currentMonth.value, day)
    const previous = selectedDate.value ? selectedDate.value.getTime() : null
    selectedDate.value = nextDate
    selectedTime.value = ''
    availabilityError.value = ''
    submissionError.value = ''
    if (previous !== nextDate.getTime()) {
      resetTurnstile()
    }
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

  function resetTurnstile() {
    turnstileToken.value = ''
    turnstileRenderKey.value += 1
  }

  function formatAvailabilityDate(date) {
    if (!(date instanceof Date)) return ''
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  function isTimeSlotUnavailable(time) {
    return occupiedSlots.value.includes(String(time || ''))
  }

  function mergeContactDetails(source) {
    const nextContact = normalizeScheduleContact(source)
    contactDetails.value = {
      fullName: nextContact.fullName || contactDetails.value.fullName,
      email: nextContact.email || contactDetails.value.email,
      phone: nextContact.phone || contactDetails.value.phone,
    }
  }

  async function hydrateContactDetails() {
    mergeContactDetails(authStore.user)

    if (contactDetailsComplete.value) return

    try {
      const refreshedUser = await authStore.checkAuth()
      mergeContactDetails(refreshedUser || authStore.user)
    } catch {
      // Ignore session refresh failures here; the route guard already handles auth redirects.
    }

    if (contactDetailsComplete.value) return

    try {
      const response = await api.get('/client/profile')
      mergeContactDetails(response?.data || {})
    } catch {
      // Keep the schedule page usable even if profile hydration fails.
    }
  }

  async function loadAvailability(date = selectedDate.value) {
    if (!(date instanceof Date)) {
      occupiedSlots.value = []
      availabilityError.value = ''
      return
    }

    isLoadingAvailability.value = true
    availabilityError.value = ''

    try {
      const response = await api.get('/appointments/public-availability', {
        params: { date: formatAvailabilityDate(date) }
      })
      const nextSlots = Array.isArray(response?.data?.occupied_slots)
        ? response.data.occupied_slots.filter((slot) => allSlots.includes(slot))
        : []
      occupiedSlots.value = nextSlots

      if (nextSlots.includes(selectedTime.value)) {
        selectedTime.value = ''
      }
    } catch (error) {
      occupiedSlots.value = []
      availabilityError.value = extractErrorMessage(error)
    } finally {
      isLoadingAvailability.value = false
    }
  }

  async function confirmAppointment() {
    if (!selectedDate.value || !selectedTime.value || !turnstileToken.value) return

    if (!contactDetailsComplete.value) {
      submissionError.value = 'Completa tu correo y teléfono antes de agendar la cita.'
      return
    }

    if (isTimeSlotUnavailable(selectedTime.value)) {
      submissionError.value = 'Ese horario ya fue tomado. Selecciona otro bloque disponible.'
      step.value = 2
      resetTurnstile()
      return
    }

    isSubmitting.value = true
    submissionError.value = ''

    try {
      const appointmentDate = new Date(selectedDate.value)
      const [hours, minutes] = selectedTime.value.split(':')
      appointmentDate.setHours(Number(hours), Number(minutes), 0, 0)

      const response = await api.post('/appointments/', {
        nombre: normalizeAppointmentName(contactDetails.value.fullName),
        email: contactDetails.value.email || '',
        telefono: contactDetails.value.phone || '',
        fecha: appointmentDate.toISOString(),
        mensaje: 'Cita de diagnóstico',
        turnstile_token: turnstileToken.value
      })

      appointmentNumber.value = formatAppointmentNumber(response?.data?.id)
      step.value = 4
    } catch (error) {
      submissionError.value = extractErrorMessage(error)
      resetTurnstile()
    } finally {
      isSubmitting.value = false
    }
  }

  function goHome() {
    router.push('/')
  }

  onMounted(() => {
    hydrateContactDetails()
  })

  watch(selectedDate, (date) => {
    loadAvailability(date)
  })

  watch(() => authStore.user, (nextUser) => {
    mergeContactDetails(nextUser)
  }, { deep: true })

  watch(selectedTime, (time, previous) => {
    if (time && time !== previous) {
      submissionError.value = ''
    }
    if (time !== previous && turnstileToken.value) {
      resetTurnstile()
    }
  })

  return {
    step,
    selectedDate,
    selectedTime,
    occupiedSlots,
    agreeConditions,
    turnstileToken,
    turnstileRenderKey,
    appointmentNumber,
    isSubmitting,
    isLoadingAvailability,
    submissionError,
    availabilityError,
    contactDetailsComplete,
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
    isTimeSlotUnavailable,
    onVerify,
    confirmAppointment,
    goHome
  }
}
