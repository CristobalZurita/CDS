<template>
  <section class="calc-panel">
    <div class="panel-header">
      <div class="panel-title">
        <i class="fa-solid fa-wave-square"></i>
        Resultado
      </div>
    </div>

    <div class="panel-body">
      <div class="resistor-visual">
        <div class="resistor-body">
          <span
            v-for="(color, index) in previewBands"
            :key="`${color}-${index}`"
            :class="['band', bandClass(color)]"
          ></span>
        </div>
      </div>

      <div class="output-values">
        <div class="value-row">
          <span>Resistencia</span>
          <strong>{{ result.formattedResistance }}</strong>
        </div>
        <div class="value-row">
          <span>Tolerancia</span>
          <strong>±{{ result.tolerance_percent }}%</strong>
        </div>
        <div class="value-row">
          <span>Rango</span>
          <strong>{{ result.formattedRange }}</strong>
        </div>
        <div class="value-row" v-if="result.tempco_ppm">
          <span>Tempco</span>
          <strong>{{ result.tempco_ppm }} ppm</strong>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  bandClass: { type: Function, required: true },
  previewBands: { type: Array, required: true },
  result: { type: Object, required: true }
})
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
<style scoped src="./resistorColorPageShared.css"></style>
