<template>
  <section class="calc-panel calculator-reference-panel">
    <div class="panel-header">
      <div class="panel-title">
        <i :class="icon"></i>
        {{ title }}
      </div>
    </div>

    <div class="panel-body">
      <div class="diagram-card calculator-reference-card">
        <img :src="imageSrc" :alt="alt" />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useCloudinaryImage } from '@/composables/useCloudinary'

const props = defineProps({
  alt: { type: String, required: true },
  icon: { type: String, default: 'fa-solid fa-image' },
  imagePath: { type: String, required: true },
  title: { type: String, default: 'Referencia' }
})

const imageSrc = computed(() => useCloudinaryImage(props.imagePath))
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
<style scoped>
.calculator-reference-card {
  min-height: 18rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(62, 60, 56, 0.04);
}

.calculator-reference-card img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>
