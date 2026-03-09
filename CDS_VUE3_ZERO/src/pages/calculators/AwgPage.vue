<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Calculadora AWG</h1>
        <p>Convierte calibre AWG a diámetro, área y resistencia por kilómetro.</p>
      </header>

      <section class="calc-card">
        <BaseInput
          id="awg-value"
          v-model.number="form.awg"
          label="Calibre AWG"
          type="number"
          inputmode="numeric"
          placeholder="Ej: 24"
        />
      </section>

      <section class="result-card">
        <template v-if="canCalculate && result">
          <p class="result-value">Diámetro: {{ result.diameter_mm }} mm</p>
          <p class="result-value">Área: {{ result.area_mm2 }} mm²</p>
          <p class="result-value">Resistencia: {{ result.resistance_ohm_per_km }} Ω/km</p>
        </template>
        <p v-else class="result-hint">Ingresa un AWG válido.</p>
      </section>

      <router-link to="/calculadoras" class="back-link">Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { BaseInput } from '@/components/ui'
import { useAwgCalculator } from '@/composables/useAwgCalculator'

const { form, canCalculate, result } = useAwgCalculator()
</script>

<style scoped>
.calc-page { padding: 1rem; }
.calc-container { max-width: 960px; margin: 0 auto; display: grid; gap: 1rem; }
.calc-header h1 { margin: 0; font-size: var(--cds-text-3xl); line-height: var(--cds-leading-tight); }
.calc-header p { margin: 0.4rem 0 0; color: var(--cds-text-muted); font-size: var(--cds-text-base); }
.calc-card, .result-card { background: var(--cds-white); border: 1px solid color-mix(in srgb, var(--cds-light) 75%, white); border-radius: 0.8rem; padding: 1rem; }
.result-value { margin: 0.2rem 0; font-size: var(--cds-text-lg); color: var(--cds-primary); font-weight: var(--cds-font-semibold); }
.result-hint { margin: 0; font-size: var(--cds-text-base); color: var(--cds-text-muted); }
.back-link { display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 0.65rem 1rem; border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, white); border-radius: 0.6rem; text-decoration: none; color: var(--cds-primary); width: fit-content; }
</style>
