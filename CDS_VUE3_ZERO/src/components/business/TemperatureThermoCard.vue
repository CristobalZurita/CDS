<template>
  <article class="thermo-card">
    <header class="thermo-card-head">
      <span>{{ label }}</span>
      <strong>{{ formattedValue }}</strong>
    </header>

    <div class="thermo-track" :class="`thermo-track--${tone}`">
      <span class="thermo-column"></span>
      <span class="thermo-bulb"></span>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  fillPercent: { type: Number, default: 0 },
  formattedValue: { type: String, default: '- ' },
  label: { type: String, default: '' },
  tone: { type: String, default: 'hot' }
})

const thermoFill = computed(() => `${props.fillPercent}%`)
</script>

<style scoped src="../../pages/calculators/TemperaturePage.css"></style>
<style scoped>
.thermo-track {
  --thermo-fill: v-bind(thermoFill);
}

.thermo-track--hot {
  --thermo-color: #ec6b00;
}

.thermo-track--warm {
  --thermo-color: #c74f33;
}

.thermo-track--cool {
  --thermo-color: #2b8bd7;
}
</style>
