<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>LED Series Resistor</h1>
        <p>Calcula el resistor en serie para proteger LEDs según fuente, Vf e intensidad.</p>
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
            <BaseInput id="led-supply" v-model.number="form.supply_v" label="Voltaje de fuente (V)" type="number" inputmode="decimal" />
            <BaseInput id="led-forward" v-model.number="form.led_forward_v" label="Voltaje directo por LED (Vf)" type="number" inputmode="decimal" />
            <BaseInput id="led-count" v-model.number="form.led_count" label="Cantidad de LEDs en serie" type="number" inputmode="numeric" />

            <div class="field-grid field-grid--2">
              <BaseInput id="led-current" v-model.number="form.led_current_value" label="Corriente objetivo" type="number" inputmode="decimal" />
              <label class="field-label" for="led-current-unit">
                Unidad corriente
                <select id="led-current-unit" v-model="form.led_current_unit" class="field-control">
                  <option v-for="unit in ledCurrentUnitOptions" :key="unit.value" :value="unit.value">{{ unit.label }}</option>
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
              <img src="/images/calculadoras/led_series_RES.webp" alt="Diagrama cálculo resistor LED" />
            </div>

            <div v-if="canCalculate && result" class="output-values">
              <p v-if="result.error" class="result-hint">{{ result.error }}</p>

              <template v-else>
                <div class="value-row"><span>Resistor serie</span><strong>{{ result.resistor_ohm }} Ω</strong></div>
                <div class="value-row"><span>Caída en resistor</span><strong>{{ result.voltage_drop_v }} V</strong></div>
                <div class="value-row"><span>Potencia mínima</span><strong>{{ result.resistor_power_w }} W</strong></div>
                <div class="value-row"><span>Potencia recomendada</span><strong>{{ result.recommended_power_w }} W</strong></div>
                <div class="value-row"><span>Corriente LED</span><strong>{{ result.led_current_a }} A</strong></div>
              </template>
            </div>
            <p v-else class="result-hint">Ingresa valores válidos para calcular.</p>
          </div>
        </section>
      </div>

      <router-link to="/calculadoras" class="back-link">← Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { BaseInput } from '@/components/ui'
import { useLedSeriesResistorCalculator, ledCurrentUnitOptions } from '@/composables/useLedSeriesResistorCalculator'

const { form, canCalculate, result, reset } = useLedSeriesResistorCalculator()
</script>

<style scoped src="./commonCalculatorPage.css"></style>
