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
              <button class="calendar-nav" @click="previousMonth">←</button>
              <h3>{{ monthYearString }}</h3>
              <button class="calendar-nav" @click="nextMonth">→</button>
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
                  @click="selectedTime = time"
                >
                  {{ time }}
                </button>
              </div>
            </div>
          </div>

          <div class="step-actions">
            <button class="btn-secondary" @click="step = 1">
              ← Atrás
            </button>
            <button
              class="btn-primary"
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

          <div class="step-actions">
            <button class="btn-secondary" @click="step = 2">
              ← Atrás
            </button>
            <button
              class="btn-primary"
              :disabled="!agreeConditions"
              @click="confirmAppointment"
            >
              Confirmar Cita
            </button>
          </div>
        </div>

        <!-- Step 4: Success -->
        <div v-if="step === 4" class="schedule-step success-step">
          <div class="success-icon">✓</div>
          <h2>¡Cita Confirmada!</h2>
          <p class="success-message">
            Tu cita ha sido agendada exitosamente.
          </p>

          <div class="confirmation-card">
            <div class="confirmation-section">
              <span class="label">Número de cita:</span>
              <span class="value monospace">{{ appointmentNumber }}</span>
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

const quotationStore = useQuotationStore()

// State
const step = ref(1)
const selectedDate = ref(null)
const selectedTime = ref(null)
const agreeConditions = ref(false)
const appointmentNumber = ref('')

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

const confirmAppointment = () => {
  // Generar número de cita
  appointmentNumber.value = 'CIT-' + Date.now().toString().slice(-8)
  step.value = 4

  // Aquí iría la lógica para guardar en BD
  console.log('Cita confirmada:', {
    number: appointmentNumber.value,
    date: selectedDate.value,
    time: selectedTime.value,
    instrument: quotationStore.selectedInstrument
  })
}

// Emit
const emit = defineEmits(['cancel'])
</script>

<style scoped>
.schedule-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 1rem;
}

.schedule-container {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  border-radius: 16px;
  padding: 3rem 2rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.schedule-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.schedule-header h1 {
  margin: 0 0 0.5rem 0;
  color: #2d3748;
  font-size: 2rem;
}

.schedule-header p {
  margin: 0;
  color: #718096;
  font-size: 1.1rem;
}

/* Progress Bar */
.progress-bar {
  display: flex;
  justify-content: space-around;
  margin-bottom: 2rem;
  gap: 1rem;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  opacity: 0.5;
  transition: opacity 0.2s;
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
  border-radius: 50%;
  background: #edf2f7;
  color: #4a5568;
  font-weight: 600;
  font-size: 1.1rem;
}

.progress-step.active .step-number {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.step-label {
  font-size: 0.9rem;
  color: #718096;
  font-weight: 500;
}

.progress-step.active .step-label {
  color: #2d3748;
  font-weight: 600;
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
  margin: 0 0 0.5rem 0;
  color: #2d3748;
  font-size: 1.5rem;
}

.step-description {
  margin: 0 0 2rem 0;
  color: #718096;
  font-size: 1rem;
}

/* Calendar */
.calendar-container {
  background: #f7fafc;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.calendar-header h3 {
  margin: 0;
  color: #2d3748;
  font-size: 1.2rem;
}

.calendar-nav {
  background: white;
  border: 1px solid #cbd5e0;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  color: #4a5568;
  transition: all 0.2s;
}

.calendar-nav:hover {
  background: #edf2f7;
  border-color: #a0aec0;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.weekday {
  text-align: center;
  font-weight: 600;
  color: #718096;
  font-size: 0.9rem;
  padding: 0.5rem;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.5rem;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  color: #4a5568;
  background: white;
  transition: all 0.2s;
}

.calendar-day:not(.empty):not(.disabled):hover {
  border-color: #667eea;
  background: #f0f4ff;
}

.calendar-day.empty {
  background: transparent;
  border: none;
  cursor: default;
}

.calendar-day.disabled {
  background: #edf2f7;
  color: #cbd5e0;
  cursor: not-allowed;
}

.calendar-day.selected {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-color: #667eea;
}

/* Time Slots */
.timeslots-container {
  margin-bottom: 2rem;
}

.timeslot-group {
  margin-bottom: 2rem;
}

.timeslot-group h3 {
  margin: 0 0 1rem 0;
  color: #4a5568;
  font-size: 1rem;
  font-weight: 600;
}

.timeslots {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 1rem;
}

.timeslot {
  padding: 0.75rem;
  border: 2px solid #cbd5e0;
  border-radius: 8px;
  background: white;
  color: #4a5568;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.timeslot:hover {
  border-color: #667eea;
  background: #f0f4ff;
}

.timeslot.selected {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-color: #667eea;
}

/* Confirmation Card */
.confirmation-card {
  background: #f7fafc;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  border-left: 4px solid #667eea;
}

.confirmation-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #e2e8f0;
}

.confirmation-section:last-of-type {
  border-bottom: none;
}

.confirmation-section .label {
  font-weight: 600;
  color: #4a5568;
}

.confirmation-section .value {
  color: #2d3748;
  font-size: 1rem;
}

.confirmation-section .value.monospace {
  font-family: 'Courier New', monospace;
  background: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
}

.confirmation-info {
  background: #eff6ff;
  border-radius: 8px;
  padding: 1rem;
  margin: 1.5rem 0;
  border-left: 4px solid #3b82f6;
}

.confirmation-info p {
  margin: 0.5rem 0;
  color: #1e40af;
  font-size: 0.95rem;
  line-height: 1.5;
}

.checkbox-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1.5rem;
  cursor: pointer;
}

.checkbox-container input {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.checkbox-container span {
  color: #4a5568;
  font-size: 0.95rem;
}

/* Success Step */
.success-step {
  text-align: center;
}

.success-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
  background: linear-gradient(135deg, #48bb78, #38a169);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  color: white;
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
  color: #718096;
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.small-text {
  font-size: 0.9rem;
  color: #718096;
  margin-top: 1rem;
}

/* Actions */
.step-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  padding: 0.875rem 1.75rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.6);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #edf2f7;
  color: #4a5568;
  border: 2px solid #cbd5e0;
}

.btn-secondary:hover {
  background: #e2e8f0;
  border-color: #a0aec0;
}

/* Responsive */
@media (max-width: 768px) {
  .schedule-container {
    padding: 1.5rem;
  }

  .progress-bar {
    flex-direction: column;
    gap: 0.5rem;
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
    gap: 0.5rem;
  }
}
</style>
