<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Conversor de Sistemas Numéricos</h1>
        <p>Convierte valores entre binario, octal, decimal y hexadecimal.</p>
      </header>

      <div class="calc-layout">
        <section class="calc-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-hashtag"></i>
              Parámetros
            </div>
          </div>

          <div class="panel-body panel-form">
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
                  <option v-for="base in numericBaseOptions" :key="base.value" :value="base.value">{{ base.label }}</option>
                </select>
              </label>

              <label class="field-label" for="number-system-to">
                Base destino
                <select id="number-system-to" v-model.number="form.to" class="field-control">
                  <option v-for="base in numericBaseOptions" :key="`to-${base.value}`" :value="base.value">{{ base.label }}</option>
                </select>
              </label>
            </div>

            <div class="form-actions">
              <BaseButton type="button" variant="ghost" class="swap-button" @click="swapBases">Intercambiar bases</BaseButton>
              <BaseButton type="button" variant="ghost" class="reset-button" @click="reset">Resetear parámetros</BaseButton>
            </div>
          </div>
        </section>

        <section class="calc-panel output-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-wave-square"></i>
              Resultado
            </div>
          </div>

          <div class="panel-body">
            <div v-if="isValid" class="output-values">
              <div class="value-row">
                <span>Conversión</span>
                <strong>{{ result }}</strong>
              </div>
            </div>
            <p v-else class="result-hint">Ingresa un valor válido para la base de origen.</p>
          </div>
        </section>
      </div>

      <router-link to="/calculadoras" class="back-link">← Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { BaseButton, BaseInput } from '@/components/ui'
import { numericBaseOptions, useNumberSystemCalculator } from '@/composables/useNumberSystemCalculator'

const { form, isValid, result, reset } = useNumberSystemCalculator()

function swapBases() {
  const nextFrom = form.to
  form.to = form.from
  form.from = nextFrom
}
</script>

<style scoped>
.calc-page {
  padding: var(--cds-space-xl) var(--cds-space-md) var(--cds-space-2xl);
  background:
    radial-gradient(circle at top left, rgba(236, 107, 0, 0.1), transparent 35%),
    radial-gradient(circle at bottom right, rgba(3, 134, 0, 0.06), transparent 28%);
}

.calc-container {
  max-width: 980px;
  margin: 0 auto;
  display: grid;
  gap: 1.25rem;
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

.calc-layout {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 860px) {
  .calc-layout {
    grid-template-columns: minmax(300px, 1fr) minmax(320px, 1fr);
  }
}

.calc-panel {
  border: 1px solid rgba(62, 60, 56, 0.13);
  border-radius: var(--cds-radius-lg);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(233, 236, 230, 0.7));
  box-shadow: var(--cds-shadow-sm);
  overflow: hidden;
}

.panel-header {
  padding: 0.85rem 1.1rem;
  border-bottom: 1px solid rgba(62, 60, 56, 0.1);
  background: rgba(62, 60, 56, 0.05);
}

.panel-title {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--cds-dark);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: var(--cds-font-semibold);
  font-size: var(--cds-text-sm);
}

.panel-body {
  padding: 1rem 1.1rem 1.2rem;
}

.panel-form {
  display: grid;
  gap: 0.9rem;
}

.field-grid {
  display: grid;
  gap: 0.75rem;
}

@media (min-width: 560px) {
  .field-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
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
  border: 1.5px solid rgba(62, 60, 56, 0.25);
  border-radius: 0.5rem;
  padding: 0.75rem 0.875rem;
  font-size: var(--cds-text-base);
  background: var(--cds-white);
  color: var(--cds-text-normal);
}

.form-actions {
  display: flex;
}

.swap-button {
  width: auto;
}

.reset-button {
  width: auto;
}

.output-values {
  display: grid;
  gap: 0.5rem;
}

.value-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.55rem 0.85rem;
  border: 1px solid rgba(62, 60, 56, 0.08);
  border-radius: 0.45rem;
  background: rgba(62, 60, 56, 0.04);
}

.value-row span {
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
}

.value-row strong {
  color: var(--cds-primary);
  font-size: var(--cds-text-base);
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
  border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, transparent);
  border-radius: 0.6rem;
  text-decoration: none;
  color: var(--cds-primary);
  width: fit-content;
  font-weight: var(--cds-font-semibold);
  font-size: var(--cds-text-sm);
}
</style>
