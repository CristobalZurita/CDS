<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Ley de Ohm</h1>
        <p>Ingresa al menos 2 valores para calcular el tercero y la potencia.</p>
      </header>

      <div class="calc-layout">
        <section class="calc-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-sliders"></i>
              Parámetros
            </div>
          </div>

          <div class="panel-body">
            <div class="field-grid">
              <BaseInput id="ohm-voltage" v-model.number="form.voltage_v" label="Voltaje (V)" type="number" inputmode="decimal" min="0" step="0.1" />
              <BaseInput id="ohm-current" v-model.number="form.current_a" label="Corriente (A)" type="number" inputmode="decimal" min="0" step="0.1" />
              <BaseInput id="ohm-resistance" v-model.number="form.resistance_ohm" label="Resistencia (Ω)" type="number" inputmode="decimal" min="0" step="0.1" />
            </div>

            <div class="form-actions">
              <BaseButton type="button" variant="ghost" class="reset-button" @click="reset">Resetear parámetros</BaseButton>
            </div>
          </div>
        </section>

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
              <div class="value-row"><span>Resistencia</span><strong>{{ displayResult.resistance_ohm }} Ω</strong></div>
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
              <article
                v-for="meter in meterItems"
                :key="meter.key"
                class="meter-card"
              >
                <header class="meter-head">
                  <span>{{ meter.label }}</span>
                  <strong>{{ meter.value }} {{ meter.unit }}</strong>
                </header>
                <div class="meter-track">
                  <span class="meter-fill" :style="{ width: `${meter.percent}%`, background: meter.tone }"></span>
                </div>
              </article>
            </div>
            <p v-if="!canCalculate" class="result-hint">Completa al menos 2 campos numéricos.</p>
          </div>
        </section>
      </div>

      <router-link to="/calculadoras" class="back-link">← Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { BaseButton, BaseInput } from '@/components/base'
import { useOhmsLawCalculator } from '@/composables/useOhmsLawCalculator'

const { form, canCalculate, result, reset } = useOhmsLawCalculator()

const formulaCards = [
  { key: 'V', title: 'Voltaje', expression: 'V = I × R' },
  { key: 'I', title: 'Corriente', expression: 'I = V / R' },
  { key: 'R', title: 'Resistencia', expression: 'R = V / I' },
  { key: 'P', title: 'Potencia', expression: 'P = V × I' }
]

const inputState = computed(() => ({
  hasV: form.voltage_v !== '' && Number.isFinite(Number(form.voltage_v)) && Number(form.voltage_v) >= 0,
  hasI: form.current_a !== '' && Number.isFinite(Number(form.current_a)) && Number(form.current_a) >= 0,
  hasR: form.resistance_ohm !== '' && Number.isFinite(Number(form.resistance_ohm)) && Number(form.resistance_ohm) >= 0
}))

const solvedVariable = computed(() => {
  if (!canCalculate.value || !result.value) return null
  const { hasV, hasI, hasR } = inputState.value
  if (hasV && hasI) return 'R'
  if (hasV && hasR) return 'I'
  if (hasI && hasR) return 'V'
  return null
})

const solvedVariableLabel = computed(() => {
  if (solvedVariable.value === 'V') return 'Voltaje (V)'
  if (solvedVariable.value === 'I') return 'Corriente (I)'
  if (solvedVariable.value === 'R') return 'Resistencia (R)'
  return '—'
})

const displayResult = computed(() => {
  if (result.value) return result.value
  return {
    voltage_v: '—',
    current_a: '—',
    resistance_ohm: '—',
    power_w: '—'
  }
})

const numericResult = computed(() => {
  if (result.value) return result.value
  return {
    voltage_v: 0,
    current_a: 0,
    resistance_ohm: 0,
    power_w: 0
  }
})

const highlightedFormulas = computed(() => (
  solvedVariable.value ? [solvedVariable.value, 'P'] : []
))

function meterPercent(value, softMax) {
  const numeric = Math.abs(Number(value))
  if (!Number.isFinite(numeric)) return 0
  return Math.min(100, (numeric / softMax) * 100)
}

const meterItems = computed(() => {
  return [
    {
      key: 'V',
      label: 'Voltaje',
      unit: 'V',
      value: numericResult.value.voltage_v,
      percent: meterPercent(numericResult.value.voltage_v, 50),
      tone: '#ec6b00'
    },
    {
      key: 'I',
      label: 'Corriente',
      unit: 'A',
      value: numericResult.value.current_a,
      percent: meterPercent(numericResult.value.current_a, 5),
      tone: '#2b8bd7'
    },
    {
      key: 'R',
      label: 'Resistencia',
      unit: 'Ω',
      value: numericResult.value.resistance_ohm,
      percent: meterPercent(numericResult.value.resistance_ohm, 10000),
      tone: '#5b4a3f'
    },
    {
      key: 'P',
      label: 'Potencia',
      unit: 'W',
      value: numericResult.value.power_w,
      percent: meterPercent(numericResult.value.power_w, 250),
      tone: '#ce3f2a'
    }
  ]
})
</script>

<style scoped src="./commonCalculatorPage.css"></style>
<style scoped src="./OhmsLawPage.css"></style>
