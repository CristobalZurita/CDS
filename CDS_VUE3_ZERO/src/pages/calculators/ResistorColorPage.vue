<template>
  <BaseCalculatorPage
    title="Calculadora de Resistencias"
    description="Código de colores para resistencias THT/DIP de 4, 5 y 6 bandas."
  >
    <section class="calc-panel">
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

      <div class="panel-body">
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
          <button type="button" class="action-btn" @click="resetBands">
            <i class="fa-solid fa-rotate-left"></i>
            Resetear parámetros
          </button>
        </div>
      </div>
    </section>

    <section class="calc-panel">
      <div class="panel-header">
        <div class="panel-title">
          <i class="fa-solid fa-wave-square"></i>
          Resultado
        </div>
      </div>

      <div class="panel-body">
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
  </BaseCalculatorPage>
</template>

<script setup>
import { computed } from 'vue'
import { BaseCalculatorPage } from '@/components/base'
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

<style scoped src="./commonCalculatorPage.css"></style>
<style scoped>
/* Panel tabs */
.panel-tabs { display: flex; gap: 0.3rem; }
.panel-tab { padding: 0.3rem 0.85rem; border-radius: var(--cds-radius-pill); border: 1px solid var(--cds-border-strong); background: transparent; color: var(--cds-dark); font-size: var(--cds-text-sm); font-weight: var(--cds-font-semibold); cursor: pointer; }
.panel-tab--active { background: var(--cds-primary); border-color: var(--cds-primary); color: var(--cds-white); }
/* Form fields (selects dentro del panel) */
.form-field { display: grid; gap: 0.3rem; }
.form-field span { font-size: var(--cds-text-sm); font-weight: var(--cds-font-semibold); color: var(--cds-dark); letter-spacing: 0.02em; }
.form-field select, .form-field input { border: 1.5px solid var(--cds-border-strong); border-radius: var(--cds-radius-sm); padding: 0.62rem 0.75rem; font-size: var(--cds-text-base); background: var(--cds-white); color: var(--cds-dark); outline: none; width: 100%; box-sizing: border-box; }
.form-field select:focus, .form-field input:focus { border-color: var(--cds-primary); }
/* Resistor visual */
.resistor-visual { display: flex; justify-content: center; padding: 0.2rem 0 0.5rem; }
.resistor-body { width: min(100%, 380px); min-height: 64px; border-radius: var(--cds-radius-pill); background: linear-gradient(135deg, #f1d9a8, #e8c98d); border: 1px solid var(--cds-border-strong); display: grid; grid-auto-flow: column; grid-auto-columns: 18px; justify-content: center; align-items: stretch; gap: 10px; padding: 0 1.2rem; }
.band { border-radius: 4px; margin: 8px 0; border: 1px solid var(--cds-border-strong); }
.band-black  { background: #1f1f1f; }
.band-brown  { background: #6f4a2a; }
.band-red    { background: #b8392c; }
.band-orange { background: #d88321; }
.band-yellow { background: #e4bf31; }
.band-green  { background: #3f7d4c; }
.band-blue   { background: #2d5fb0; }
.band-violet { background: #6e4ca3; }
.band-gray   { background: #9e9e9e; }
.band-white  { background: #f2f2f2; }
.band-gold   { background: #d2ae3d; }
.band-silver { background: #c4c4c4; }
.band-default { background: #8c8c8c; }
</style>
