<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Conversor de Sistemas Numéricos</h1>
        <p>Convierte valores entre binario, octal, decimal y hexadecimal.</p>
      </header>

      <section class="calc-card">
        <BaseInput
          id="number-system-value"
          v-model.trim="form.value"
          label="Valor de entrada"
          type="text"
          placeholder="Ej: FF o 1010"
        />

        <div class="field-grid">
          <label class="field-label" for="number-system-from">
            Base origen
            <select id="number-system-from" v-model.number="form.from" class="field-control">
              <option v-for="base in numericBaseOptions" :key="base.value" :value="base.value">
                {{ base.label }}
              </option>
            </select>
          </label>

          <label class="field-label" for="number-system-to">
            Base destino
            <select id="number-system-to" v-model.number="form.to" class="field-control">
              <option v-for="base in numericBaseOptions" :key="`to-${base.value}`" :value="base.value">
                {{ base.label }}
              </option>
            </select>
          </label>
        </div>

        <div class="calc-actions">
          <BaseButton type="button" variant="ghost" class="swap-button" @click="swapBases">
            Intercambiar bases
          </BaseButton>
        </div>
      </section>

      <section class="result-card">
        <p v-if="isValid" class="result-value">{{ result }}</p>
        <p v-else class="result-hint">Ingresa un valor válido para la base de origen.</p>
      </section>

      <router-link to="/calculadoras" class="back-link">Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { BaseButton, BaseInput } from '@new/components/ui'
import { numericBaseOptions, useNumberSystemCalculator } from '@new/composables/useNumberSystemCalculator'

const { form, isValid, result } = useNumberSystemCalculator()

function swapBases() {
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
  overflow-wrap: anywhere;
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
