<template>
  <article class="ohm-scene-card">
    <div class="ohm-scene-stage">
      <img
        class="ohm-scene-image"
        :src="sceneImageUrl"
        alt="Portada interactiva de la calculadora de Ley de Ohm"
        loading="eager"
        decoding="async"
      />
    </div>
  </article>
</template>

<script setup>
import { useCloudinaryImage } from '@/composables/useCloudinary'

const sceneImageUrl = useCloudinaryImage('/images/calculadoras/leyohm.webp')
</script>

<style scoped src="../../pages/calculators/OhmsLawPage.css"></style>
