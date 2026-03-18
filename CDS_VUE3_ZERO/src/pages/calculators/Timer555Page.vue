<template>
  <main class="calc-page" id="timer-555-calculator">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Calculadora Timer 555</h1>
        <p>Astable, monostable y biestable con conexiones reales del CI 555.</p>
      </header>

      <div class="timer555-layout">
        <Timer555ParametersPanel
          :form="form"
          :is-astable="isAstable"
          :is-bistable="isBistable"
          :is-monostable="isMonostable"
          :timer555-mode-options="timer555ModeOptions"
          @reset="reset"
        />

        <Timer555CircuitPanel
          :active-diagram-src="activeDiagramSrc"
          :active-diagram-alt="activeDiagramAlt"
          :output-blink-on="outputBlinkOn"
          :diagram-mode="diagramMode"
          :circuit-label="circuitLabel"
          :is-astable="isAstable"
          :is-monostable="isMonostable"
          :is-bistable="isBistable"
          :wave-duty-x="waveDutyX"
          :bistable-output-wave-path="bistableOutputWavePath"
          :bistable-output-high="bistableOutputHigh"
        />

        <Timer555OutputPanel
          :is-astable="isAstable"
          :is-monostable="isMonostable"
          :is-bistable="isBistable"
          :formatted-frequency="formattedFrequency"
          :formatted-high="formattedHigh"
          :formatted-low="formattedLow"
          :formatted-duty="formattedDuty"
          :formatted-period="formattedPeriod"
          :formatted-pulse="formattedPulse"
          :bistable-next-pulse-label="bistableNextPulseLabel"
          :bistable-output-high="bistableOutputHigh"
          :bistable-state-label="bistableStateLabel"
          :push-pressed="pushPressed"
          :result-summary="resultSummary"
          @trigger-bistable-pulse="triggerBistablePulse"
        />
      </div>

      <router-link to="/calculadoras" class="back-link">← Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import Timer555CircuitPanel from '@/components/business/Timer555CircuitPanel.vue'
import Timer555OutputPanel from '@/components/business/Timer555OutputPanel.vue'
import Timer555ParametersPanel from '@/components/business/Timer555ParametersPanel.vue'
import { useTimer555Page } from '@/composables/useTimer555Page'

const {
  activeDiagramAlt,
  activeDiagramSrc,
  bistableNextPulseLabel,
  bistableOutputHigh,
  bistableOutputWavePath,
  bistableStateLabel,
  circuitLabel,
  diagramMode,
  form,
  formattedDuty,
  formattedFrequency,
  formattedHigh,
  formattedLow,
  formattedPeriod,
  formattedPulse,
  isAstable,
  isBistable,
  isMonostable,
  outputBlinkOn,
  pushPressed,
  reset,
  resultSummary,
  timer555ModeOptions,
  triggerBistablePulse,
  waveDutyX,
} = useTimer555Page()
</script>

<style scoped src="./commonCalculatorPage.css"></style>
<style scoped src="./Timer555Page.css"></style>
