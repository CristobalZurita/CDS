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
        <svg
          class="resistor-illustration"
          viewBox="0 0 420 140"
          role="img"
          aria-label="Previsualizacion de resistencia THT por codigo de colores"
        >
          <defs>
            <linearGradient id="resistorLeadGradient" x1="0%" x2="0%" y1="0%" y2="100%">
              <stop offset="0%" stop-color="#989898" />
              <stop offset="100%" stop-color="#606060" />
            </linearGradient>
            <linearGradient id="resistorBodyGradient" x1="0%" x2="0%" y1="0%" y2="100%">
              <stop offset="0%" stop-color="#f6e8bf" />
              <stop offset="55%" stop-color="#ecd9a6" />
              <stop offset="100%" stop-color="#e2cb93" />
            </linearGradient>
          </defs>

          <line x1="0" y1="70" x2="62" y2="70" class="resistor-illustration__lead" />
          <line x1="358" y1="70" x2="420" y2="70" class="resistor-illustration__lead" />

          <path
            class="resistor-illustration__body"
            d="M64 44 H98 L108 50 H312 L322 44 H356 L362 70 L356 96 H322 L312 90 H108 L98 96 H64 L58 70 Z"
          />
          <path
            class="resistor-illustration__shine"
            d="M72 49 H95 L104 55 H316 L325 49 H347 L350 60 H70 Z"
          />
          <path
            class="resistor-illustration__shadow"
            d="M70 80 H350 L347 90 H325 L316 84 H104 L95 90 H72 Z"
          />

          <line x1="97" y1="48" x2="97" y2="92" class="resistor-illustration__cap-line" />
          <line x1="323" y1="48" x2="323" y2="92" class="resistor-illustration__cap-line" />

          <rect
            v-for="(item, index) in bandSummaries"
            :key="`${item.roleLabel}-${index}`"
            :x="bandLayout[index].x"
            y="50"
            :width="bandLayout[index].width"
            height="40"
            rx="2.5"
            :fill="item.swatch"
            :stroke="item.borderColor"
            stroke-width="1.2"
          />
        </svg>
      </div>

      <div class="band-summary-grid">
        <div
          v-for="(item, index) in bandSummaries"
          :key="`${item.roleLabel}-${index}`"
          class="band-summary-item"
        >
          <span
            class="band-summary-chip"
            :style="{ background: item.swatch, color: item.textColor, borderColor: item.borderColor }"
          >
            {{ item.valueText }}
          </span>
          <span class="band-summary-label">{{ item.roleLabel }}</span>
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
import { computed } from 'vue'

const props = defineProps({
  bandClass: { type: Function, required: true },
  bandSummaries: { type: Array, required: true },
  previewBands: { type: Array, required: true },
  result: { type: Object, required: true }
})

const bandLayout = computed(() => {
  const count = props.bandSummaries.length

  if (count === 4) {
    return [
      { x: 118, width: 12 },
      { x: 145, width: 12 },
      { x: 243, width: 18 },
      { x: 300, width: 12 }
    ]
  }

  if (count === 5) {
    return [
      { x: 114, width: 12 },
      { x: 138, width: 12 },
      { x: 162, width: 12 },
      { x: 244, width: 18 },
      { x: 300, width: 12 }
    ]
  }

  return [
    { x: 112, width: 11 },
    { x: 134, width: 11 },
    { x: 156, width: 11 },
    { x: 236, width: 17 },
    { x: 286, width: 11 },
    { x: 308, width: 11 }
  ]
})
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
<style scoped src="./resistorColorPageShared.css"></style>
