<template>
  <div class="schedule-page">
    <div class="schedule-container">
      <!-- Header -->
      <div class="schedule-header">
        <h1>Agendar Cita de Reparación</h1>
        <p>Selecciona el mejor horario para tu equipo</p>
      </div>

      <!-- Progress -->
      <div class="progress-bar">
        <div class="progress-step active">
          <span class="step-number">1</span>
          <span class="step-label">Fecha</span>
        </div>
        <div class="progress-step" :class="{ active: dateSelected }">
          <span class="step-number">2</span>
          <span class="step-label">Hora</span>
        </div>
        <div class="progress-step" :class="{ active: timeSelected }">
          <span class="step-number">3</span>
          <span class="step-label">Confirmación</span>
        </div>
      </div>

      <!-- Main Content -->
      <div class="schedule-content">
        <!-- Step 1: Date Selection -->
        <div v-if="step === 1" class="schedule-step">
          <h2>Selecciona una Fecha</h2>
          <p class="step-description">
            Elige el día que prefieras para traer tu instrumento
          </p>

          <div class="calendar-container">
            <div class="calendar-header">
              <button class="calendar-nav" data-testid="schedule-prev-month" @click="previousMonth">←</button>
              <h3>{{ monthYearString }}</h3>
              <button class="calendar-nav" data-testid="schedule-next-month" @click="nextMonth">→</button>
            </div>

            <div class="calendar-weekdays">
              <div class="weekday" v-for="day in weekdays" :key="day">
                {{ day }}
              </div>
            </div>

            <div class="calendar-days">
              <div
                v-for="day in calendarDays"
                :key="day"
                class="calendar-day"
                :class="{
                  empty: !day,
                  disabled: isDateDisabled(day),
                  selected: isSameDate(selectedDate, day)
                }"
                data-testid="schedule-day"
                :data-day="day || ''"
                :data-disabled="isDateDisabled(day) ? 'true' : 'false'"
                @click="selectDate(day)"
              >
                {{ day }}
              </div>
            </div>
          </div>

          <div class="step-actions">
            <button class="btn-secondary" @click="$emit('cancel')">
              Cancelar
            </button>
            <button
              class="btn-primary"
              data-testid="schedule-date-next"
              :disabled="!dateSelected"
              @click="step = 2"
            >
              Siguiente →
            </button>
          </div>
        </div>

        <!-- Step 2: Time Selection -->
        <div v-if="step === 2" class="schedule-step">
          <h2>Selecciona una Hora</h2>
          <p class="step-description">
            Fecha seleccionada: {{ formatDate(selectedDate) }}
          </p>

          <div class="timeslots-container">
            <div class="timeslot-group">
              <h3>Mañana (09:00 - 12:00)</h3>
              <div class="timeslots">
                <button
                  v-for="time in morningSlots"
                  :key="time"
                  class="timeslot"
                  :class="{ selected: selectedTime === time }"
                  data-testid="schedule-time-slot"
                  :data-time="time"
                  @click="selectedTime = time"
                >
                  {{ time }}
                </button>
              </div>
            </div>

            <div class="timeslot-group">
              <h3>Tarde (14:00 - 18:00)</h3>
              <div class="timeslots">
                <button
                  v-for="time in afternoonSlots"
                  :key="time"
                  class="timeslot"
                  :class="{ selected: selectedTime === time }"
                  data-testid="schedule-time-slot"
                  :data-time="time"
                  @click="selectedTime = time"
                >
                  {{ time }}
                </button>
              </div>
            </div>
          </div>

          <div class="step-actions">
            <button class="btn-secondary" data-testid="schedule-time-back" @click="step = 1">
              ← Atrás
            </button>
            <button
              class="btn-primary"
              data-testid="schedule-time-next"
              :disabled="!timeSelected"
              @click="step = 3"
            >
              Siguiente →
            </button>
          </div>
        </div>

        <!-- Step 3: Confirmation -->
        <div v-if="step === 3" class="schedule-step">
          <h2>Confirmar Cita</h2>

          <div class="confirmation-card">
            <div class="confirmation-section">
              <span class="label">Fecha:</span>
              <span class="value">{{ formatDate(selectedDate) }}</span>
            </div>

            <div class="confirmation-section">
              <span class="label">Hora:</span>
              <span class="value">{{ selectedTime }}</span>
            </div>

            <div class="confirmation-section">
              <span class="label">Instrumento:</span>
              <span class="value">
                {{ quotationStore.selectedInstrument?.name || 'No seleccionado' }}
              </span>
            </div>

            <div class="confirmation-info">
              <p>
                <strong>⏱️ Duración estimada:</strong> 20-30 minutos para diagnóstico
              </p>
              <p>
                <strong>📍 Ubicación:</strong> Tu taller de reparaciones
              </p>
              <p>
                <strong>⚠️ Importante:</strong> Trae el instrumento con el problema
                y todos los accesorios asociados.
              </p>
            </div>

            <label class="checkbox-container">
              <input v-model="agreeConditions" type="checkbox" />
              <span>Acepto los términos y condiciones de esta cita</span>
            </label>
          </div>

          <TurnstileWidget @verify="onVerify" />

          <p v-if="submissionError" class="schedule-error" data-testid="schedule-error">
            {{ submissionError }}
          </p>

          <div class="step-actions">
            <button class="btn-secondary" @click="step = 2">
              ← Atrás
            </button>
            <button
              class="btn-primary"
              data-testid="schedule-confirm"
              :disabled="isSubmitting || !agreeConditions || !turnstileToken"
              @click="confirmAppointment"
            >
              {{ isSubmitting ? 'Confirmando...' : 'Confirmar Cita' }}
            </button>
          </div>
        </div>

        <!-- Step 4: Success -->
        <div v-if="step === 4" class="schedule-step success-step" data-testid="schedule-success">
          <div class="success-icon">✓</div>
          <h2>¡Cita Confirmada!</h2>
          <p class="success-message">
            Tu cita ha sido agendada exitosamente.
          </p>

          <div class="confirmation-card">
            <div class="confirmation-section">
              <span class="label">Número de cita:</span>
              <span class="value monospace" data-testid="schedule-appointment-number">{{ appointmentNumber }}</span>
            </div>

            <div class="confirmation-section">
              <span class="label">Fecha y hora:</span>
              <span class="value">
                {{ formatDate(selectedDate) }} a las {{ selectedTime }}
              </span>
            </div>

            <p class="small-text">
              Se ha enviado un email de confirmación a tu correo. Recuerda que puedes
              cancelar la cita hasta 24 horas antes.
            </p>
          </div>

          <div class="step-actions">
            <button class="btn-secondary" @click="$emit('cancel')">
              Volver al Inicio
            </button>
            <router-link to="/dashboard" class="btn-primary">
              Ir al Dashboard
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuotationStore } from '@/stores/quotation'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'
import TurnstileWidget from '@/vue/components/widgets/TurnstileWidget.vue'

