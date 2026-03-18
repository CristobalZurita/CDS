<template>
  <section class="calc-panel cd40106-output">
    <div class="panel-header">
      <div class="panel-title">
        <i class="fa-solid fa-wave-square"></i>
        Resultado
      </div>
    </div>

    <div class="panel-body">
      <div class="circuit-card">
        <canvas :ref="setCanvasElement" class="circuit-canvas" width="420" height="260" />
        <div class="circuit-label">Oscilador Schmitt</div>
      </div>

      <div class="output-values">
        <div class="value-row">
          <span>Frecuencia</span>
          <strong>{{ formattedFrequency }}</strong>
        </div>
        <div class="value-row">
          <span>Periodo</span>
          <strong>{{ formattedPeriod }}</strong>
        </div>
      </div>

      <p class="result-hint">La frecuencia es aproximada y cambia al ajustar R y C.</p>
    </div>
  </section>
</template>

<script setup>
defineProps({
  formattedFrequency: { type: String, default: '-' },
  formattedPeriod: { type: String, default: '-' },
  setCanvasElement: { type: Function, required: true }
})
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
<style scoped src="./cd40106PageShared.css"></style>
