<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Reactance</h1>
        <p>Calcula reactancia capacitiva (Xc) o inductiva (Xl) según frecuencia.</p>
      </header>

      <div class="calc-layout">
        <section class="calc-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-sliders"></i>
              Configuración
            </div>

            <div class="mode-tabs">
              <button
                v-for="mode in reactanceModeOptions"
                :key="mode.value"
                class="mode-tab"
                :class="{ 'mode-tab--active': form.mode === mode.value }"
                type="button"
                @click="form.mode = mode.value"
              >
                {{ mode.label }}
              </button>
            </div>
          </div>

          <div class="panel-body">
            <div class="field-grid field-grid--2">
              <BaseInput id="rx-frequency" v-model.number="form.frequency_value" label="Frecuencia" type="number" inputmode="decimal" />
              <label class="field-label" for="rx-frequency-unit">
                Unidad frecuencia
                <select id="rx-frequency-unit" v-model="form.frequency_unit" class="field-control">
                  <option v-for="unit in reactanceFrequencyUnitOptions" :key="`f-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
                </select>
              </label>
            </div>

            <div v-if="form.mode === 'capacitive'" class="field-grid field-grid--2">
              <BaseInput id="rx-cap" v-model.number="form.capacitance_value" label="Capacitancia" type="number" inputmode="decimal" />
              <label class="field-label" for="rx-cap-unit">
                Unidad C
                <select id="rx-cap-unit" v-model="form.capacitance_unit" class="field-control">
                  <option v-for="unit in reactanceCapacitanceUnitOptions" :key="`c-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
                </select>
              </label>
            </div>

            <div v-else class="field-grid field-grid--2">
              <BaseInput id="rx-ind" v-model.number="form.inductance_value" label="Inductancia" type="number" inputmode="decimal" />
              <label class="field-label" for="rx-ind-unit">
                Unidad L
                <select id="rx-ind-unit" v-model="form.inductance_unit" class="field-control">
                  <option v-for="unit in reactanceInductanceUnitOptions" :key="`l-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
                </select>
              </label>
            </div>

            <div class="form-actions">
              <button type="button" class="action-btn" @click="reset">
                <i class="fa-solid fa-rotate-left"></i>
                Resetear parámetros
              </button>
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
            <div class="diagram-card">
              <img src="/images/calculadoras/reacctancia.webp" alt="Referencia reactancia capacitiva e inductiva" />
            </div>

            <div v-if="canCalculate && result" class="output-values">
              <div class="value-row"><span>Modo</span><strong>{{ result.mode === 'capacitive' ? 'Capacitivo' : 'Inductivo' }}</strong></div>
              <div class="value-row"><span>Reactancia</span><strong>{{ result.reactance_ohm }} Ω</strong></div>
            </div>
            <p v-else class="result-hint">Ingresa frecuencia y componente válidos para calcular.</p>
          </div>
        </section>
      </div>

      <router-link to="/calculadoras" class="back-link">← Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { BaseInput } from '@/components/ui'
import {
  useReactanceCalculator,
  reactanceModeOptions,
  reactanceFrequencyUnitOptions,
  reactanceCapacitanceUnitOptions,
  reactanceInductanceUnitOptions,
} from '@/composables/useReactanceCalculator'

const { form, canCalculate, result, reset } = useReactanceCalculator()
</script>

<style scoped src="./commonCalculatorPage.css"></style>
