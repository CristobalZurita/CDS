<template>
  <section class="calc-panel">
    <div class="panel-header">
      <div class="panel-title">
        <i class="fa-solid fa-temperature-high"></i>
        Parametros
      </div>
    </div>

    <div class="panel-body panel-form">
      <BaseInput
        id="temperature-value"
        v-model.number="form.value"
        label="Valor"
        type="number"
        inputmode="decimal"
        placeholder="Ej: 25"
      />

      <div class="field-grid">
        <label class="field-label" for="temperature-from">
          Escala origen
          <select id="temperature-from" v-model="form.from" class="field-control">
            <option v-for="scale in temperatureScales" :key="scale.value" :value="scale.value">{{ scale.label }}</option>
          </select>
        </label>

        <label class="field-label" for="temperature-to">
          Escala destino
          <select id="temperature-to" v-model="form.to" class="field-control">
            <option v-for="scale in temperatureScales" :key="`to-${scale.value}`" :value="scale.value">{{ scale.label }}</option>
          </select>
        </label>
      </div>

      <div class="form-actions">
        <BaseButton type="button" variant="ghost" class="swap-button" @click="$emit('swap')">Intercambiar escalas</BaseButton>
        <BaseButton type="button" variant="ghost" class="reset-button" @click="$emit('reset')">Resetear parametros</BaseButton>
      </div>
    </div>
  </section>
</template>

<script setup>
import { BaseButton, BaseInput } from '@/components/base'

defineProps({
  form: { type: Object, required: true },
  temperatureScales: { type: Array, required: true }
})

defineEmits(['reset', 'swap'])
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
