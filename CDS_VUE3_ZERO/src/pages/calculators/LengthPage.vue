<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Conversor de Longitud</h1>
        <p>Convierte milímetros, centímetros, metros, kilómetros, pulgadas y pies.</p>
      </header>

      <section class="calc-card">
        <BaseInput
          id="length-value"
          v-model.number="form.value"
          label="Valor"
          type="number"
          inputmode="decimal"
          placeholder="Ej: 1.25"
        />

        <div class="field-grid">
          <label class="field-label" for="length-from">
            Unidad origen
            <select id="length-from" v-model="form.from_unit" class="field-control">
              <option v-for="unit in lengthUnits" :key="unit.value" :value="unit.value">
                {{ unit.label }}
              </option>
            </select>
          </label>

          <label class="field-label" for="length-to">
            Unidad destino
            <select id="length-to" v-model="form.to_unit" class="field-control">
              <option v-for="unit in lengthUnits" :key="`to-${unit.value}`" :value="unit.value">
                {{ unit.label }}
              </option>
            </select>
          </label>
        </div>

        <div class="calc-actions">
          <BaseButton type="button" variant="ghost" class="swap-button" @click="swapUnits">
            Intercambiar unidades
          </BaseButton>
        </div>
      </section>

      <section class="result-card">
        <p v-if="canConvert && result !== null" class="result-value">{{ result }} {{ form.to_unit }}</p>
        <p v-else class="result-hint">Ingresa un valor numérico para ver el resultado.</p>
      </section>

      <router-link to="/calculadoras" class="back-link">Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { BaseButton, BaseInput } from '@new/components/ui'
import { lengthUnits, useLengthCalculator } from '@new/composables/useLengthCalculator'

const { form, canConvert, result } = useLengthCalculator()

function swapUnits() {
  const nextFrom = form.to_unit
  form.to_unit = form.from_unit
  form.from_unit = nextFrom
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
