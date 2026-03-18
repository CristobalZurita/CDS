<template>
  <BaseCalculatorPage
    title="Calculadora de Resistencias SMD"
    description="Decodifica resistencias SMD con EIA-3, EIA-4, EIA-96 y notación R."
  >
    <SmdResistorCodeParametersPanel
      :active-examples="activeExamples"
      :apply-example="applyExample"
      :form="form"
      :smd-resistor-type-options="smdResistorTypeOptions"
      @reset="reset"
    />

    <SmdResistorCodeResultPanel
      :decoded="decoded"
      :display-code="displayCode"
      :formatted-resistance="formattedResistance"
      :formula-text="formulaText"
      :is-valid="isValid"
      :mode-label="modeLabel"
    />
  </BaseCalculatorPage>
</template>

<script setup>
import SmdResistorCodeParametersPanel from '@/components/business/SmdResistorCodeParametersPanel.vue'
import SmdResistorCodeResultPanel from '@/components/business/SmdResistorCodeResultPanel.vue'
import { BaseCalculatorPage } from '@/components/base'
import { smdResistorTypeOptions, useSmdResistorCalculator } from '@/composables/useSmdResistorCalculator'

const { form, activeExamples, applyExample, decoded, displayCode, isValid, formattedResistance, formulaText, modeLabel, reset } = useSmdResistorCalculator()
</script>

<style scoped src="./commonCalculatorPage.css"></style>
