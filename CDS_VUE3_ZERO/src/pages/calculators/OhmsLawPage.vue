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
            <div v-if="canCalculate && result" class="output-values">
              <div class="value-row"><span>Voltaje</span><strong>{{ result.voltage_v }} V</strong></div>
              <div class="value-row"><span>Corriente</span><strong>{{ result.current_a }} A</strong></div>
              <div class="value-row"><span>Resistencia</span><strong>{{ result.resistance_ohm }} Ω</strong></div>
              <div class="value-row"><span>Potencia</span><strong>{{ result.power_w }} W</strong></div>
            </div>
            <p v-else class="result-hint">Completa al menos 2 campos numéricos.</p>
          </div>
        </section>
      </div>

      <router-link to="/calculadoras" class="back-link">← Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { BaseInput } from '@/components/ui'
import { useOhmsLawCalculator } from '@/composables/useOhmsLawCalculator'

const { form, canCalculate, result } = useOhmsLawCalculator()
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