const quotationStore = useQuotationStore()
const authStore = useAuthStore()

// State
const step = ref(1)
const selectedDate = ref(null)
const selectedTime = ref(null)
const agreeConditions = ref(false)
const appointmentNumber = ref('')
const turnstileToken = ref('')
const submissionError = ref('')
const isSubmitting = ref(false)

// Calendar
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

  for (let i = 0; i < firstDay; i++) {
    days.push(null)
  }

  for (let i = 1; i <= daysInMonth; i++) {
    days.push(i)
  }

  return days
})

const dateSelected = computed(() => selectedDate.value !== null)
const timeSelected = computed(() => selectedTime.value !== null)

// Methods
const previousMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

const nextMonth = () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

const isDateDisabled = (day) => {
  if (!day) return true
  const today = new Date()
  const date = new Date(currentYear.value, currentMonth.value, day)
  // No puedes agendar en el pasado o en domingos
  return date < today || date.getDay() === 0
}

const isSameDate = (date, day) => {
  if (!date || !day) return false
  return date.getFullYear() === currentYear.value &&
         date.getMonth() === currentMonth.value &&
         date.getDate() === day
}

const selectDate = (day) => {
  if (!day || isDateDisabled(day)) return
  selectedDate.value = new Date(currentYear.value, currentMonth.value, day)
}

const formatDate = (date) => {
  if (!date) return ''
  const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
  return new Intl.DateTimeFormat('es-CL', options).format(date)
}

const normalizeAppointmentName = (value) => {
  const cleaned = String(value || '')
    .replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

  return cleaned || 'Cliente'
}

const confirmAppointment = async () => {
  if (!turnstileToken.value) {
    return
  }
  submissionError.value = ''
  isSubmitting.value = true
  appointmentNumber.value = 'CIT-' + Date.now().toString().slice(-8)

  try {
    console.log('Cita confirmada:', {
      number: appointmentNumber.value,
      date: selectedDate.value,
      time: selectedTime.value,
      instrument: quotationStore.selectedInstrument
    })

    const appointmentDate = new Date(selectedDate.value)
    const [hours, minutes] = selectedTime.value.split(':')
    appointmentDate.setHours(parseInt(hours), parseInt(minutes), 0, 0)

    const response = await api.post('/appointments/', {
      nombre: normalizeAppointmentName(authStore.user?.full_name),
      email: authStore.user?.email || '',
      telefono: authStore.user?.phone || '+56900000000',
      fecha: appointmentDate.toISOString(),
      mensaje: quotationStore.selectedInstrument?.name
        ? `Instrumento: ${quotationStore.selectedInstrument.name}`
        : 'Cita de diagnóstico',
      turnstile_token: turnstileToken.value
    })

    console.log('Cita guardada en backend:', response.data)
    step.value = 4
  } catch (error) {
    console.warn('Error guardando cita en backend:', error)
    submissionError.value = error?.response?.data?.detail || 'No se pudo agendar la cita. Intenta nuevamente.'
  } finally {
    isSubmitting.value = false
  }
}

const onVerify = (token) => {
  turnstileToken.value = token
}

// Emit
const emit = defineEmits(['cancel'])
</script>
