<template>
  <BaseCalculatorPage title="Parallel and Series Resistor" description="Calcula resistencia equivalente en configuración serie o paralelo.">
    <section class="calc-panel">
      <div class="panel-header">
        <div class="panel-title">
          <i class="fa-solid fa-sliders"></i>
          Configuración
        </div>
        <div class="mode-tabs">
          <button
            v-for="mode in resistorNetworkModes"
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
          <label class="field-label" for="res-network-unit">
            Unidad de entrada
            <select id="res-network-unit" v-model="form.input_unit" class="field-control">
              <option v-for="unit in resistorUnitOptions" :key="`in-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
            </select>
          </label>

          <label class="field-label" for="res-network-output-unit">
            Unidad resultado
            <select id="res-network-output-unit" v-model="form.output_unit" class="field-control">
              <option v-for="unit in resistorUnitOptions" :key="`out-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
            </select>
          </label>
        </div>

        <div class="form-grid">
          <div v-for="(value, index) in form.resistors" :key="`res-${index}`" class="field-label">
            R{{ index + 1 }}
            <input v-model.number="form.resistors[index]" type="number" min="0" step="0.1" inputmode="decimal" class="field-control" />
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="action-btn action-btn--primary" @click="addResistor">
            <i class="fa-solid fa-plus"></i>
            Agregar resistor
          </button>
          <button type="button" class="action-btn" @click="removeResistor">
            <i class="fa-solid fa-minus"></i>
            Quitar resistor
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
          <img src="/images/calculadoras/serie_parallel.webp" alt="Circuito serie y paralelo" />
        </div>

        <div v-if="canCalculate && result" class="output-values">
          <div class="value-row"><span>Req</span><strong>{{ result.total_in_output_unit }} {{ unitLabel(form.output_unit) }}</strong></div>
          <div class="value-row"><span>Req (Ω)</span><strong>{{ result.total_ohm }} Ω</strong></div>
          <div class="value-row"><span>Resistores válidos</span><strong>{{ sanitizedResistors.length }}</strong></div>
        </div>
        <p v-else class="result-hint">Ingresa al menos 2 resistores válidos.</p>
      </div>
    </section>
  </BaseCalculatorPage>
</template>

<script setup>
import { BaseCalculatorPage } from '@/components/base'
import { useSeriesParallelResistorCalculator, resistorNetworkModes, resistorUnitOptions } from '@/composables/useSeriesParallelResistorCalculator'

const { form, canCalculate, sanitizedResistors, result, addResistor, removeResistor, reset } = useSeriesParallelResistorCalculator()

function unitLabel(unit) {
  const found = resistorUnitOptions.find((entry) => entry.value === unit)
  return found ? found.label : 'Ω'
}
</script>

<style scoped src="./commonCalculatorPage.css"></style>
