<template>
  <div class="schedule-step">
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
            @click="$emit('select-time', time)"
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
            @click="$emit('select-time', time)"
          >
            {{ time }}
          </button>
        </div>
      </div>
    </div>

    <div class="step-actions">
      <button class="btn-secondary" data-testid="schedule-time-back" @click="$emit('back')">← Atrás</button>
      <button
        class="btn-primary"
        data-testid="schedule-time-next"
        :disabled="!timeSelected || isLoadingAvailability"
        @click="$emit('next')"
      >
        Siguiente →
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  selectedDate: { type: Date, default: null },
  formatDate: { type: Function, required: true },
  isLoadingAvailability: { type: Boolean, default: false },
  availabilityError: { type: String, default: '' },
  morningSlots: { type: Array, default: () => [] },
  afternoonSlots: { type: Array, default: () => [] },
  selectedTime: { type: String, default: '' },
  timeSelected: { type: Boolean, default: false },
  isTimeSlotUnavailable: { type: Function, required: true }
})

defineEmits(['back', 'next', 'select-time'])
</script>

<style scoped src="./schedulePageShared.css"></style>
