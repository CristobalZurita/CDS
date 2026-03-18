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
        <div class="value-row"><span>Voltaje</span><strong>{{ displayResult.voltage_v }} V</strong></div>
        <div class="value-row"><span>Corriente</span><strong>{{ displayResult.current_a }} A</strong></div>
        <div class="value-row"><span>Resistencia</span><strong>{{ displayResult.resistance_ohm }} Ohm</strong></div>
        <div class="value-row"><span>Potencia</span><strong>{{ displayResult.power_w }} W</strong></div>
      </div>

      <div class="ohm-visual-grid">
        <article class="ohm-wheel-card">
          <div class="ohm-wheel">
            <span class="wheel-label wheel-label--v" :class="{ 'is-active': highlightedFormulas.includes('V') }">V</span>
            <span class="wheel-label wheel-label--i" :class="{ 'is-active': highlightedFormulas.includes('I') }">I</span>
            <span class="wheel-label wheel-label--r" :class="{ 'is-active': highlightedFormulas.includes('R') }">R</span>
            <span class="wheel-label wheel-label--p" :class="{ 'is-active': highlightedFormulas.includes('P') }">P</span>
            <div class="wheel-core">
              <small>Variable activa</small>
              <strong>{{ solvedVariableLabel }}</strong>
            </div>
          </div>
        </article>

        <div class="formula-grid">
          <article
            v-for="formula in formulaCards"
            :key="formula.key"
            class="formula-card"
            :class="{ 'formula-card--active': highlightedFormulas.includes(formula.key) }"
          >
            <span>{{ formula.title }}</span>
            <strong>{{ formula.expression }}</strong>
          </article>
        </div>
      </div>

      <div class="meter-grid">
        <OhmsLawMeterCard
          v-for="meter in meterItems"
          :key="meter.key"
          :label="meter.label"
          :value="meter.value"
          :unit="meter.unit"
          :percent="meter.percent"
          :tone="meter.tone"
        />
      </div>

      <p v-if="!canCalculate" class="result-hint">Completa al menos 2 campos numericos.</p>
    </div>
  </section>
</template>

<script setup>
import OhmsLawMeterCard from '@/components/business/OhmsLawMeterCard.vue'

defineProps({
  canCalculate: { type: Boolean, default: false },
  displayResult: { type: Object, required: true },
  formulaCards: { type: Array, required: true },
  highlightedFormulas: { type: Array, required: true },
  meterItems: { type: Array, required: true },
  solvedVariableLabel: { type: String, default: '-' }
})
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
<style scoped src="../../pages/calculators/OhmsLawPage.css"></style>
