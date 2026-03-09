<template>
  <main class="calc-page" id="resistor-color-calculator">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Calculadora de Resistencias</h1>
        <p>Código de colores para resistencias THT/DIP de 4, 5 y 6 bandas.</p>
      </header>

      <div class="resistor-layout">
        <section class="resistor-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-palette"></i>
              Parámetros
            </div>
            <div class="panel-tabs">
              <button
                v-for="bands in [4, 5, 6]"
                :key="bands"
                type="button"
                class="panel-tab"
                :class="{ 'panel-tab--active': form.bands === bands }"
                @click="applyBands(bands)"
              >
                {{ bands }} bandas
              </button>
            </div>
          </div>

          <div class="panel-form">
            <div class="form-grid">
              <label class="form-field">
                <span>1ra banda</span>
                <select v-model="form.colors[0]">
                  <option v-for="color in digitColorOptions" :key="`d1-${color.value}`" :value="color.value">
                    {{ color.label }}
                  </option>
                </select>
              </label>

              <label class="form-field">
                <span>2da banda</span>
                <select v-model="form.colors[1]">
                  <option v-for="color in digitColorOptions" :key="`d2-${color.value}`" :value="color.value">
                    {{ color.label }}
                  </option>
                </select>
              </label>

              <label v-if="form.bands >= 5" class="form-field">
                <span>3ra banda</span>
                <select v-model="form.colors[2]">
                  <option v-for="color in digitColorOptions" :key="`d3-${color.value}`" :value="color.value">
                    {{ color.label }}
                  </option>
                </select>
              </label>

              <label class="form-field">
                <span>Multiplicador</span>
                <select v-model="form.colors[multiplierIndex]">
                  <option v-for="color in multiplierColorOptions" :key="`m-${color.value}`" :value="color.value">
                    {{ color.label }}
                  </option>
                </select>
              </label>

              <label class="form-field">
                <span>Tolerancia</span>
                <select v-model="form.colors[toleranceIndex]">
                  <option v-for="color in toleranceColorOptions" :key="`t-${color.value}`" :value="color.value">
                    {{ color.label }}
                  </option>
                </select>
              </label>

              <label v-if="form.bands === 6" class="form-field">
                <span>Tempco</span>
                <select v-model="form.colors[tempcoIndex]">
                  <option v-for="color in tempcoColorOptions" :key="`tc-${color.value}`" :value="color.value">
                    {{ color.label }}
                  </option>
                </select>
              </label>
            </div>

            <div class="form-actions">
              <button type="button" class="btn-reset" @click="resetBands">
                <i class="fa-solid fa-rotate-left"></i>
                Resetear parámetros
              </button>
            </div>
          </div>
        </section>

        <section class="resistor-panel output-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-wave-square"></i>
              Resultado
            </div>
          </div>

          <div class="output-body">
            <div class="resistor-visual">
              <div class="resistor-body">
                <span
                  v-for="(color, index) in previewBands"
                  :key="`${color}-${index}`"
                  :class="['band', bandClass(color)]"
                ></span>
              </div>
            </div>

            <div class="output-values">
              <div class="value-row">
                <span>Resistencia</span>
                <strong>{{ result.formattedResistance }}</strong>
              </div>
              <div class="value-row">
                <span>Tolerancia</span>
                <strong>±{{ result.tolerance_percent }}%</strong>
              </div>
              <div class="value-row">
                <span>Rango</span>
                <strong>{{ result.formattedRange }}</strong>
              </div>
              <div class="value-row" v-if="result.tempco_ppm">
                <span>Tempco</span>
                <strong>{{ result.tempco_ppm }} ppm</strong>
              </div>
            </div>
          </div>
        </section>
      </div>

      <router-link to="/calculadoras" class="back-link">← Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import {
  digitColorOptions,
  multiplierColorOptions,
  toleranceColorOptions,
  tempcoColorOptions,
  useResistorColorCalculator,
} from '@/composables/useResistorColorCalculator'

const { form, multiplierIndex, toleranceIndex, tempcoIndex, result, setBands } = useResistorColorCalculator()

const previewBands = computed(() => form.colors.slice(0, form.bands))

function applyBands(bands) {
  setBands(bands)
  if (bands === 4) {
    form.colors.splice(0, form.colors.length, 'brown', 'black', 'red', 'gold', 'brown', 'brown')
  }
  if (bands === 5) {
    form.colors.splice(0, form.colors.length, 'brown', 'black', 'black', 'red', 'brown', 'brown')
  }
  if (bands === 6) {
    form.colors.splice(0, form.colors.length, 'brown', 'black', 'black', 'red', 'brown', 'brown')
  }
}

