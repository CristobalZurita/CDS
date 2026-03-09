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
              <BaseInput id="ohm-voltage" v-model.number="form.voltage_v" label="Voltaje (V)" type="number" inputmode="decimal" />
              <BaseInput id="ohm-current" v-model.number="form.current_a" label="Corriente (A)" type="number" inputmode="decimal" />
              <BaseInput id="ohm-resistance" v-model.number="form.resistance_ohm" label="Resistencia (Ω)" type="number" inputmode="decimal" />
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
import { BaseButton, BaseInput } from '@/components/ui'
import { useOhmsLawCalculator } from '@/composables/useOhmsLawCalculator'

const { form, canCalculate, result, reset } = useOhmsLawCalculator()

const formulaCards = [
  { key: 'V', title: 'Voltaje', expression: 'V = I × R' },
  { key: 'I', title: 'Corriente', expression: 'I = V / R' },
  { key: 'R', title: 'Resistencia', expression: 'R = V / I' },
  { key: 'P', title: 'Potencia', expression: 'P = V × I' }
]

const inputState = computed(() => ({
  hasV: form.voltage_v !== '' && Number.isFinite(Number(form.voltage_v)),
  hasI: form.current_a !== '' && Number.isFinite(Number(form.current_a)),
  hasR: form.resistance_ohm !== '' && Number.isFinite(Number(form.resistance_ohm))
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

<style scoped>
.calc-page {
  padding: var(--cds-space-xl) var(--cds-space-md) var(--cds-space-2xl);
  background:
    radial-gradient(circle at top left, rgba(236, 107, 0, 0.1), transparent 35%),
    radial-gradient(circle at bottom right, rgba(3, 134, 0, 0.06), transparent 28%);
}

.calc-container {
  max-width: 980px;
  margin: 0 auto;
  display: grid;
  gap: 1.25rem;
}

.calc-header h1 {
  margin: 0;
  font-size: var(--cds-text-3xl);
  line-height: var(--cds-leading-tight);
}

.calc-header p {
  margin: 0.4rem 0 0;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-base);
}

.calc-layout {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 860px) {
  .calc-layout {
    grid-template-columns: minmax(300px, 1fr) minmax(320px, 1fr);
  }
}

.calc-panel {
  border: 1px solid rgba(62, 60, 56, 0.13);
  border-radius: var(--cds-radius-lg);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(233, 236, 230, 0.7));
  box-shadow: var(--cds-shadow-sm);
  overflow: hidden;
}

.panel-header {
  padding: 0.85rem 1.1rem;
  border-bottom: 1px solid rgba(62, 60, 56, 0.1);
  background: rgba(62, 60, 56, 0.05);
}

.panel-title {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--cds-dark);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: var(--cds-font-semibold);
  font-size: var(--cds-text-sm);
}

.panel-body {
  padding: 1rem 1.1rem 1.2rem;
}

.field-grid {
  display: grid;
  gap: 0.75rem;
}

.form-actions {
  margin-top: 0.75rem;
  display: flex;
}

.reset-button {
  width: auto;
}

.output-values {
  display: grid;
  gap: 0.5rem;
}

.value-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.55rem 0.85rem;
  border: 1px solid rgba(62, 60, 56, 0.08);
  border-radius: 0.45rem;
  background: rgba(62, 60, 56, 0.04);
}

.value-row span {
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
}

.value-row strong {
  color: var(--cds-primary);
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
}

.result-hint {
  margin: 0;
  font-size: var(--cds-text-base);
  color: var(--cds-text-muted);
}

.ohm-visual-grid {
  margin-top: 0.9rem;
  display: grid;
  gap: 0.8rem;
}

.ohm-wheel-card {
  border: 1px solid rgba(62, 60, 56, 0.12);
  border-radius: 0.65rem;
  background: rgba(255, 255, 255, 0.62);
  padding: 0.8rem;
  display: flex;
  justify-content: center;
}

.ohm-wheel {
  width: 182px;
  height: 182px;
  border-radius: 50%;
  border: 1px solid rgba(62, 60, 56, 0.3);
  background: conic-gradient(
    rgba(236, 107, 0, 0.32) 0deg 90deg,
    rgba(43, 139, 215, 0.3) 90deg 180deg,
    rgba(91, 74, 63, 0.32) 180deg 270deg,
    rgba(206, 63, 42, 0.3) 270deg 360deg
  );
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.wheel-label {
  position: absolute;
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  color: rgba(62, 60, 56, 0.56);
  transition: transform 0.2s ease, color 0.2s ease;
}

.wheel-label.is-active {
  color: var(--cds-dark);
  transform: scale(1.12);
}

.wheel-label--v { top: 12%; left: 50%; transform: translateX(-50%); }
.wheel-label--i { top: 50%; right: 13%; transform: translateY(-50%); }
.wheel-label--r { bottom: 12%; left: 50%; transform: translateX(-50%); }
.wheel-label--p { top: 50%; left: 13%; transform: translateY(-50%); }

.wheel-label--v.is-active,
.wheel-label--r.is-active {
  transform: translateX(-50%) scale(1.12);
}

.wheel-label--i.is-active,
.wheel-label--p.is-active {
  transform: translateY(-50%) scale(1.12);
}

.wheel-core {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(62, 60, 56, 0.2);
  display: grid;
  align-content: center;
  justify-items: center;
  gap: 0.15rem;
  text-align: center;
}

.wheel-core small {
  font-size: var(--cds-text-xs);
  color: var(--cds-text-muted);
}

.wheel-core strong {
  font-size: var(--cds-text-sm);
  color: var(--cds-dark);
}

.formula-grid {
  display: grid;
  gap: 0.55rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.formula-card {
  border: 1px solid rgba(62, 60, 56, 0.13);
  border-radius: 0.55rem;
  background: rgba(255, 255, 255, 0.62);
  padding: 0.55rem 0.6rem;
  display: grid;
  gap: 0.2rem;
}

.formula-card span {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.formula-card strong {
  font-size: var(--cds-text-base);
  color: var(--cds-dark);
}

.formula-card--active {
  border-color: color-mix(in srgb, var(--cds-primary) 55%, transparent);
  background: color-mix(in srgb, var(--cds-primary) 12%, white);
}

.meter-grid {
  margin-top: 0.8rem;
  display: grid;
  gap: 0.6rem;
}

.meter-card {
  border: 1px solid rgba(62, 60, 56, 0.1);
  border-radius: 0.55rem;
  background: rgba(255, 255, 255, 0.62);
  padding: 0.5rem 0.6rem 0.55rem;
}

.meter-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.6rem;
}

.meter-head span {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.meter-head strong {
  font-size: var(--cds-text-sm);
  color: var(--cds-dark);
}

.meter-track {
  margin-top: 0.45rem;
  height: 10px;
  border-radius: 999px;
  overflow: hidden;
  background: rgba(62, 60, 56, 0.12);
}

.meter-fill {
  height: 100%;
  display: block;
  border-radius: inherit;
  transition: width 0.25s ease;
}

@media (min-width: 560px) {
  .ohm-visual-grid {
    grid-template-columns: minmax(180px, 210px) minmax(0, 1fr);
    align-items: stretch;
  }
}

@media (max-width: 420px) {
  .formula-grid {
    grid-template-columns: 1fr;
  }
}

.back-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.65rem 1rem;
  border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, transparent);
  border-radius: 0.6rem;
  text-decoration: none;
  color: var(--cds-primary);
  width: fit-content;
  font-weight: var(--cds-font-semibold);
  font-size: var(--cds-text-sm);
}
</style>
