<template>
  <div class="schedule-page">
    <div class="schedule-container">
      <div class="schedule-header">
        <h1>Agendar Cita de Reparación</h1>
        <p>Selecciona fecha y hora para diagnóstico en taller.</p>
      </div>

      <div class="progress-bar">
        <div class="progress-step" :class="{ active: step >= 1 }">
          <span class="step-number">1</span>
          <span class="step-label">Fecha</span>
        </div>
        <div class="progress-step" :class="{ active: step >= 2 }">
          <span class="step-number">2</span>
          <span class="step-label">Hora</span>
        </div>
        <div class="progress-step" :class="{ active: step >= 3 }">
          <span class="step-number">3</span>
          <span class="step-label">Confirmación</span>
        </div>
      </div>

      <div class="schedule-content">
        <div v-if="step === 1" class="schedule-step">
          <h2>Selecciona una Fecha</h2>
          <div class="calendar-header">
            <button class="btn-secondary" data-testid="schedule-prev-month" @click="previousMonth">←</button>
            <h3>{{ monthYearString }}</h3>
            <button class="btn-secondary" data-testid="schedule-next-month" @click="nextMonth">→</button>
          </div>

          <div class="calendar-weekdays">
            <div v-for="day in weekdays" :key="day" class="weekday">{{ day }}</div>
          </div>

          <div class="calendar-days">
            <button
              v-for="(day, idx) in calendarDays"
              :key="day ? `day-${day}` : `empty-${idx}`"
              class="calendar-day"
              :class="{
                empty: !day,
                disabled: isDateDisabled(day),
                selected: isSameDate(selectedDate, day)
              }"
              data-testid="schedule-day"
              :data-day="day || ''"
              :data-disabled="isDateDisabled(day) ? 'true' : 'false'"
              :disabled="!day || isDateDisabled(day)"
              @click="selectDate(day)"
            >
              {{ day }}
            </button>
          </div>

          <div class="step-actions">
            <button class="btn-secondary" @click="goHome">Cancelar</button>
            <button class="btn-primary" data-testid="schedule-date-next" :disabled="!dateSelected" @click="step = 2">
              Siguiente →
            </button>
          </div>
        </div>

        <div v-if="step === 2" class="schedule-step">
          <h2>Selecciona una Hora</h2>
          <p class="step-description">Fecha seleccionada: {{ formatDate(selectedDate) }}</p>

          <div class="timeslots-container">
            <div class="timeslot-group">
              <h3>Mañana (09:00 - 12:00)</h3>
              <p v-if="isLoadingAvailability" class="schedule-info">Cargando disponibilidad...</p>
              <p v-else-if="availabilityError" class="schedule-warning">{{ availabilityError }}</p>
              <div class="timeslots">
                <button
                  v-for="time in morningSlots"
                  :key="time"
                  class="timeslot"
                  :class="{ selected: selectedTime === time, unavailable: isTimeSlotUnavailable(time) }"
                  data-testid="schedule-time-slot"
                  :data-time="time"
                  :disabled="isLoadingAvailability || isTimeSlotUnavailable(time)"
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
                  :class="{ selected: selectedTime === time, unavailable: isTimeSlotUnavailable(time) }"
                  data-testid="schedule-time-slot"
                  :data-time="time"
                  :disabled="isLoadingAvailability || isTimeSlotUnavailable(time)"
                  @click="selectedTime = time"
                >
                  {{ time }}
                </button>
              </div>
            </div>
          </div>

          <div class="step-actions">
            <button class="btn-secondary" data-testid="schedule-time-back" @click="step = 1">← Atrás</button>
            <button
              class="btn-primary"
              data-testid="schedule-time-next"
              :disabled="!timeSelected || isLoadingAvailability"
              @click="step = 3"
            >
              Siguiente →
            </button>
          </div>
        </div>

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
            <div class="confirmation-info">
              <p><strong>Duración estimada:</strong> 20-30 minutos.</p>
              <p><strong>Importante:</strong> Trae el instrumento y accesorios asociados.</p>
            </div>
            <p v-if="!contactDetailsComplete" class="schedule-warning">
              Debes tener correo y teléfono en tu perfil para confirmar la cita.
            </p>
            <label class="checkbox-container">
              <input v-model="agreeConditions" type="checkbox" />
              <span>Acepto los términos y condiciones de esta cita</span>
            </label>
          </div>

          <TurnstileWidget :key="turnstileRenderKey" @verify="onVerify" />

          <p v-if="submissionError" class="schedule-error" data-testid="schedule-error">
            {{ submissionError }}
          </p>

          <div class="step-actions">
            <button class="btn-secondary" @click="step = 2">← Atrás</button>
            <button
              class="btn-primary"
              data-testid="schedule-confirm"
              :disabled="isSubmitting || !agreeConditions || !turnstileToken || !contactDetailsComplete"
              @click="confirmAppointment"
            >
              {{ isSubmitting ? 'Confirmando...' : 'Confirmar Cita' }}
            </button>
          </div>
        </div>

        <div v-if="step === 4" class="schedule-step success-step" data-testid="schedule-success">
          <div class="success-icon">✓</div>
          <h2>¡Cita Confirmada!</h2>
          <p class="success-message">Tu cita fue registrada correctamente.</p>
          <div class="confirmation-card">
            <div class="confirmation-section">
              <span class="label">Número de cita:</span>
              <span class="value monospace" data-testid="schedule-appointment-number">{{ appointmentNumber }}</span>
            </div>
            <div class="confirmation-section">
              <span class="label">Fecha y hora:</span>
              <span class="value">{{ formatDate(selectedDate) }} a las {{ selectedTime }}</span>
            </div>
          </div>
          <div class="step-actions">
            <button class="btn-secondary" @click="goHome">Volver al inicio</button>
            <router-link class="btn-primary" to="/dashboard">Ir al dashboard</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import TurnstileWidget from '@/components/widgets/TurnstileWidget.vue'
