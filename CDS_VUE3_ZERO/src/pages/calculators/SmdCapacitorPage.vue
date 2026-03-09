<template>
  <main class="calc-page" id="smd-capacitor-calculator">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Conversión de Capacitancia</h1>
        <p>Conversión de unidades y lectura por código para capacitores SMD.</p>
      </header>

      <div class="cap-layout">
        <section class="cap-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-scale-balanced"></i>
              Conversión de unidades
            </div>
          </div>

          <div class="panel-form">
            <div class="cap-visual-inline">
              <img src="/images/calculadoras/CAP_E.webp" alt="Capacitor electrolítico" />
              <p>Electrolítico (Cap E)</p>
            </div>

            <div class="form-grid form-grid-wide">
              <label class="form-field">
                <span>Picofarad</span>
                <div class="unit-input">
                  <input v-model.number="form.pf" type="number" min="0" step="0.1" @input="convertFrom('pf')" />
                  <span class="unit-tag">pF</span>
                </div>
              </label>

              <label class="form-field">
                <span>Nanofarad</span>
                <div class="unit-input">
                  <input v-model.number="form.nf" type="number" min="0" step="0.1" @input="convertFrom('nf')" />
                  <span class="unit-tag">nF</span>
                </div>
              </label>

              <label class="form-field">
                <span>Microfarad</span>
                <div class="unit-input">
                  <input v-model.number="form.uf" type="number" min="0" step="0.1" @input="convertFrom('uf')" />
                  <span class="unit-tag">µF</span>
                </div>
              </label>

              <label class="form-field">
                <span>Farad</span>
                <div class="unit-input">
                  <input v-model.number="form.f" type="number" min="0" step="0.1" @input="convertFrom('f')" />
                  <span class="unit-tag">F</span>
                </div>
              </label>
            </div>

            <div class="form-actions">
              <button type="button" class="btn-reset" @click="resetConversion">
                <i class="fa-solid fa-rotate-left"></i>
                Resetear parámetros
              </button>
            </div>
          </div>
        </section>

        <section class="cap-panel output-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-hashtag"></i>
              Código cerámico / poliester
            </div>
          </div>

          <div class="panel-form">
            <div class="cap-visual-inline">
              <img src="/images/calculadoras/CAP_C.webp" alt="Capacitor cerámico" />
              <p>Cerámico (Cap C)</p>
            </div>

            <div class="form-grid">
              <label class="form-field">
                <span>Código</span>
                <input v-model.trim="form.code" type="text" placeholder="Ej: 104 o 472" />
              </label>

              <label class="form-field">
                <span>Tipo</span>
                <select v-model="form.type">
                  <option v-for="item in smdCapacitorTypeOptions" :key="item.value" :value="item.value">
                    {{ item.label }}
                  </option>
                </select>
              </label>
            </div>

            <div class="form-actions">
              <button type="button" class="btn-reset" @click="resetCode">
                <i class="fa-solid fa-rotate-left"></i>
                Resetear parámetros
              </button>
            </div>
          </div>

          <div class="output-body">
            <div class="output-values">
              <div class="value-row">
                <span>pF</span>
                <strong>{{ isValidCode ? decoded.pf : '—' }}</strong>
              </div>
              <div class="value-row">
                <span>nF</span>
                <strong>{{ isValidCode ? decoded.nf : '—' }}</strong>
              </div>
              <div class="value-row">
                <span>µF</span>
                <strong>{{ isValidCode ? decoded.uf : '—' }}</strong>
              </div>
            </div>
            <p class="output-hint">El código se interpreta en pF: dos dígitos + cantidad de ceros.</p>
          </div>
        </section>
      </div>

      <router-link to="/calculadoras" class="back-link">← Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { smdCapacitorTypeOptions, useSmdCapacitorCalculator } from '@/composables/useSmdCapacitorCalculator'

const { form, decoded, isValidCode, convertFrom } = useSmdCapacitorCalculator()

function resetConversion() {
  form.pf = null
  form.nf = null
  form.uf = null
  form.f = null
}

function resetCode() {
  form.code = ''
  form.type = 'EIA3'
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

.cap-layout {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 920px) {
  .cap-layout {
    grid-template-columns: minmax(320px, 1fr) minmax(360px, 1.3fr);
    align-items: start;
  }
}

.cap-panel {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(233, 236, 230, 0.7));
  border: 1px solid rgba(62, 60, 56, 0.13);
  border-radius: var(--cds-radius-lg);
  box-shadow: var(--cds-shadow-sm);
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
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

.cap-visual-inline {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.2rem 0 0.35rem;
}

.cap-visual-inline img {
  width: 48px;
  height: 48px;
  object-fit: contain;
}

.cap-visual-inline p {
  margin: 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.form-grid {
  display: grid;
  gap: 0.85rem;
}

.form-grid-wide {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

@media (max-width: 580px) {
  .form-grid-wide {
    grid-template-columns: 1fr;
  }
}

.form-field {
  display: grid;
  gap: 0.3rem;
}

.form-field span {
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-dark);
  letter-spacing: 0.02em;
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

.unit-input {
  display: grid;
  grid-template-columns: 1fr auto;
  border: 1.5px solid rgba(62, 60, 56, 0.25);
  border-radius: 0.5rem;
  overflow: hidden;
  background: var(--cds-white);
}

.unit-input input {
  border: none;
  border-radius: 0;
  min-width: 0;
}

.unit-tag {
  display: inline-flex;
  align-items: center;
  padding: 0 0.7rem;
  border-left: 1px solid rgba(62, 60, 56, 0.2);
  background: rgba(62, 60, 56, 0.05);
  color: var(--cds-dark);
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
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
  padding: 0 1.1rem 1.25rem;
  display: grid;
  gap: 1rem;
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
