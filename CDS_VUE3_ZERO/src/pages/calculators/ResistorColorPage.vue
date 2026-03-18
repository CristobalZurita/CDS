<template>
  <BaseCalculatorPage
    title="Calculadora de Resistencias"
    description="Código de colores para resistencias THT/DIP de 4, 5 y 6 bandas."
  >
    <ResistorColorParametersPanel
      :digit-color-options="digitColorOptions"
      :form="form"
      :multiplier-color-options="multiplierColorOptions"
      :multiplier-index="multiplierIndex"
      :tempco-color-options="tempcoColorOptions"
      :tempco-index="tempcoIndex"
      :tolerance-color-options="toleranceColorOptions"
      :tolerance-index="toleranceIndex"
      @apply-bands="applyBands"
      @reset-bands="resetBands"
    />

    <ResistorColorResultPanel
      :band-class="bandClass"
      :preview-bands="previewBands"
      :result="result"
    />
  </BaseCalculatorPage>
</template>

<script setup>
import ResistorColorParametersPanel from '@/components/business/ResistorColorParametersPanel.vue'
import ResistorColorResultPanel from '@/components/business/ResistorColorResultPanel.vue'
import { BaseCalculatorPage } from '@/components/base'
import {
  digitColorOptions,
  multiplierColorOptions,
  toleranceColorOptions,
  tempcoColorOptions,
  useResistorColorCalculator,
} from '@/composables/useResistorColorCalculator'

const { applyBands, bandClass, form, multiplierIndex, previewBands, resetBands, result, tempcoIndex, toleranceIndex } = useResistorColorCalculator()
</script>

<style scoped src="./commonCalculatorPage.css"></style>
