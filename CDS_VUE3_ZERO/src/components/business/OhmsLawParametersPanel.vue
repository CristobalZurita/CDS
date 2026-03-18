<template>
  <section class="calc-panel">
    <div class="panel-header">
      <div class="panel-title">
        <i class="fa-solid fa-sliders"></i>
        Parametros
      </div>
    </div>

    <div class="panel-body">
      <div class="field-grid">
        <BaseInput id="ohm-voltage" v-model.number="form.voltage_v" label="Voltaje (V)" type="number" inputmode="decimal" min="0" step="0.1" />
        <BaseInput id="ohm-current" v-model.number="form.current_a" label="Corriente (A)" type="number" inputmode="decimal" min="0" step="0.1" />
        <BaseInput id="ohm-resistance" v-model.number="form.resistance_ohm" label="Resistencia (Ohm)" type="number" inputmode="decimal" min="0" step="0.1" />
      </div>

      <div class="form-actions">
        <BaseButton type="button" variant="ghost" class="reset-button" @click="$emit('reset')">Resetear parametros</BaseButton>
      </div>
    </div>
  </section>
</template>

<script setup>
import { BaseButton, BaseInput } from '@/components/base'

defineProps({
  form: {
    type: Object,
    required: true
  }
})

defineEmits(['reset'])
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
