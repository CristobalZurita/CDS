<template>
  <article class="meter-card">
    <header class="meter-head">
      <span>{{ label }}</span>
      <strong>{{ value }} {{ unit }}</strong>
    </header>
    <div class="meter-track">
      <span class="meter-fill" :class="`meter-fill--${tone}`"></span>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, default: '' },
  value: { type: [Number, String], default: 0 },
  unit: { type: String, default: '' },
  percent: { type: Number, default: 0 },
  tone: { type: String, default: 'voltage' }
})

const fillWidth = computed(() => `${props.percent}%`)
</script>

<style scoped src="../../pages/calculators/OhmsLawPage.css"></style>
<style scoped>
.meter-fill {
  width: v-bind(fillWidth);
}

.meter-fill--voltage {
  background: #ec6b00;
}

.meter-fill--current {
  background: #2b8bd7;
}

.meter-fill--resistance {
  background: #5b4a3f;
}

.meter-fill--power {
  background: #ce3f2a;
}
</style>
