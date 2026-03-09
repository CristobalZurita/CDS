<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Código de Colores de Resistencias</h1>
        <p>Calcula valor y tolerancia para resistencias de 4, 5 y 6 bandas.</p>
      </header>

      <section class="calc-card">
        <div class="band-tabs">
          <button
            v-for="bands in [4, 5, 6]"
            :key="bands"
            type="button"
            class="band-tab"
            :class="{ active: form.bands === bands }"
            @click="setBands(bands)"
          >
            {{ bands }} bandas
          </button>
        </div>

        <div class="field-grid">
          <label class="field-label">
            Banda 1
            <select v-model="form.colors[0]" class="field-control">
              <option v-for="color in digitColorOptions" :key="`d1-${color.value}`" :value="color.value">
                {{ color.label }}
              </option>
            </select>
          </label>

          <label class="field-label">
            Banda 2
            <select v-model="form.colors[1]" class="field-control">
              <option v-for="color in digitColorOptions" :key="`d2-${color.value}`" :value="color.value">
                {{ color.label }}
              </option>
            </select>
          </label>

          <label v-if="form.bands >= 5" class="field-label">
            Banda 3
            <select v-model="form.colors[2]" class="field-control">
              <option v-for="color in digitColorOptions" :key="`d3-${color.value}`" :value="color.value">
                {{ color.label }}
              </option>
            </select>
          </label>

          <label class="field-label">
            Multiplicador
            <select v-model="form.colors[multiplierIndex]" class="field-control">
              <option v-for="color in multiplierColorOptions" :key="`m-${color.value}`" :value="color.value">
                {{ color.label }}
              </option>
            </select>
          </label>

          <label class="field-label">
            Tolerancia
            <select v-model="form.colors[toleranceIndex]" class="field-control">
              <option v-for="color in toleranceColorOptions" :key="`t-${color.value}`" :value="color.value">
                {{ color.label }}
              </option>
            </select>
          </label>

          <label v-if="form.bands === 6" class="field-label">
            Tempco
            <select v-model="form.colors[tempcoIndex]" class="field-control">
              <option v-for="color in tempcoColorOptions" :key="`tc-${color.value}`" :value="color.value">
                {{ color.label }}
              </option>
            </select>
          </label>
        </div>
      </section>

      <section class="result-card">
        <p class="result-value">Resistencia: {{ result.formattedResistance }}</p>
        <p class="result-value">Tolerancia: ±{{ result.tolerance_percent }}%</p>
        <p class="result-value">Rango: {{ result.formattedRange }}</p>
        <p v-if="result.tempco_ppm" class="result-value">Tempco: {{ result.tempco_ppm }} ppm</p>
      </section>

      <router-link to="/calculadoras" class="back-link">Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import {
  digitColorOptions,
  multiplierColorOptions,
  toleranceColorOptions,
  tempcoColorOptions,
  useResistorColorCalculator
} from '@/composables/useResistorColorCalculator'

const { form, multiplierIndex, toleranceIndex, tempcoIndex, result, setBands } = useResistorColorCalculator()
</script>

<style scoped>
.calc-page { padding: 1rem; }
.calc-container { max-width: 1040px; margin: 0 auto; display: grid; gap: 1rem; }
.calc-header h1 { margin: 0; font-size: var(--cds-text-3xl); line-height: var(--cds-leading-tight); }
.calc-header p { margin: 0.4rem 0 0; color: var(--cds-text-muted); font-size: var(--cds-text-base); }
.calc-card, .result-card { background: var(--cds-white); border: 1px solid color-mix(in srgb, var(--cds-light) 75%, white); border-radius: 0.8rem; padding: 1rem; }
.band-tabs { display: flex; gap: 0.5rem; margin-bottom: 0.9rem; flex-wrap: wrap; }
.band-tab { min-height: 40px; padding: 0.4rem 0.8rem; border-radius: 0.5rem; border: 1px solid var(--cds-light-4); background: var(--cds-white); cursor: pointer; }
.band-tab.active { background: color-mix(in srgb, var(--cds-primary) 14%, white); border-color: var(--cds-primary); color: var(--cds-primary); }
.field-grid { display: grid; gap: 0.75rem; }
.field-label { display: grid; gap: 0.35rem; font-size: var(--cds-text-sm); font-weight: var(--cds-font-medium); color: var(--cds-text-normal); }
.field-control { min-height: 44px; border: 2px solid var(--cds-light-4); border-radius: 0.5rem; padding: 0.75rem 0.875rem; font-size: var(--cds-text-base); background: var(--cds-white); color: var(--cds-text-normal); }
.result-value { margin: 0.2rem 0; font-size: var(--cds-text-lg); color: var(--cds-primary); font-weight: var(--cds-font-semibold); }
.back-link { display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 0.65rem 1rem; border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, white); border-radius: 0.6rem; text-decoration: none; color: var(--cds-primary); width: fit-content; }
@media (min-width: 768px) { .field-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
