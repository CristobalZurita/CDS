<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Convertidor de Temperatura</h1>
        <p>Convierte entre Celsius, Fahrenheit, Kelvin y Rankine.</p>
      </header>

      <div class="calc-layout">
        <TemperatureParametersPanel
          :form="form"
          :temperature-scales="temperatureScales"
          @reset="reset"
          @swap="swapScales"
        />

        <TemperatureResultPanel
          :can-convert="canConvert"
          :display-scales="displayScales"
          :fill-percent="fillPercent"
          :form="form"
          :format-scale="formatScale"
          :result="result"
          :thermo-items="thermoItems"
        />
      </div>

      <router-link to="/calculadoras" class="back-link">← Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import TemperatureParametersPanel from '@/components/business/TemperatureParametersPanel.vue'
import TemperatureResultPanel from '@/components/business/TemperatureResultPanel.vue'
import { temperatureScales, useTemperatureCalculator } from '@/composables/useTemperatureCalculator'

const { form, canConvert, displayScales, fillPercent, formatScale, result, reset, swapScales, thermoItems } = useTemperatureCalculator()
</script>

<style scoped src="./commonCalculatorPage.css"></style>
<style scoped src="./TemperaturePage.css"></style>
