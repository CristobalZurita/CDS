<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Voltage Divider</h1>
        <p>Calcula voltaje de salida, corriente del divisor y potencia en cada resistencia.</p>
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
            <BaseInput id="vd-vin" v-model.number="form.vin_v" label="Vin (V)" type="number" inputmode="decimal" />

            <div class="field-grid field-grid--2">
              <BaseInput id="vd-r1" v-model.number="form.r1_value" label="R1" type="number" inputmode="decimal" />
              <label class="field-label" for="vd-r1-unit">
                Unidad R1
                <select id="vd-r1-unit" v-model="form.r1_unit" class="field-control">
                  <option v-for="unit in voltageDividerResistanceUnits" :key="`r1-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
                </select>
              </label>
            </div>

            <div class="field-grid field-grid--2">
              <BaseInput id="vd-r2" v-model.number="form.r2_value" label="R2" type="number" inputmode="decimal" />
              <label class="field-label" for="vd-r2-unit">
                Unidad R2
                <select id="vd-r2-unit" v-model="form.r2_unit" class="field-control">
                  <option v-for="unit in voltageDividerResistanceUnits" :key="`r2-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
                </select>
              </label>
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
              <img src="/images/calculadoras/votaje_divider.webp" alt="Diagrama divisor de voltaje" />
            </div>

            <div v-if="canCalculate && result" class="output-values">
              <div class="value-row"><span>Vout</span><strong>{{ result.vout_v }} V</strong></div>
              <div class="value-row"><span>Corriente</span><strong>{{ result.current_ma }} mA</strong></div>
              <div class="value-row"><span>Potencia R1</span><strong>{{ result.p_r1_w }} W</strong></div>
              <div class="value-row"><span>Potencia R2</span><strong>{{ result.p_r2_w }} W</strong></div>
              <div class="value-row"><span>Relación</span><strong>{{ result.ratio }}</strong></div>
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
import { useVoltageDividerCalculator, voltageDividerResistanceUnits } from '@/composables/useVoltageDividerCalculator'

const { form, canCalculate, result } = useVoltageDividerCalculator()
</script>

<style scoped src="./commonCalculatorPage.css"></style>
