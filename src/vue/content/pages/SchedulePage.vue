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

<style lang="scss" scoped>
@use "@/scss/_core.scss" as *;

.schedule-page {
  min-height: 100vh;
  background: linear-gradient(135deg, $color-indigo-legacy 0%, $color-purple-legacy 100%);
  padding: $spacer-xl $spacer-md;
}

.schedule-container {
  max-width: 900px;
  margin: 0 auto;
  background: $color-white;
  border-radius: $border-radius-xl;
  padding: $spacer-xxl $spacer-xl;
  box-shadow: $shadow-xl;
}

.schedule-header {
  text-align: center;
  margin-bottom: $spacer-xl;
}

.schedule-header h1 {
  margin: 0 0 $spacer-sm 0;
  color: $text-color;
  font-size: $h2-size;
}

.schedule-header p {
  margin: 0;
  color: $text-color-muted;
  font-size: $text-lg;
}

/* Progress Bar */
.progress-bar {
  display: flex;
  justify-content: space-around;
  margin-bottom: $spacer-xl;
  gap: $spacer-md;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacer-sm;
  opacity: 0.5;
  transition: $transition-fast;
}

.progress-step.active {
  opacity: 1;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: $border-radius-pill;
  background: $light-2;
  color: $light-7;
  font-weight: $fw-semibold;
  font-size: $text-lg;
}

.progress-step.active .step-number {
  background: linear-gradient(135deg, $color-indigo-legacy, $color-purple-legacy);
  color: $color-white;
}

.step-label {
  font-size: $text-sm;
  color: $light-6;
  font-weight: $fw-medium;
}

.progress-step.active .step-label {
  color: $text-color;
  font-weight: $fw-semibold;
}

/* Schedule Content */
.schedule-content {
  min-height: 500px;
}

.schedule-step {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.schedule-step h2 {
  margin: 0 0 $spacer-sm 0;
  color: $text-color;
  font-size: $h4-size;
}

.step-description {
  margin: 0 0 $spacer-xl 0;
  color: $light-6;
  font-size: $text-base;
}

/* Calendar */
.calendar-container {
  background: $light-1;
  border-radius: $border-radius-lg;
  padding: $spacer-lg;
  margin-bottom: $spacer-xl;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacer-lg;
}

.calendar-header h3 {
  margin: 0;
  color: $text-color;
  font-size: $text-xl;
}

.calendar-nav {
  background: $color-white;
  border: 1px solid $light-4;
  padding: $spacer-sm $spacer-md;
  border-radius: $border-radius-sm;
  cursor: pointer;
  font-weight: $fw-semibold;
  color: $light-7;
  transition: $transition-fast;
}

.calendar-nav:hover {
  background: $light-2;
  border-color: $light-5;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: $spacer-sm;
  margin-bottom: $spacer-md;
}

.weekday {
  text-align: center;
  font-weight: $fw-semibold;
  color: $light-6;
  font-size: $text-sm;
  padding: $spacer-sm;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: $spacer-sm;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid $light-3;
  border-radius: $border-radius-md;
  cursor: pointer;
  font-weight: $fw-medium;
  color: $light-7;
  background: $color-white;
  transition: $transition-fast;
}

.calendar-day:not(.empty):not(.disabled):hover {
  border-color: $color-indigo-legacy;
  background: $color-blue-100-legacy;
}

.calendar-day.empty {
  background: transparent;
  border: none;
  cursor: default;
}

.calendar-day.disabled {
  background: $light-2;
  color: $light-4;
  cursor: not-allowed;
}

.calendar-day.selected {
  background: linear-gradient(135deg, $color-indigo-legacy, $color-purple-legacy);
  color: $color-white;
  border-color: $color-indigo-legacy;
}

/* Time Slots */
.timeslots-container {
  margin-bottom: $spacer-xl;
}

.timeslot-group {
  margin-bottom: $spacer-xl;
}

.timeslot-group h3 {
  margin: 0 0 $spacer-md 0;
  color: $light-7;
  font-size: $text-base;
  font-weight: $fw-semibold;
}

.timeslots {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: $spacer-md;
}

.timeslot {
  padding: $spacer-sm + $spacer-xs;
  border: 2px solid $light-4;
  border-radius: $border-radius-md;
  background: $color-white;
  color: $light-7;
  font-weight: $fw-semibold;
  cursor: pointer;
  transition: $transition-fast;
}

.timeslot:hover {
  border-color: $color-indigo-legacy;
  background: $color-blue-100-legacy;
}

.timeslot.selected {
  background: linear-gradient(135deg, $color-indigo-legacy, $color-purple-legacy);
  color: $color-white;
  border-color: $color-indigo-legacy;
}

/* Confirmation Card */
.confirmation-card {
  background: $light-1;
  border-radius: $border-radius-lg;
  padding: $spacer-xl;
  margin-bottom: $spacer-xl;
  border-left: 4px solid $color-indigo-legacy;
}

.confirmation-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacer-md 0;
  border-bottom: 1px solid $light-3;
}

