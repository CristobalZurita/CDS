<template>
  <BaseCalculatorPage
    title="Conversión de Capacitancia"
    description="Conversión de unidades y lectura por código para capacitores SMD."
  >
    <SmdCapacitorConversionPanel
      :convert-from="convertFrom"
      :form="form"
      @reset-conversion="resetConversion"
    />

    <SmdCapacitorCodePanel
      :decoded="decoded"
      :form="form"
      :is-valid-code="isValidCode"
      :smd-capacitor-type-options="smdCapacitorTypeOptions"
      @reset-code="resetCode"
    />
  </BaseCalculatorPage>
</template>

<script setup>
import SmdCapacitorCodePanel from '@/components/business/SmdCapacitorCodePanel.vue'
import SmdCapacitorConversionPanel from '@/components/business/SmdCapacitorConversionPanel.vue'
import { BaseCalculatorPage } from '@/components/base'
import { smdCapacitorTypeOptions, useSmdCapacitorCalculator } from '@/composables/useSmdCapacitorCalculator'

const { form, decoded, isValidCode, convertFrom, resetCode, resetConversion } = useSmdCapacitorCalculator()
</script>

<style scoped src="./commonCalculatorPage.css"></style>
