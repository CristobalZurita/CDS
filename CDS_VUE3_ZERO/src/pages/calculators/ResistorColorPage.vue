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

<style scoped src="./commonCalculatorPage.css"></style>