.confirmation-section:last-of-type {
  border-bottom: none;
}

.confirmation-section .label {
  font-weight: $fw-semibold;
  color: $light-7;
}

.confirmation-section .value {
  color: $text-color;
  font-size: $text-base;
}

.confirmation-section .value.monospace {
  font-family: 'Courier New', monospace;
  background: $color-white;
  padding: $spacer-sm $spacer-md;
  border-radius: $border-radius-sm;
  font-size: $text-sm;
}

.confirmation-info {
  background: $color-blue-50-legacy;
  border-radius: $border-radius-md;
  padding: $spacer-md;
  margin: $spacer-lg 0;
  border-left: 4px solid $color-blue-500-legacy;
}

.confirmation-info p {
  margin: $spacer-sm 0;
  color: $color-blue-900-legacy;
  font-size: $text-sm;
  line-height: $lh-normal;
}

.checkbox-container {
  display: flex;
  align-items: center;
  gap: $spacer-sm + $spacer-xs;
  margin-top: $spacer-lg;
  cursor: pointer;
}

.checkbox-container input {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.checkbox-container span {
  color: $light-7;
  font-size: $text-sm;
}

/* Success Step */
.success-step {
  text-align: center;
}

.success-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto $spacer-lg;
  background: linear-gradient(135deg, $color-success, darken($color-success, 5%));
  border-radius: $border-radius-pill;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $spacer-xxl;
  color: $color-white;
  animation: scaleIn 0.5s ease;
}

@keyframes scaleIn {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

.success-message {
  color: $light-6;
  font-size: $text-lg;
  margin-bottom: $spacer-xl;
}

.small-text {
  font-size: $text-sm;
  color: $light-6;
  margin-top: $spacer-md;
}

/* Actions */
.step-actions {
  display: flex;
  gap: $spacer-md;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  padding: $spacer-sm + $spacer-xs $spacer-lg + $spacer-xs;
  border-radius: $border-radius-md;
  font-size: $text-base;
  font-weight: $fw-semibold;
  border: none;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: $spacer-sm;
  transition: $transition-fast;
}

.btn-primary {
  background: linear-gradient(135deg, $color-indigo-legacy, $color-purple-legacy);
  color: $color-white;
  box-shadow: 0 4px 12px rgba($color-indigo-legacy, 0.4);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba($color-indigo-legacy, 0.6);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: $light-2;
  color: $light-7;
  border: 2px solid $light-4;
}

.btn-secondary:hover {
  background: $light-3;
  border-color: $light-5;
}

/* Responsive */
@include media-breakpoint-down(md) {
  .schedule-container {
    padding: $spacer-lg;
  }

  .progress-bar {
    flex-direction: column;
    gap: $spacer-sm;
  }

  .step-actions {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
    justify-content: center;
  }

  .confirmation-section {
    flex-direction: column;
    align-items: flex-start;
    gap: $spacer-sm;
  }
}
</style>
