<template>
  <BaseCalculatorPage
    title="Oscilador CD40106"
    description="Schmitt trigger con R y C para estimar frecuencia y periodo."
  >
    <Cd40106ParametersPanel
      :form="form"
      :pinout-src="pinoutSrc"
      @reset="reset"
    />

    <Cd40106OutputPanel
      :formatted-frequency="formattedFrequency"
      :formatted-period="formattedPeriod"
      :set-canvas-element="setCanvasElement"
    />
  </BaseCalculatorPage>
</template>

<script setup>
import Cd40106OutputPanel from '@/components/business/Cd40106OutputPanel.vue'
import Cd40106ParametersPanel from '@/components/business/Cd40106ParametersPanel.vue'
import { BaseCalculatorPage } from '@/components/base'
import { useCd40106Calculator } from '@/composables/useCd40106Calculator'
import { useCloudinaryImage } from '@/composables/useCloudinary'

const { form, formattedFrequency, formattedPeriod, reset, setCanvasElement } = useCd40106Calculator()
const pinoutSrc = useCloudinaryImage('/images/calculadoras/CD40106.webp')
</script>

<style scoped src="./commonCalculatorPage.css"></style>
