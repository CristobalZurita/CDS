<template>
  <BaseCalculatorPage title="RC Time Constant" description="Calcula constante de tiempo, corte de frecuencia y tiempo de carga objetivo.">
    <section class="calc-panel">
      <div class="panel-header">
        <div class="panel-title">
          <i class="fa-solid fa-sliders"></i>
          Parámetros
        </div>
      </div>

      <div class="panel-body">
        <div class="field-grid field-grid--2">
          <BaseInput id="rc-r-value" v-model.number="form.r_value" label="Resistencia" type="number" inputmode="decimal" min="0" step="0.1" />
          <label class="field-label" for="rc-r-unit">
            Unidad R
            <select id="rc-r-unit" v-model="form.r_unit" class="field-control">
              <option v-for="unit in rcResistanceUnitOptions" :key="`r-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
            </select>
          </label>
        </div>

        <div class="field-grid field-grid--2">
          <BaseInput id="rc-c-value" v-model.number="form.c_value" label="Capacitancia" type="number" inputmode="decimal" min="0" step="0.1" />
          <label class="field-label" for="rc-c-unit">
            Unidad C
            <select id="rc-c-unit" v-model="form.c_unit" class="field-control">
              <option v-for="unit in rcCapacitanceUnitOptions" :key="`c-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
            </select>
          </label>
        </div>

        <BaseInput id="rc-target-percent" v-model.number="form.target_percent" label="Porcentaje objetivo de carga (%)" type="number" inputmode="decimal" min="1" max="99.999" step="0.1" />

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
          <img src="/images/calculadoras/rc_time.webp" alt="Diagrama constante de tiempo RC" />
        </div>

        <div v-if="canCalculate && result" class="output-values">
          <div class="value-row"><span>τ (segundos)</span><strong>{{ result.tau_s }} s</strong></div>
          <div class="value-row"><span>τ (milisegundos)</span><strong>{{ result.tau_ms }} ms</strong></div>
          <div class="value-row"><span>5τ</span><strong>{{ result.five_tau_s }} s</strong></div>
          <div class="value-row"><span>Frecuencia corte</span><strong>{{ result.cutoff_hz }} Hz</strong></div>
          <div class="value-row"><span>Carga objetivo</span><strong>{{ result.target_percent }} %</strong></div>
          <div class="value-row"><span>Tiempo a objetivo</span><strong>{{ result.t_charge_s }} s</strong></div>
        </div>
        <p v-else class="result-hint">Ingresa valores válidos para calcular.</p>
      </div>
    </section>
  </BaseCalculatorPage>
</template>

<script setup>
import { BaseCalculatorPage } from '@/components/base'
import { BaseInput } from '@/components/ui'
import {
  useRcTimeConstantCalculator,
  rcResistanceUnitOptions,
  rcCapacitanceUnitOptions,
} from '@/composables/useRcTimeConstantCalculator'

const { form, canCalculate, result, reset } = useRcTimeConstantCalculator()
</script>

<style scoped src="./commonCalculatorPage.css"></style>