function resetBands() {
  applyBands(4)
}

function bandClass(color) {
  const normalized = String(color || '').toLowerCase()
  return normalized ? `band-${normalized}` : 'band-default'
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
  max-width: 1150px;
  margin: 0 auto;
  display: grid;
  gap: 1.5rem;
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

.resistor-layout {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 920px) {
  .resistor-layout {
    grid-template-columns: minmax(320px, 1fr) minmax(360px, 1.3fr);
    align-items: start;
  }
}

.resistor-panel {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(233, 236, 230, 0.7));
  border: 1px solid rgba(62, 60, 56, 0.13);
  border-radius: var(--cds-radius-lg);
  box-shadow: var(--cds-shadow-sm);
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
  padding: 0.85rem 1.1rem;
  background: rgba(62, 60, 56, 0.05);
  border-bottom: 1px solid rgba(62, 60, 56, 0.1);
}

.panel-title {
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--cds-dark);
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.panel-tabs {
  display: flex;
  gap: 0.3rem;
}

.panel-tab {
  padding: 0.3rem 0.85rem;
  border-radius: 999px;
  border: 1px solid rgba(62, 60, 56, 0.22);
  background: transparent;
  color: var(--cds-dark);
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  cursor: pointer;
}

.panel-tab--active {
  background: var(--cds-primary);
  border-color: var(--cds-primary);
  color: var(--cds-white);
}

.panel-form {
  padding: 1rem 1.1rem 1.25rem;
  display: grid;
  gap: 1rem;
}

.form-grid {
  display: grid;
  gap: 0.85rem;
}

.form-field {
  display: grid;
  gap: 0.3rem;
}

.form-field span {
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-dark);
  letter-spacing: 0.02em;
}

.form-field select,
.form-field input {
  border: 1.5px solid rgba(62, 60, 56, 0.25);
  border-radius: 0.5rem;
  padding: 0.62rem 0.75rem;
  font-size: var(--cds-text-base);
  background: var(--cds-white);
  color: var(--cds-dark);
  outline: none;
  width: 100%;
  box-sizing: border-box;
}

.form-field select:focus,
.form-field input:focus {
  border-color: var(--cds-primary);
}

.form-actions {
  display: flex;
}

.btn-reset {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1rem;
  border-radius: 0.5rem;
  border: 1.5px solid rgba(62, 60, 56, 0.25);
  background: transparent;
  color: var(--cds-dark);
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  cursor: pointer;
}

.output-body {
  padding: 1rem 1.1rem 1.25rem;
  display: grid;
  gap: 1rem;
}

.resistor-visual {
  display: flex;
  justify-content: center;
  padding: 0.2rem 0 0.5rem;
}

.resistor-body {
  width: min(100%, 380px);
  min-height: 64px;
  border-radius: 999px;
  background: linear-gradient(135deg, #f1d9a8, #e8c98d);
  border: 1px solid rgba(62, 60, 56, 0.25);
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 18px;
  justify-content: center;
  align-items: stretch;
  gap: 10px;
  padding: 0 1.2rem;
}

.band {
  border-radius: 4px;
  margin: 8px 0;
  border: 1px solid rgba(62, 60, 56, 0.3);
}

.band-black { background: #1f1f1f; }
.band-brown { background: #6f4a2a; }
.band-red { background: #b8392c; }
.band-orange { background: #d88321; }
.band-yellow { background: #e4bf31; }
.band-green { background: #3f7d4c; }
.band-blue { background: #2d5fb0; }
.band-violet { background: #6e4ca3; }
.band-gray { background: #9e9e9e; }
.band-white { background: #f2f2f2; }
.band-gold { background: #d2ae3d; }
.band-silver { background: #c4c4c4; }
.band-default { background: #8c8c8c; }

.output-values {
  display: grid;
  gap: 0.5rem;
}

.value-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.55rem 0.85rem;
  background: rgba(62, 60, 56, 0.04);
  border-radius: 0.45rem;
  border: 1px solid rgba(62, 60, 56, 0.08);
}

.value-row span {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.value-row strong {
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-primary);
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
  font-weight: var(--cds-font-semibold);
  width: fit-content;
  font-size: var(--cds-text-sm);
}
</style>
