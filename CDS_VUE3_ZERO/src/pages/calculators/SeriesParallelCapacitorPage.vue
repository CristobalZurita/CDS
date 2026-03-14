<template>
  <BaseCalculatorPage title="Series and Parallel Capacitor" description="Calcula capacitancia equivalente en configuración serie o paralelo.">
    <section class="calc-panel">
      <div class="panel-header">
        <div class="panel-title">
          <i class="fa-solid fa-sliders"></i>
          Configuración
        </div>
        <div class="mode-tabs">
          <button
            v-for="mode in capacitorNetworkModes"
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
          <label class="field-label" for="cap-network-unit">
            Unidad de entrada
            <select id="cap-network-unit" v-model="form.input_unit" class="field-control">
              <option v-for="unit in capacitorUnitOptions" :key="`in-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
            </select>
          </label>

          <label class="field-label" for="cap-network-output-unit">
            Unidad resultado
            <select id="cap-network-output-unit" v-model="form.output_unit" class="field-control">
              <option v-for="unit in capacitorUnitOptions" :key="`out-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
            </select>
          </label>
        </div>

        <div class="form-grid">
          <div v-for="(value, index) in form.capacitors" :key="`cap-${index}`" class="field-label">
            C{{ index + 1 }}
            <input v-model.number="form.capacitors[index]" type="number" min="0" step="0.1" inputmode="decimal" class="field-control" />
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="action-btn action-btn--primary" @click="addCapacitor">
            <i class="fa-solid fa-plus"></i>
            Agregar capacitor
          </button>
          <button type="button" class="action-btn" @click="removeCapacitor">
            <i class="fa-solid fa-minus"></i>
            Quitar capacitor
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
          <img src="/images/calculadoras/cap_serie_parallel.webp" alt="Capacitores serie y paralelo" />
        </div>

        <div v-if="canCalculate && result" class="output-values">
          <div class="value-row"><span>Ceq</span><strong>{{ result.total_in_output_unit }} {{ unitLabel(form.output_unit) }}</strong></div>
          <div class="value-row"><span>Ceq (F)</span><strong>{{ result.total_f }} F</strong></div>
          <div class="value-row"><span>Capacitores válidos</span><strong>{{ sanitizedCapacitors.length }}</strong></div>
        </div>
        <p v-else class="result-hint">Ingresa al menos 2 capacitores válidos.</p>
      </div>
    </section>
  </BaseCalculatorPage>
</template>

<script setup>
import { BaseCalculatorPage } from '@/components/base'
import { useSeriesParallelCapacitorCalculator, capacitorNetworkModes, capacitorUnitOptions } from '@/composables/useSeriesParallelCapacitorCalculator'

const { form, canCalculate, sanitizedCapacitors, result, addCapacitor, removeCapacitor, reset } = useSeriesParallelCapacitorCalculator()

function unitLabel(unit) {
  const found = capacitorUnitOptions.find((entry) => entry.value === unit)
  return found ? found.label : 'F'
}
</script>

<style scoped src="./commonCalculatorPage.css"></style>
