<template>
  <article class="timer555-panel output-panel output-panel--center">
    <header class="panel-header">
      <h2 class="panel-title">
        <i class="fa-solid fa-wave-square"></i>
        Conexion real
      </h2>
    </header>

    <div class="output-body">
      <section class="circuit-card" aria-label="Circuito de referencia 555">
        <div class="diagram-stage">
          <img :src="activeDiagramSrc" :alt="activeDiagramAlt" class="diagram-image" />
          <span
            class="diagram-led"
            :class="[`diagram-led--${diagramMode}`, { 'diagram-led--on': outputBlinkOn }]"
          ></span>
        </div>
        <div class="circuit-label">{{ circuitLabel }}</div>
      </section>

      <section class="wave-card" aria-label="Previsualizacion de onda de salida">
        <svg class="wave-svg" viewBox="0 0 332 120" role="img" aria-label="Forma de onda de salida">
          <line x1="18" y1="18" x2="18" y2="102" class="wave-axis" />
          <line x1="18" y1="102" x2="316" y2="102" class="wave-axis" />

          <path v-if="isAstable" :d="`M22 90 H ${waveDutyX} V 34 H 278 V 90 H 310`" class="wave-path" />
          <path v-else-if="isMonostable" d="M22 90 H 98 V 34 H 192 V 90 H 310" class="wave-path" />
          <path
            v-else
            :d="bistableOutputWavePath"
            :class="['wave-path', 'wave-path-output', { 'wave-path-output--high': bistableOutputHigh }]"
          />

          <text x="24" y="28" class="wave-label">{{ isBistable ? 'Salida (0V / 5V)' : 'Pulso' }}</text>
          <text x="284" y="112" class="wave-label">Tiempo</text>
        </svg>
      </section>
    </div>
  </article>
</template>

<script setup>
defineProps({
  activeDiagramSrc: { type: String, default: '' },
  activeDiagramAlt: { type: String, default: '' },
  outputBlinkOn: { type: Boolean, default: false },
  diagramMode: { type: String, default: 'astable' },
  circuitLabel: { type: String, default: '' },
  isAstable: { type: Boolean, default: false },
  isMonostable: { type: Boolean, default: false },
  isBistable: { type: Boolean, default: false },
  waveDutyX: { type: Number, default: 150 },
  bistableOutputWavePath: { type: String, default: '' },
  bistableOutputHigh: { type: Boolean, default: false }
})
</script>

<style scoped src="../../pages/calculators/Timer555Page.css"></style>
