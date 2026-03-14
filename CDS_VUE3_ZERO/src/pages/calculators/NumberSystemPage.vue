<template>
  <BaseCalculatorPage title="Conversor de Sistemas Numéricos" description="Convierte valores entre binario, octal, decimal y hexadecimal.">
    <section class="calc-panel">
      <div class="panel-header">
        <div class="panel-title">
          <i class="fa-solid fa-hashtag"></i>
          Parámetros
        </div>
      </div>

      <div class="panel-body panel-form">
        <BaseInput
          id="number-system-value"
          v-model.trim="form.value"
          label="Valor de entrada"
          type="text"
          placeholder="Ej: FF o 1010"
        />

        <div class="field-grid">
          <label class="field-label" for="number-system-from">
            Base origen
            <select id="number-system-from" v-model.number="form.from" class="field-control">
              <option v-for="base in numericBaseOptions" :key="base.value" :value="base.value">{{ base.label }}</option>
            </select>
          </label>

          <label class="field-label" for="number-system-to">
            Base destino
            <select id="number-system-to" v-model.number="form.to" class="field-control">
              <option v-for="base in numericBaseOptions" :key="`to-${base.value}`" :value="base.value">{{ base.label }}</option>
            </select>
          </label>
        </div>

        <div class="form-actions">
          <BaseButton type="button" variant="ghost" class="swap-button" @click="swapBases">Intercambiar bases</BaseButton>
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
        <div v-if="isValid" class="output-values">
          <div class="value-row">
            <span>Conversión</span>
            <strong>{{ result }}</strong>
          </div>
        </div>
        <p v-else class="result-hint">Ingresa un valor válido para la base de origen.</p>
      </div>
    </section>
  </BaseCalculatorPage>
</template>

<script setup>
import { BaseCalculatorPage, BaseButton } from '@/components/base'
import { BaseInput } from '@/components/ui'
import { numericBaseOptions, useNumberSystemCalculator } from '@/composables/useNumberSystemCalculator'

const { form, isValid, result, reset } = useNumberSystemCalculator()

function swapBases() {
  const nextFrom = form.to
  form.to = form.from
  form.from = nextFrom
}
</script>

<style scoped src="./commonCalculatorPage.css"></style>
