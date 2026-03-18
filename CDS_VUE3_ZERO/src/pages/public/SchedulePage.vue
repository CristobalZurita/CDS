<template>
  <div class="schedule-page">
    <div class="schedule-container">
      <div class="schedule-header">
        <h1>Agendar Cita de Reparación</h1>
        <p>Selecciona fecha y hora para diagnóstico en taller.</p>
      </div>

      <ScheduleProgressBar :step="step" />

      <div class="schedule-content">
        <ScheduleDateStep
          v-if="step === 1"
          :month-year-string="monthYearString"
          :weekdays="weekdays"
          :calendar-days="calendarDays"
          :selected-date="selectedDate"
          :date-selected="dateSelected"
          :is-date-disabled="isDateDisabled"
          :is-same-date="isSameDate"
          @previous-month="previousMonth"
          @next-month="nextMonth"
          @select-date="selectDate"
          @cancel="goHome"
          @next="step = 2"
        />

        <ScheduleTimeStep
          v-if="step === 2"
          :selected-date="selectedDate"
          :format-date="formatDate"
          :is-loading-availability="isLoadingAvailability"
          :availability-error="availabilityError"
          :morning-slots="morningSlots"
          :afternoon-slots="afternoonSlots"
          :selected-time="selectedTime"
          :time-selected="timeSelected"
          :is-time-slot-unavailable="isTimeSlotUnavailable"
          @select-time="selectedTime = $event"
          @back="step = 1"
          @next="step = 3"
        />

        <ScheduleConfirmStep
          v-if="step === 3"
          :selected-date="selectedDate"
          :selected-time="selectedTime"
          :format-date="formatDate"
          :contact-details-complete="contactDetailsComplete"
          :agree-conditions="agreeConditions"
          :turnstile-token="turnstileToken"
          :turnstile-render-key="turnstileRenderKey"
          :submission-error="submissionError"
          :is-submitting="isSubmitting"
          @update:agree-conditions="agreeConditions = $event"
          @verify="onVerify"
          @back="step = 2"
          @confirm="confirmAppointment"
        />

        <ScheduleSuccessStep
          v-if="step === 4"
          :appointment-number="appointmentNumber"
          :selected-date="selectedDate"
          :selected-time="selectedTime"
          :format-date="formatDate"
          @home="goHome"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import ScheduleConfirmStep from '@/components/business/ScheduleConfirmStep.vue'
import ScheduleDateStep from '@/components/business/ScheduleDateStep.vue'
import ScheduleProgressBar from '@/components/business/ScheduleProgressBar.vue'
import ScheduleSuccessStep from '@/components/business/ScheduleSuccessStep.vue'
import ScheduleTimeStep from '@/components/business/ScheduleTimeStep.vue'
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
<style scoped src="../../components/business/schedulePageShared.css"></style>
