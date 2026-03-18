<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Ley de Ohm</h1>
        <p>Ingresa al menos 2 valores para calcular el tercero y la potencia.</p>
      </header>

      <div class="calc-layout">
        <OhmsLawParametersPanel :form="form" @reset="reset" />

        <OhmsLawOutputPanel
          :can-calculate="canCalculate"
          :display-result="displayResult"
          :formula-cards="formulaCards"
          :highlighted-formulas="highlightedFormulas"
          :meter-items="meterItems"
          :solved-variable-label="solvedVariableLabel"
        />
      </div>

      <router-link to="/calculadoras" class="back-link">← Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import OhmsLawOutputPanel from '@/components/business/OhmsLawOutputPanel.vue'
import OhmsLawParametersPanel from '@/components/business/OhmsLawParametersPanel.vue'
import { useOhmsLawCalculator } from '@/composables/useOhmsLawCalculator'

const { form, canCalculate, displayResult, formulaCards, highlightedFormulas, meterItems, reset, solvedVariableLabel } = useOhmsLawCalculator()
</script>

<style scoped src="./commonCalculatorPage.css"></style>
<style scoped src="./OhmsLawPage.css"></style>
