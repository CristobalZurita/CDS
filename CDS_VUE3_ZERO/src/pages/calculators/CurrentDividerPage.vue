<template>
  <BaseCalculatorPage title="Current Divider" description="Distribuye la corriente total por ramas en paralelo según su resistencia.">
    <section class="calc-panel">
      <div class="panel-header">
        <div class="panel-title">
          <i class="fa-solid fa-sliders"></i>
          Parámetros
        </div>
      </div>

      <div class="panel-body">
        <div class="field-grid field-grid--2">
          <BaseInput id="cd-total-current" v-model.number="form.total_current_value" label="Corriente total" type="number" inputmode="decimal" min="0" step="0.1" />
          <label class="field-label" for="cd-total-current-unit">
            Unidad corriente total
            <select id="cd-total-current-unit" v-model="form.total_current_unit" class="field-control">
              <option v-for="unit in currentDividerCurrentUnitOptions" :key="`total-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
            </select>
          </label>
        </div>

        <div class="field-grid field-grid--2">
          <label class="field-label" for="cd-resistor-unit">
            Unidad resistencias
            <select id="cd-resistor-unit" v-model="form.resistor_unit" class="field-control">
              <option v-for="unit in currentDividerResistanceUnitOptions" :key="`rin-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
            </select>
          </label>

          <label class="field-label" for="cd-output-current-unit">
            Unidad resultado corriente
            <select id="cd-output-current-unit" v-model="form.output_current_unit" class="field-control">
              <option v-for="unit in currentDividerCurrentUnitOptions" :key="`out-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
            </select>
          </label>
        </div>

        <div class="form-grid">
          <div v-for="(value, index) in form.resistors" :key="`branch-${index}`" class="field-label">
            R{{ index + 1 }}
            <input v-model.number="form.resistors[index]" type="number" min="0" step="0.1" inputmode="decimal" class="field-control" />
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="action-btn action-btn--primary" @click="addBranch">
            <i class="fa-solid fa-plus"></i>
            Agregar rama
          </button>
          <button type="button" class="action-btn" @click="removeBranch">
            <i class="fa-solid fa-minus"></i>
            Quitar rama
          </button>
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
          <img src="/images/calculadoras/corriente_div.webp" alt="Diagrama divisor de corriente" />
        </div>

        <div v-if="canCalculate && result" class="output-values">
          <div class="value-row">
            <span>Corriente total</span>
            <strong>{{ result.total_current_output_unit }} {{ unitLabel(form.output_current_unit) }}</strong>
          </div>

          <div
            v-for="branch in result.branches"
            :key="`branch-output-${branch.index}`"
            class="value-row"
          >
            <span>I{{ branch.index }}</span>
            <strong>{{ branch.current_output_unit }} {{ unitLabel(form.output_current_unit) }}</strong>
          </div>
        </div>
        <p v-else class="result-hint">Ingresa corriente total y al menos 2 resistencias válidas.</p>
      </div>
    </section>
  </BaseCalculatorPage>
</template>

<script setup>
import { BaseCalculatorPage } from '@/components/base'
import { BaseInput } from '@/components/ui'
import {
  useCurrentDividerCalculator,
  currentDividerResistanceUnitOptions,
  currentDividerCurrentUnitOptions,
} from '@/composables/useCurrentDividerCalculator'

const { form, canCalculate, result, addBranch, removeBranch, reset } = useCurrentDividerCalculator()

function unitLabel(unit) {
  const found = currentDividerCurrentUnitOptions.find((entry) => entry.value === unit)
  return found ? found.label : 'A'
}
</script>

<style scoped src="./commonCalculatorPage.css"></style>
