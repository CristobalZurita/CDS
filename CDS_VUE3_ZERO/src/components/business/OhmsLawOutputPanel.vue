<template>
  <section class="calc-panel output-panel">
    <div class="panel-header">
      <div class="panel-title">
        <i class="fa-solid fa-wave-square"></i>
        Referencia
      </div>
    </div>

    <div class="panel-body">
      <OhmsLawScene />

      <div class="formula-grid formula-grid--scene">
        <article
          v-for="formula in formulaCards"
          :key="formula.key"
          class="formula-card"
          :class="{ 'formula-card--active': highlightedFormulas.includes(formula.key) }"
        >
          <span>{{ formula.title }}</span>
          <strong>{{ formula.expression }}</strong>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
import OhmsLawScene from '@/components/business/OhmsLawScene.vue'

defineProps({
  formulaCards: { type: Array, required: true },
  highlightedFormulas: { type: Array, required: true }
})
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
<style scoped src="../../pages/calculators/OhmsLawPage.css"></style>
