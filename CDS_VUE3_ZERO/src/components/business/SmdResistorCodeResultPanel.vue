<template>
  <section class="calc-panel">
    <div class="panel-header">
      <div class="panel-title">
        <i class="fa-solid fa-wave-square"></i>
        Resultado
      </div>
    </div>

    <div class="panel-body">
      <div class="diagram-card">
        <img src="/images/calculadoras/resistencia_smd.webp" alt="Resistencia SMD" />
      </div>

      <div class="chip-preview" :class="{ 'chip-preview--active': isValid }">
        <span class="chip-text">{{ displayCode }}</span>
      </div>

      <div class="output-values">
        <div class="value-row">
          <span>Resistencia</span>
          <strong>{{ isValid ? formattedResistance : '-' }}</strong>
        </div>
        <div class="value-row">
          <span>Modo detectado</span>
          <strong>{{ isValid ? modeLabel : '-' }}</strong>
        </div>
        <div class="value-row">
          <span>Formula</span>
          <strong>{{ isValid ? formulaText : '-' }}</strong>
        </div>
        <div class="value-row">
          <span>Codigo normalizado</span>
          <strong>{{ isValid ? decoded?.normalizedCode : '-' }}</strong>
        </div>
      </div>

      <p v-if="!isValid" class="result-hint">Ingresa un codigo valido segun el formato seleccionado.</p>
    </div>
  </section>
</template>

<script setup>
defineProps({
  decoded: { type: Object, default: null },
  displayCode: { type: String, default: 'SMD' },
  formattedResistance: { type: String, default: '-' },
  formulaText: { type: String, default: '-' },
  isValid: { type: Boolean, default: false },
  modeLabel: { type: String, default: '-' }
})
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
<style scoped src="./smdResistorCodePageShared.css"></style>
