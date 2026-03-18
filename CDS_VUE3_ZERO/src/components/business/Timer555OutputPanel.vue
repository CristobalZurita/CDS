<template>
  <article class="timer555-panel output-panel output-panel--right">
    <header class="panel-header">
      <h2 class="panel-title">
        <i class="fa-solid fa-circle-info"></i>
        Modo y salida
      </h2>
    </header>

    <div class="output-body">
      <div class="output-values" v-if="!isBistable">
        <div class="value-row">
          <span>Frecuencia</span>
          <strong>{{ formattedFrequency }}</strong>
        </div>

        <div class="value-row" v-if="isAstable">
          <span>Tiempo alto</span>
          <strong>{{ formattedHigh }}</strong>
        </div>

        <div class="value-row" v-if="isAstable">
          <span>Tiempo bajo</span>
          <strong>{{ formattedLow }}</strong>
        </div>

        <div class="value-row" v-if="isAstable">
          <span>Ciclo de trabajo</span>
          <strong>{{ formattedDuty }}</strong>
        </div>

        <div class="value-row" v-if="isAstable">
          <span>Periodo</span>
          <strong>{{ formattedPeriod }}</strong>
        </div>

        <div class="value-row" v-if="isMonostable">
          <span>Duracion del pulso</span>
          <strong>{{ formattedPulse }}</strong>
        </div>
      </div>

      <div class="output-values" v-else>
        <section class="bistable-guide">
          <h3>Como usar modo biestable</h3>
          <p>1. Parte en RESET (salida en 0 V).</p>
          <p>2. Cada click en el pulsador envia un pulso y alterna <strong>SET / RESET</strong>.</p>
          <p>3. Pulso siguiente: <strong>{{ bistableNextPulseLabel }}</strong>.</p>
          <p>4. La salida en pin 3 queda memorizada en <strong>{{ bistableOutputHigh ? 'HIGH (5V)' : 'LOW (0V)' }}</strong>.</p>
          <p class="bistable-guide-note">No parpadea sola; cambia solo con SET o RESET.</p>
        </section>

        <div class="value-row">
          <span>SET</span>
          <strong>Pin 2 a nivel bajo</strong>
        </div>
        <div class="value-row">
          <span>RESET</span>
          <strong>Pin 4 a nivel bajo</strong>
        </div>
        <div class="value-row">
          <span>Salida (pin 3)</span>
          <strong>{{ bistableOutputHigh ? 'HIGH (5V)' : 'LOW (0V)' }}</strong>
        </div>

        <div class="bistable-controls">
          <button
            type="button"
            class="bistable-btn"
            :class="{ 'bistable-btn--active': bistableStateLabel === 'SET' }"
            disabled
          >Seleccionar SET</button>
          <button
            type="button"
            class="bistable-btn"
            :class="{ 'bistable-btn--active': bistableStateLabel === 'RESET' }"
            disabled
          >Seleccionar RESET</button>
        </div>

        <button
          type="button"
          class="push-trigger"
          :class="{ 'push-trigger--pressed': pushPressed }"
          @click="$emit('trigger-bistable-pulse')"
        >
          <img src="/images/calculadoras/push.webp" alt="Pulsador virtual SET RESET" class="push-image" />
          <span class="push-text">
            {{ `Presionar pulsador (pulso a ${bistableNextPulseLabel})` }}
          </span>
        </button>
      </div>

      <p class="output-hint">{{ resultSummary }}</p>
    </div>
  </article>
</template>

<script setup>
defineProps({
  isAstable: { type: Boolean, default: false },
  isMonostable: { type: Boolean, default: false },
  isBistable: { type: Boolean, default: false },
  formattedFrequency: { type: String, default: '—' },
  formattedHigh: { type: String, default: '—' },
  formattedLow: { type: String, default: '—' },
  formattedDuty: { type: String, default: '—' },
  formattedPeriod: { type: String, default: '—' },
  formattedPulse: { type: String, default: '—' },
  bistableNextPulseLabel: { type: String, default: 'SET' },
  bistableOutputHigh: { type: Boolean, default: false },
  bistableStateLabel: { type: String, default: 'RESET' },
  pushPressed: { type: Boolean, default: false },
  resultSummary: { type: String, default: '' }
})

defineEmits(['trigger-bistable-pulse'])
</script>

<style scoped src="../../pages/calculators/Timer555Page.css"></style>