import { useSchedulePage } from '@/composables/useSchedulePage'

const {
  step,
  selectedDate,
  selectedTime,
  contactDetailsComplete,
  agreeConditions,
  turnstileToken,
  turnstileRenderKey,
  appointmentNumber,
  isSubmitting,
  isLoadingAvailability,
  submissionError,
  availabilityError,
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
} = useSchedulePage()
</script>

<style scoped>
.schedule-page {
  padding: 1rem;
}

.schedule-container {
  max-width: 1040px;
  margin: 0 auto;
  display: grid;
  gap: 1rem;
}

.schedule-header,
.schedule-step {
  background: var(--cds-white);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-md);
  padding: 1rem;
}

.schedule-header h1 {
  margin: 0;
  font-size: var(--cds-text-3xl);
}

.schedule-header p {
  margin: 0.4rem 0 0;
  color: var(--cds-text-muted);
}

.progress-bar {
  display: grid;
  gap: 0.5rem;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.progress-step {
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-md);
  min-height: 64px;
  display: grid;
  place-items: center;
  background: var(--cds-white);
}

.progress-step.active {
  border-color: color-mix(in srgb, var(--cds-primary) 50%, white);
}

.step-number {
  font-weight: var(--cds-font-bold);
}

.schedule-content {
  display: grid;
}

.schedule-step {
  display: grid;
  gap: 0.9rem;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.calendar-header h3 {
  margin: 0;
}

.calendar-weekdays,
.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 0.35rem;
}

.weekday {
  min-height: 32px;
  display: grid;
  place-items: center;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
}

.calendar-day {
  min-height: 40px;
  border-radius: var(--cds-radius-sm);
  border: 1px solid var(--cds-border-input);
  background: var(--cds-white);
  cursor: pointer;
}

.calendar-day.selected {
  border-color: var(--cds-primary);
  background: color-mix(in srgb, var(--cds-primary) 15%, white);
}

.calendar-day.disabled,
.calendar-day.empty {
  opacity: 0.45;
  cursor: not-allowed;
}

.timeslots-container {
  display: grid;
  gap: 0.9rem;
}

.timeslot-group h3 {
  margin: 0 0 0.45rem;
  font-size: var(--cds-text-base);
}

.timeslots {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.timeslot,
.btn-primary,
.btn-secondary {
  min-height: 44px;
  padding: 0.65rem 0.9rem;
  border-radius: var(--cds-radius-sm);
  font-size: var(--cds-text-base);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.timeslot,
.btn-secondary {
  border: 1px solid color-mix(in srgb, var(--cds-light) 60%, white);
  background: var(--cds-white);
  color: var(--cds-text-normal);
}

.timeslot.selected,
.btn-primary {
  border: 1px solid var(--cds-primary);
  background: var(--cds-primary);
  color: var(--cds-white);
}

.timeslot.unavailable {
  opacity: 0.45;
  cursor: not-allowed;
}

.confirmation-card {
  display: grid;
  gap: 0.7rem;
  border: 1px solid var(--cds-border-input);
  border-radius: var(--cds-radius-md);
  padding: 0.9rem;
}

.confirmation-section {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  border-bottom: 1px solid var(--cds-border-input);
  padding-bottom: 0.5rem;
}

.label {
  color: var(--cds-text-muted);
}

.value {
  font-weight: var(--cds-font-semibold);
}

.confirmation-info p {
  margin: 0.3rem 0;
  font-size: var(--cds-text-base);
}

.checkbox-container {
  display: flex;
  gap: var(--cds-space-xs);
  align-items: flex-start;
  font-size: var(--cds-text-base);
}

.schedule-error {
  margin: 0;
  border: 1px solid var(--cds-invalid-border);
  background: var(--cds-invalid-bg);
  color: var(--cds-invalid-text);
  border-radius: var(--cds-radius-sm);
  padding: 0.7rem;
}

.schedule-info,
.schedule-warning {
  margin: 0;
  border-radius: var(--cds-radius-sm);
  padding: 0.7rem;
}

.schedule-info {
  border: 1px solid color-mix(in srgb, var(--cds-primary) 20%, white);
  background: color-mix(in srgb, var(--cds-primary) 8%, white);
  color: var(--cds-text-normal);
}

.schedule-warning {
  border: 1px solid var(--cds-warning-border);
  background: var(--cds-warning-bg);
  color: var(--cds-warning-text);
}

.success-step {
  text-align: center;
}

.success-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--cds-radius-pill);
  background: var(--cds-primary);
  color: var(--cds-white);
  margin: 0 auto;
  display: grid;
  place-items: center;
  font-size: 1.5rem;
}

.success-message {
  margin: 0;
}

.monospace {
  font-family: monospace;
}

.step-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}
</style>
