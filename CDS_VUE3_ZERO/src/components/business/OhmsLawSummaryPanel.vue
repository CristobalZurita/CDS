<template>
  <section class="calc-panel">
    <div class="panel-header">
      <div class="panel-title">
        <i class="fa-solid fa-bolt"></i>
        Resultado
      </div>
    </div>

    <div class="panel-body">
      <div class="meter-grid meter-grid--summary">
        <OhmsLawMeterCard
          v-for="meter in meterItems"
          :key="meter.key"
          :label="meter.label"
          :value="meter.value"
          :unit="meter.unit"
          :percent="meter.percent"
          :tone="meter.tone"
        />
      </div>

      <p v-if="!canCalculate" class="result-hint">Completa al menos 2 campos numericos.</p>
    </div>
  </section>
</template>

<script setup>
import OhmsLawMeterCard from '@/components/business/OhmsLawMeterCard.vue'

defineProps({
  canCalculate: { type: Boolean, default: false },
  meterItems: { type: Array, required: true }
})
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
<style scoped src="../../pages/calculators/OhmsLawPage.css"></style>
