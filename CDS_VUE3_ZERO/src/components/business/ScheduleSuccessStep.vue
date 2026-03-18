<template>
  <div class="schedule-step success-step" data-testid="schedule-success">
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
      <button class="btn-secondary" @click="$emit('home')">Volver al inicio</button>
      <router-link class="btn-primary" to="/dashboard">Ir al dashboard</router-link>
    </div>
  </div>
</template>

<script setup>
defineProps({
  appointmentNumber: { type: String, default: '' },
  selectedDate: { type: Date, default: null },
  selectedTime: { type: String, default: '' },
  formatDate: { type: Function, required: true }
})

defineEmits(['home'])
</script>

<style scoped src="./schedulePageShared.css"></style>
