<template>
  <BaseCalculatorPage title="Conversor de Longitud" description="Convierte milímetros, centímetros, metros, kilómetros, pulgadas y pies.">
    <section class="calc-panel">
      <div class="panel-header">
        <div class="panel-title">
          <i class="fa-solid fa-ruler"></i>
          Parámetros
        </div>
      </div>

      <div class="panel-body panel-form">
        <BaseInput
          id="length-value"
          v-model.number="form.value"
          label="Valor"
          type="number"
          inputmode="decimal"
          min="0"
          step="0.1"
          placeholder="Ej: 1.25"
        />

        <div class="field-grid">
          <label class="field-label" for="length-from">
            Unidad origen
            <select id="length-from" v-model="form.from_unit" class="field-control">
              <option v-for="unit in lengthUnits" :key="unit.value" :value="unit.value">{{ unit.label }}</option>
            </select>
          </label>

          <label class="field-label" for="length-to">
            Unidad destino
            <select id="length-to" v-model="form.to_unit" class="field-control">
              <option v-for="unit in lengthUnits" :key="`to-${unit.value}`" :value="unit.value">{{ unit.label }}</option>
            </select>
          </label>
        </div>

        <div class="form-actions">
          <BaseButton type="button" variant="ghost" class="swap-button" @click="swapUnits">Intercambiar unidades</BaseButton>
          <BaseButton type="button" variant="ghost" class="reset-button" @click="reset">Resetear parámetros</BaseButton>
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
        <div v-if="canConvert && result !== null" class="output-values">
          <div class="value-row">
            <span>Conversión</span>
            <strong>{{ result }} {{ form.to_unit }}</strong>
          </div>
        </div>
        <p v-else class="result-hint">Ingresa un valor numérico para ver el resultado.</p>
      </div>
    </section>
  </BaseCalculatorPage>
</template>

<script setup>
import { BaseCalculatorPage, BaseButton } from '@/components/base'
import { BaseInput } from '@/components/ui'
import { lengthUnits, useLengthCalculator } from '@/composables/useLengthCalculator'

const { form, canConvert, result, reset } = useLengthCalculator()

function swapUnits() {
  const nextFrom = form.to_unit
  form.to_unit = form.from_unit
  form.from_unit = nextFrom
}
</script>

<style scoped src="./commonCalculatorPage.css"></style>
