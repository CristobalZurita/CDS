<template>
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
</template>

<script setup>
defineProps({
  step: { type: Number, default: 1 }
})
</script>

<style scoped src="./schedulePageShared.css"></style>
