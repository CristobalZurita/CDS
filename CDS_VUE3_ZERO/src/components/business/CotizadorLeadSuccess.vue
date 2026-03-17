<template>
  <div class="success-box">
    <i class="fa-solid fa-circle-check success-icon"></i>
    <h2>¡Listo, {{ firstName }}!</h2>
    <p v-if="!notFoundMode">
      Recibimos tu solicitud para el
      <strong>{{ selectedBrandName }} {{ selectedModelName }}</strong>.
      Estimación: <strong>{{ formattedFinalCost }}</strong>.
    </p>
    <p v-else>
      Recibimos tu solicitud para el
      <strong>{{ selectedBrandName }} {{ selectedModelName }}</strong>.
      Prepararemos una cotización personalizada para tu equipo.
    </p>
    <p>Te contactaremos pronto para coordinar la revisión.</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  leadName: {
    type: String,
    required: true
  },
  selectedBrandName: {
    type: String,
    required: true
  },
  selectedModelName: {
    type: String,
    required: true
  },
  formattedFinalCost: {
    type: String,
    required: true
  },
  notFoundMode: {
    type: Boolean,
    default: false
  }
})

const firstName = computed(() => {
  const [name = ''] = String(props.leadName || '').trim().split(' ')
  return name || '!'
})
</script>

<style scoped>
.success-box {
  display: grid;
  gap: 0.6rem;
  text-align: center;
  padding: 1rem 0;
}

.success-icon {
  font-size: 2.5rem;
  color: var(--cds-primary);
  margin: 0 auto;
}

.success-box h2 {
  margin: 0;
  font-size: var(--cds-text-xl);
}

.success-box p {
  margin: 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}
</style>
