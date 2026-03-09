<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Convertidor de Temperatura</h1>
        <p>Convierte entre Celsius, Fahrenheit, Kelvin y Rankine.</p>
      </header>

      <div class="calc-layout">
        <section class="calc-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-temperature-high"></i>
              Parámetros
            </div>
          </div>

          <div class="panel-body panel-form">
            <BaseInput
              id="temperature-value"
              v-model.number="form.value"
              label="Valor"
              type="number"
              inputmode="decimal"
              placeholder="Ej: 25"
            />

            <div class="field-grid">
              <label class="field-label" for="temperature-from">
                Escala origen
                <select id="temperature-from" v-model="form.from" class="field-control">
                  <option v-for="scale in temperatureScales" :key="scale.value" :value="scale.value">{{ scale.label }}</option>
                </select>
              </label>

              <label class="field-label" for="temperature-to">
                Escala destino
                <select id="temperature-to" v-model="form.to" class="field-control">
                  <option v-for="scale in temperatureScales" :key="`to-${scale.value}`" :value="scale.value">{{ scale.label }}</option>
                </select>
              </label>
            </div>

            <div class="form-actions">
              <BaseButton type="button" variant="ghost" class="swap-button" @click="swapScales">Intercambiar escalas</BaseButton>
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
              <div class="value-row">
                <span>Conversión</span>
                <strong>{{ canConvert ? `${result} °${form.to}` : '—' }}</strong>
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
              <article
                v-for="item in thermoItems"
                :key="item.key"
                class="thermo-card"
              >
                <header class="thermo-card-head">
                  <span>{{ item.label }}</span>
                  <strong>{{ formatScale(item.value, item.unit) }}</strong>
                </header>

                <div
                  class="thermo-track"
                  :style="{
                    '--thermo-fill': `${fillPercent(item)}%`,
                    '--thermo-color': item.tone
                  }"
                >
                  <span class="thermo-column"></span>
                  <span class="thermo-bulb"></span>
                </div>
              </article>
            </div>
            <p v-if="!canConvert" class="result-hint">Ingresa un valor numérico para actualizar la conversión.</p>
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
import { temperatureScales, useTemperatureCalculator } from '@/composables/useTemperatureCalculator'

const { form, canConvert, result, allScales, reset } = useTemperatureCalculator()

const displayScales = computed(() => (
  allScales.value || {
    C: 0,
    F: 32,
    K: 273.15,
    R: 491.67
  }
))

const thermoItems = computed(() => ([
  {
    key: 'C',
    label: 'Celsius',
    unit: '°C',
    value: displayScales.value.C,
    min: -50,
    max: 150,
    tone: '#ec6b00'
  },
  {
    key: 'F',
    label: 'Fahrenheit',
    unit: '°F',
    value: displayScales.value.F,
    min: -58,
    max: 302,
    tone: '#c74f33'
  },
  {
    key: 'K',
    label: 'Kelvin',
    unit: 'K',
    value: displayScales.value.K,
    min: 223.15,
    max: 423.15,
    tone: '#2b8bd7'
  }
]))

function fillPercent(item) {
  if (!Number.isFinite(item.value)) return 0
  const span = item.max - item.min
  if (!(span > 0)) return 0
  const ratio = ((item.value - item.min) / span) * 100
  return Math.min(100, Math.max(0, ratio))
}

function formatScale(value, unit) {
  if (!Number.isFinite(value)) return `— ${unit}`
  return `${value.toFixed(2)} ${unit}`
}

function swapScales() {
  const nextFrom = form.to
  form.to = form.from
  form.from = nextFrom
}
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

.panel-form {
  display: grid;
  gap: 0.9rem;
}

.field-grid {
  display: grid;
  gap: 0.75rem;
}

@media (min-width: 560px) {
  .field-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.field-label {
  display: grid;
  gap: 0.35rem;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-medium);
  color: var(--cds-text-normal);
}

.field-control {
  min-height: 44px;
  border: 1.5px solid rgba(62, 60, 56, 0.25);
  border-radius: 0.5rem;
  padding: 0.75rem 0.875rem;
  font-size: var(--cds-text-base);
  background: var(--cds-white);
  color: var(--cds-text-normal);
}

.form-actions {
  display: flex;
}

.swap-button {
  width: auto;
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

.thermo-grid {
  margin-top: 0.9rem;
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.thermo-card {
  border: 1px solid rgba(62, 60, 56, 0.14);
  border-radius: 0.6rem;
  background: rgba(255, 255, 255, 0.62);
  padding: 0.7rem 0.6rem 0.8rem;
  display: grid;
  gap: 0.5rem;
}

.thermo-card-head {
  display: grid;
  gap: 0.25rem;
  text-align: center;
}

.thermo-card-head span {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.thermo-card-head strong {
  font-size: var(--cds-text-base);
  color: var(--cds-dark);
}

.thermo-track {
  width: 30px;
  height: 146px;
  margin: 0 auto;
  position: relative;
  display: flex;
  justify-content: center;
}

.thermo-column {
  width: 16px;
  height: 100%;
  border-radius: 999px;
  border: 1px solid rgba(62, 60, 56, 0.28);
  background:
    linear-gradient(
      to top,
      color-mix(in srgb, var(--thermo-color) 85%, black) 0%,
      color-mix(in srgb, var(--thermo-color) 85%, black) var(--thermo-fill),
      rgba(255, 255, 255, 0.75) var(--thermo-fill),
      rgba(255, 255, 255, 0.75) 100%
    );
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.45);
}

.thermo-bulb {
  position: absolute;
  bottom: -8px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1px solid rgba(62, 60, 56, 0.35);
  background: color-mix(in srgb, var(--thermo-color) 85%, black);
  box-shadow: 0 5px 12px rgba(0, 0, 0, 0.22);
}

@media (max-width: 720px) {
  .thermo-grid {
    grid-template-columns: 1fr;
  }

  .thermo-track {
    width: 100%;
    height: 54px;
    align-items: center;
  }

  .thermo-column {
    width: 100%;
    height: 16px;
    border-radius: 999px;
    background:
      linear-gradient(
        to right,
        color-mix(in srgb, var(--thermo-color) 85%, black) 0%,
        color-mix(in srgb, var(--thermo-color) 85%, black) var(--thermo-fill),
        rgba(255, 255, 255, 0.75) var(--thermo-fill),
        rgba(255, 255, 255, 0.75) 100%
      );
  }

  .thermo-bulb {
    display: none;
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
