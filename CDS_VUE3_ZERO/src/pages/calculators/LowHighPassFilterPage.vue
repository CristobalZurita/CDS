<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Low / High Pass Filter</h1>
        <p>Calcula frecuencia de corte y respuesta de ganancia para filtro RC de primer orden.</p>
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
                v-for="mode in filterModeOptions"
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
              <BaseInput id="fhp-r-value" v-model.number="form.r_value" label="Resistencia" type="number" inputmode="decimal" />
              <label class="field-label" for="fhp-r-unit">
                Unidad R
                <select id="fhp-r-unit" v-model="form.r_unit" class="field-control">
                  <option v-for="unit in filterResistanceUnitOptions" :key="`r-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
                </select>
              </label>
            </div>

            <div class="field-grid field-grid--2">
              <BaseInput id="fhp-c-value" v-model.number="form.c_value" label="Capacitancia" type="number" inputmode="decimal" />
              <label class="field-label" for="fhp-c-unit">
                Unidad C
                <select id="fhp-c-unit" v-model="form.c_unit" class="field-control">
                  <option v-for="unit in filterCapacitanceUnitOptions" :key="`c-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
                </select>
              </label>
            </div>

            <div class="field-grid field-grid--2">
              <BaseInput id="fhp-f-value" v-model.number="form.frequency_value" label="Frecuencia de análisis" type="number" inputmode="decimal" />
              <label class="field-label" for="fhp-f-unit">
                Unidad f
                <select id="fhp-f-unit" v-model="form.frequency_unit" class="field-control">
                  <option v-for="unit in filterFrequencyUnitOptions" :key="`f-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
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
              <img src="/images/calculadoras/filters.webp" alt="Diagrama filtro low pass y high pass" />
            </div>

            <div v-if="canCalculate && result" class="output-values">
              <div class="value-row"><span>Frecuencia de corte</span><strong>{{ result.cutoff_hz }} Hz</strong></div>
              <div class="value-row"><span>Ganancia (lineal)</span><strong>{{ result.gain_ratio ?? '—' }}</strong></div>
              <div class="value-row"><span>Ganancia (%)</span><strong>{{ result.gain_percent ?? '—' }}<template v-if="result.gain_percent != null"> %</template></strong></div>
              <div class="value-row"><span>Ganancia (dB)</span><strong>{{ result.gain_db ?? '—' }}<template v-if="result.gain_db != null"> dB</template></strong></div>
            </div>
            <p v-else class="result-hint">Ingresa R y C válidos para calcular.</p>
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
  useLowHighPassFilterCalculator,
  filterModeOptions,
  filterResistanceUnitOptions,
  filterCapacitanceUnitOptions,
  filterFrequencyUnitOptions,
} from '@/composables/useLowHighPassFilterCalculator'

const { form, canCalculate, result, reset } = useLowHighPassFilterCalculator()
</script>

<style scoped src="./commonCalculatorPage.css"></style>
