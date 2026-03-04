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
            <button class="btn-secondary" @click="emit('cancel')">
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
            <button class="btn-secondary" @click="emit('cancel')">
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

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.schedule-page {
  min-height: 100vh;
  padding: clamp(1rem, 3vw, 2rem);
  background:
    radial-gradient(circle at top left, color-mix(in srgb, var(--color-primary) 18%, transparent) 0, transparent 30%),
    linear-gradient(180deg, #f8f4ec 0%, #eee7db 100%);
}

.schedule-container {
  width: min(100%, 1080px);
  margin: 0 auto;
  display: grid;
  gap: var(--spacer-md);
}

.schedule-header,
.schedule-content,
.schedule-step,
.confirmation-card,
.timeslot-group,
.calendar-container {
  padding: var(--spacer-md);
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(211, 208, 195, 0.8);
  border-radius: 22px;
  box-shadow: var(--shadow-sm);
}

.schedule-header {
  text-align: center;
}

.schedule-header h1,
.schedule-step h2,
.timeslot-group h3,
.calendar-header h3 {
  margin: 0;
  color: var(--color-dark);
  font-weight: 700;
}

.schedule-header p,
.step-description,
.confirmation-info p,
.small-text,
.schedule-error {
  margin: 0;
  color: var(--color-dark);
  opacity: 0.78;
  font-size: var(--text-sm);
}

.progress-bar {
  display: grid;
  gap: var(--spacer-sm);
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.progress-step {
  display: grid;
  justify-items: center;
  gap: 0.45rem;
  padding: 0.85rem;
  border: 1px solid var(--color-light);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.8);
  color: var(--color-dark);
}

.progress-step.active {
  border-color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 12%, var(--color-white) 88%);
}

.step-number {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 999px;
  background: var(--color-dark);
  color: var(--color-white);
  font-weight: 700;
}

.progress-step.active .step-number {
  background: var(--color-primary);
}

.step-label {
  font-size: var(--text-sm);
  font-weight: 700;
}

.schedule-content {
  display: grid;
}

.schedule-step {
  display: grid;
  gap: var(--spacer-md);
}

.calendar-container {
  display: grid;
  gap: var(--spacer-sm);
  padding: 1rem;
  background: color-mix(in srgb, var(--color-white) 90%, var(--color-light) 10%);
}

.calendar-header,
.step-actions,
.confirmation-section,
.timeslots {
  display: flex;
  gap: var(--spacer-sm);
  flex-wrap: wrap;
}

.calendar-header,
.step-actions,
.confirmation-section {
  align-items: center;
  justify-content: space-between;
}

.calendar-nav,
.btn-primary,
.btn-secondary,
.timeslot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  padding: 0.7rem 1rem;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-base);
  text-decoration: none;
}

.calendar-nav,
.btn-secondary,
.timeslot {
  border: 1px solid var(--color-light);
  background: var(--color-white);
  color: var(--color-dark);
}

.btn-primary {
  border: 0;
  background: var(--color-primary);
  color: var(--color-white);
}

.calendar-nav:hover,
.btn-primary:hover:not(:disabled),
.btn-secondary:hover,
.timeslot:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: wait;
}

.calendar-weekdays,
.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 0.45rem;
}

.weekday,
.calendar-day {
  display: grid;
  place-items: center;
  min-height: 48px;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
}

.weekday {
  color: var(--color-dark);
  font-weight: 700;
}

.calendar-day {
  border: 1px solid transparent;
  background: rgba(255, 255, 255, 0.85);
  color: var(--color-dark);
  cursor: pointer;
}

.calendar-day.empty,
.calendar-day.disabled {
  opacity: 0.35;
  cursor: default;
}

.calendar-day.selected {
  border-color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 18%, var(--color-white) 82%);
  font-weight: 700;
}

.timeslots-container {
  display: grid;
  gap: var(--spacer-md);
}

.timeslot-group {
  display: grid;
  gap: var(--spacer-sm);
}

.timeslot.selected {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: var(--color-white);
}

.confirmation-card {
  display: grid;
  gap: var(--spacer-sm);
}

.confirmation-section {
  padding-bottom: 0.65rem;
  border-bottom: 1px solid var(--color-light);
}

.label {
  color: var(--color-dark);
  opacity: 0.72;
  font-size: var(--text-sm);
}

.value {
  color: var(--color-dark);
  font-weight: 700;
}

.confirmation-info {
  display: grid;
  gap: 0.5rem;
  padding: 0.85rem 0.95rem;
  border-radius: var(--radius-sm);
  background: color-mix(in srgb, var(--color-white) 90%, var(--color-light) 10%);
}

.checkbox-container {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  color: var(--color-dark);
  font-size: var(--text-sm);
  font-weight: 600;
}

.checkbox-container input {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
}

.schedule-error {
  padding: 0.8rem 0.95rem;
  border-radius: var(--radius-sm);
  background: color-mix(in srgb, var(--color-white) 86%, var(--color-danger) 14%);
}

.success-step {
  text-align: center;
}

.success-icon {
  display: grid;
  place-items: center;
  width: 84px;
  height: 84px;
  margin: 0 auto;
  border-radius: 999px;
  background: var(--color-primary);
  color: var(--color-white);
  font-size: 2.25rem;
  font-weight: 700;
}

.success-message {
  margin: 0;
  color: var(--color-dark);
  font-size: var(--text-base);
}

.monospace {
  font-family: monospace;
}

@include media-breakpoint-down(md) {
  .progress-bar,
  .calendar-weekdays,
  .calendar-days {
    grid-template-columns: repeat(7, minmax(0, 1fr));
  }

  .calendar-header,
  .step-actions,
  .confirmation-section,
  .timeslots {
    flex-direction: column;
    align-items: stretch;
  }

  .btn-primary,
  .btn-secondary,
  .calendar-nav,
  .timeslot {
    width: 100%;
  }
}
</style>
