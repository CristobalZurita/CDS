<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Ley de Ohm</h1>
        <p>Ingresa al menos 2 valores para calcular el tercero y la potencia.</p>
      </header>

      <section class="calc-card">
        <div class="field-grid">
          <BaseInput
            id="ohm-voltage"
            v-model.number="form.voltage_v"
            label="Voltaje (V)"
            type="number"
            inputmode="decimal"
          />
          <BaseInput
            id="ohm-current"
            v-model.number="form.current_a"
            label="Corriente (A)"
            type="number"
            inputmode="decimal"
          />
          <BaseInput
            id="ohm-resistance"
            v-model.number="form.resistance_ohm"
            label="Resistencia (Ω)"
            type="number"
            inputmode="decimal"
          />
        </div>
      </section>

      <section class="result-card">
        <template v-if="canCalculate && result">
          <p class="result-value">V: {{ result.voltage_v }} V</p>
          <p class="result-value">I: {{ result.current_a }} A</p>
          <p class="result-value">R: {{ result.resistance_ohm }} Ω</p>
          <p class="result-value">P: {{ result.power_w }} W</p>
        </template>
        <p v-else class="result-hint">Completa al menos 2 campos numéricos.</p>
      </section>

      <router-link to="/calculadoras" class="back-link">Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { BaseInput } from '@new/components/ui'
import { useOhmsLawCalculator } from '@new/composables/useOhmsLawCalculator'

const { form, canCalculate, result } = useOhmsLawCalculator()
</script>

<style scoped>
.calc-page { padding: 1rem; }
.calc-container { max-width: 960px; margin: 0 auto; display: grid; gap: 1rem; }
.calc-header h1 { margin: 0; font-size: var(--cds-text-3xl); line-height: var(--cds-leading-tight); }
.calc-header p { margin: 0.4rem 0 0; color: var(--cds-text-muted); font-size: var(--cds-text-base); }
.calc-card, .result-card { background: var(--cds-white); border: 1px solid color-mix(in srgb, var(--cds-light) 75%, white); border-radius: 0.8rem; padding: 1rem; }
.field-grid { display: grid; gap: 0.75rem; }
.result-value { margin: 0.2rem 0; font-size: var(--cds-text-lg); color: var(--cds-primary); font-weight: var(--cds-font-semibold); }
.result-hint { margin: 0; font-size: var(--cds-text-base); color: var(--cds-text-muted); }
.back-link { display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 0.65rem 1rem; border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, white); border-radius: 0.6rem; text-decoration: none; color: var(--cds-primary); width: fit-content; }
@media (min-width: 768px) { .field-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
</style>
