<template>
  <section class="calc-panel output-panel">
    <div class="panel-header">
      <div class="panel-title">
        <i class="fa-solid fa-wave-square"></i>
        Resultado
      </div>
    </div>

    <div class="panel-body">
      <div class="output-values">
        <div class="value-row">
          <span>Conversion</span>
          <strong>{{ canConvert ? `${result} °${form.to}` : '-' }}</strong>
        </div>
        <div class="value-row">
          <span>Celsius</span>
          <strong>{{ formatScale(displayScales.C, '°C') }}</strong>
        </div>
        <div class="value-row">
          <span>Fahrenheit</span>
          <strong>{{ formatScale(displayScales.F, '°F') }}</strong>
        </div>
        <div class="value-row">
          <span>Kelvin</span>
          <strong>{{ formatScale(displayScales.K, 'K') }}</strong>
        </div>
      </div>

      <div class="thermo-grid">
        <TemperatureThermoCard
          v-for="item in thermoItems"
          :key="item.key"
          :fill-percent="fillPercent(item)"
          :formatted-value="formatScale(item.value, item.unit)"
          :label="item.label"
          :tone="item.tone"
        />
      </div>

      <p v-if="!canConvert" class="result-hint">Ingresa un valor numerico para actualizar la conversion.</p>
    </div>
  </section>
</template>

<script setup>
import TemperatureThermoCard from '@/components/business/TemperatureThermoCard.vue'

defineProps({
  canConvert: { type: Boolean, default: false },
  displayScales: { type: Object, required: true },
  fillPercent: { type: Function, required: true },
  form: { type: Object, required: true },
  formatScale: { type: Function, required: true },
  result: { type: [Number, String, null], default: null },
  thermoItems: { type: Array, required: true }
})
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
<style scoped src="../../pages/calculators/TemperaturePage.css"></style>
