<template>
  <main class="calc-page" id="smd-resistor-calculator">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Calculadora de Resistencias SMD</h1>
        <p>Decodifica resistencias SMD con EIA-3, EIA-4, EIA-96 y notación R.</p>
      </header>

      <div class="smd-layout">
        <section class="smd-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-hashtag"></i>
              Parámetros
            </div>
          </div>

          <div class="panel-form">
            <div class="form-grid">
              <label class="form-field">
                <span>Código SMD</span>
                <input v-model.trim="form.code" type="text" placeholder="Ej: 103, 1001, 01C, 4R7" />
              </label>

              <label class="form-field">
                <span>Formato</span>
                <select v-model="form.type">
                  <option v-for="item in smdResistorTypeOptions" :key="item.value" :value="item.value">
                    {{ item.label }}
                  </option>
                </select>
              </label>
            </div>

            <div class="helper-block">
              <p class="helper-title">Ejemplos rápidos</p>
              <div class="example-list">
                <button
                  v-for="example in activeExamples"
                  :key="example"
                  type="button"
                  class="example-chip"
                  @click="applyExample(example)"
                >
                  {{ example }}
                </button>
              </div>
            </div>

            <div class="helper-block">
              <p class="helper-title">Notación R</p>
              <div class="example-list">
                <button type="button" class="example-chip" @click="applyExample('4R7')">4R7</button>
                <button type="button" class="example-chip" @click="applyExample('R47')">R47</button>
                <button type="button" class="example-chip" @click="applyExample('R604')">R604</button>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" class="btn-reset" @click="reset">
                <i class="fa-solid fa-rotate-left"></i>
                Resetear parámetros
              </button>
            </div>
          </div>
        </section>

        <section class="smd-panel output-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-wave-square"></i>
              Resultado
            </div>
          </div>

          <div class="output-body">
            <div class="image-card">
              <img src="/images/calculadoras/resistencia_smd.webp" alt="Resistencia SMD" />
            </div>

            <div class="chip-preview" :class="{ 'chip-preview--active': isValid }">
              <span class="chip-text">{{ displayCode }}</span>
            </div>

            <div class="output-values">
              <div class="value-row">
                <span>Resistencia</span>
                <strong>{{ isValid ? formattedResistance : '—' }}</strong>
              </div>
              <div class="value-row">
                <span>Modo detectado</span>
                <strong>{{ isValid ? modeLabel : '—' }}</strong>
              </div>
              <div class="value-row">
                <span>Fórmula</span>
                <strong>{{ isValid ? formulaText : '—' }}</strong>
              </div>
              <div class="value-row">
                <span>Código normalizado</span>
                <strong>{{ isValid ? decoded?.normalizedCode : '—' }}</strong>
              </div>
            </div>

            <p class="output-hint" v-if="!isValid">Ingresa un código válido según el formato seleccionado.</p>
          </div>
        </section>
      </div>

      <router-link to="/calculadoras" class="back-link">← Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { smdResistorTypeOptions, useSmdResistorCalculator } from '@/composables/useSmdResistorCalculator'

const { form, decoded, isValid, formattedResistance, formulaText, modeLabel, reset } = useSmdResistorCalculator()

const examplesByType = {
  EIA3: ['103', '472', '221'],
  EIA4: ['1001', '4702', '2493'],
  EIA96: ['01C', '24B', '68X']
}

const activeExamples = computed(() => examplesByType[form.type] || examplesByType.EIA3)

const displayCode = computed(() => {
  const normalized = String(form.code || '').trim().toUpperCase()
  return normalized || 'SMD'
})

function applyExample(example) {
  form.code = example
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
  max-width: 1150px;
  margin: 0 auto;
  display: grid;
  gap: 1.5rem;
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

.smd-layout {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 920px) {
  .smd-layout {
    grid-template-columns: minmax(320px, 1fr) minmax(360px, 1.3fr);
    align-items: start;
  }
}

.smd-panel {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(233, 236, 230, 0.7));
  border: 1px solid rgba(62, 60, 56, 0.13);
  border-radius: var(--cds-radius-lg);
  box-shadow: var(--cds-shadow-sm);
  overflow: hidden;
}

.panel-header {
  padding: 0.85rem 1.1rem;
  background: rgba(62, 60, 56, 0.05);
  border-bottom: 1px solid rgba(62, 60, 56, 0.1);
}

.panel-title {
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--cds-dark);
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.panel-form {
  padding: 1rem 1.1rem 1.25rem;
  display: grid;
  gap: 1rem;
}

.form-grid {
  display: grid;
  gap: 0.85rem;
}

.form-field {
  display: grid;
  gap: 0.3rem;
}

.form-field span {
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-dark);
}

.form-field select,
.form-field input {
  border: 1.5px solid rgba(62, 60, 56, 0.25);
  border-radius: 0.5rem;
  padding: 0.62rem 0.75rem;
  font-size: var(--cds-text-base);
  background: var(--cds-white);
  color: var(--cds-dark);
  outline: none;
  width: 100%;
  box-sizing: border-box;
}

.form-field select:focus,
.form-field input:focus {
  border-color: var(--cds-primary);
}

.helper-block {
  display: grid;
  gap: 0.45rem;
}

.helper-title {
  margin: 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.example-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.example-chip {
  border: 1px solid rgba(62, 60, 56, 0.25);
  background: var(--cds-white);
  color: var(--cds-dark);
  border-radius: 999px;
  min-height: 32px;
  padding: 0 0.7rem;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  cursor: pointer;
}

.form-actions {
  display: flex;
}

.btn-reset {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1rem;
  border-radius: 0.5rem;
  border: 1.5px solid rgba(62, 60, 56, 0.25);
  background: transparent;
  color: var(--cds-dark);
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  cursor: pointer;
}

.output-body {
  padding: 1rem 1.1rem 1.25rem;
  display: grid;
  gap: 1rem;
}

.image-card {
  border-radius: var(--cds-radius-md);
  overflow: hidden;
  border: 1px solid rgba(62, 60, 56, 0.12);
  background: rgba(255, 255, 255, 0.78);
}

.image-card img {
  display: block;
  width: 100%;
  object-fit: cover;
}

.chip-preview {
  min-height: 64px;
  border-radius: 0.8rem;
  border: 1px solid rgba(62, 60, 56, 0.25);
  background: linear-gradient(135deg, #292a2d, #17181a);
  display: flex;
  align-items: center;
  justify-content: center;
}

.chip-preview--active {
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--cds-primary) 45%, transparent) inset;
}

.chip-text {
  color: #f2f2f2;
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.output-values {
  display: grid;
  gap: 0.5rem;
}

.value-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.55rem 0.85rem;
  background: rgba(62, 60, 56, 0.04);
  border-radius: 0.45rem;
  border: 1px solid rgba(62, 60, 56, 0.08);
}

.value-row span {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.value-row strong {
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-primary);
}

.output-hint {
  margin: 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  text-align: center;
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
  font-weight: var(--cds-font-semibold);
  width: fit-content;
  font-size: var(--cds-text-sm);
}
</style>
