<template>
  <div class="schedule-step">
    <h2>Selecciona una Fecha</h2>
    <div class="calendar-header">
      <button class="btn-secondary" data-testid="schedule-prev-month" @click="$emit('previous-month')">←</button>
      <h3>{{ monthYearString }}</h3>
      <button class="btn-secondary" data-testid="schedule-next-month" @click="$emit('next-month')">→</button>
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
        @click="$emit('select-date', day)"
      >
        {{ day }}
      </button>
    </div>

    <div class="step-actions">
      <button class="btn-secondary" @click="$emit('cancel')">Cancelar</button>
      <button class="btn-primary" data-testid="schedule-date-next" :disabled="!dateSelected" @click="$emit('next')">
        Siguiente →
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  monthYearString: { type: String, default: '' },
  weekdays: { type: Array, default: () => [] },
  calendarDays: { type: Array, default: () => [] },
  selectedDate: { type: Date, default: null },
  dateSelected: { type: Boolean, default: false },
  isDateDisabled: { type: Function, required: true },
  isSameDate: { type: Function, required: true }
})

defineEmits(['previous-month', 'next-month', 'select-date', 'cancel', 'next'])
</script>

<style scoped src="./schedulePageShared.css"></style>
