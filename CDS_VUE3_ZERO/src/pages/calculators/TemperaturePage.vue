<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Convertidor de Temperatura</h1>
        <p>Convierte entre Celsius, Fahrenheit, Kelvin y Rankine.</p>
      </header>

      <section class="calc-card">
        <BaseInput
          id="temperature-value"
          v-model.number="form.value"
          label="Valor"
          type="number"
          inputmode="decimal"
          placeholder="Ej: 25"
        />

        <div class="field-grid">
          <label class="field-label" for="temperature-from">
            Escala origen
            <select id="temperature-from" v-model="form.from" class="field-control">
              <option v-for="scale in temperatureScales" :key="scale.value" :value="scale.value">
                {{ scale.label }}
              </option>
            </select>
          </label>

          <label class="field-label" for="temperature-to">
            Escala destino
            <select id="temperature-to" v-model="form.to" class="field-control">
              <option v-for="scale in temperatureScales" :key="`to-${scale.value}`" :value="scale.value">
                {{ scale.label }}
              </option>
            </select>
          </label>
        </div>

        <div class="calc-actions">
          <BaseButton type="button" variant="ghost" class="swap-button" @click="swapScales">
            Intercambiar escalas
          </BaseButton>
        </div>
      </section>

      <section class="result-card">
        <p v-if="canConvert" class="result-value">{{ result }} °{{ form.to }}</p>
        <p v-else class="result-hint">Ingresa un valor numérico para ver el resultado.</p>
      </section>

      <router-link to="/calculadoras" class="back-link">Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { BaseButton, BaseInput } from '@/components/ui'
import { temperatureScales, useTemperatureCalculator } from '@/composables/useTemperatureCalculator'

const { form, canConvert, result } = useTemperatureCalculator()

function swapScales() {
  const nextFrom = form.to
  form.to = form.from
  form.from = nextFrom
}
</script>

<style scoped>
.calc-page {
  padding: 1rem;
}

.calc-container {
  max-width: 960px;
  margin: 0 auto;
  display: grid;
  gap: 1rem;
}

.calc-header h1 {
  margin: 0;
  font-size: var(--cds-text-3xl);
  line-height: var(--cds-leading-tight);
}

.calc-header p {
  margin: 0.4rem 0 0;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-base);
}

.calc-card,
.result-card {
  background: var(--cds-white);
  border: 1px solid color-mix(in srgb, var(--cds-light) 75%, white);
  border-radius: 0.8rem;
  padding: 1rem;
}

.calc-card {
  display: grid;
  gap: 0.9rem;
}

.field-grid {
  display: grid;
  gap: 0.75rem;
}

.field-label {
  display: grid;
  gap: 0.35rem;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-medium);
  color: var(--cds-text-normal);
}

.field-control {
  min-height: 44px;
  border: 2px solid var(--cds-light-4);
  border-radius: 0.5rem;
  padding: 0.75rem 0.875rem;
  font-size: var(--cds-text-base);
  background: var(--cds-white);
  color: var(--cds-text-normal);
}

.calc-actions {
  display: flex;
  gap: 0.75rem;
}

.swap-button {
  width: auto;
}

.result-value {
  margin: 0;
  font-size: var(--cds-text-2xl);
  line-height: var(--cds-leading-tight);
  color: var(--cds-primary);
  font-weight: var(--cds-font-semibold);
}

.result-hint {
  margin: 0;
  font-size: var(--cds-text-base);
  color: var(--cds-text-muted);
}

.back-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.65rem 1rem;
  border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, white);
  border-radius: 0.6rem;
  text-decoration: none;
  color: var(--cds-primary);
  width: fit-content;
}

@media (min-width: 768px) {
  .field-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
