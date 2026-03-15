<template>
  <BaseCalculatorPage
    title="Conversión de Capacitancia"
    description="Conversión de unidades y lectura por código para capacitores SMD."
  >
    <section class="calc-panel">
      <div class="panel-header">
        <div class="panel-title">
          <i class="fa-solid fa-scale-balanced"></i>
          Conversión de unidades
        </div>
      </div>

      <div class="panel-body">
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
          <button type="button" class="action-btn" @click="resetConversion">
            <i class="fa-solid fa-rotate-left"></i>
            Resetear parámetros
          </button>
        </div>
      </div>
    </section>

    <section class="calc-panel">
      <div class="panel-header">
        <div class="panel-title">
          <i class="fa-solid fa-hashtag"></i>
          Código cerámico / poliester
        </div>
      </div>

      <div class="panel-body">
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
          <button type="button" class="action-btn" @click="resetCode">
            <i class="fa-solid fa-rotate-left"></i>
            Resetear parámetros
          </button>
        </div>

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

        <p class="result-hint">El código se interpreta en pF: dos dígitos + cantidad de ceros.</p>
      </div>
    </section>
  </BaseCalculatorPage>
</template>

<script setup>
import { BaseCalculatorPage } from '@/components/base'
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

<style scoped src="./commonCalculatorPage.css"></style>
<style scoped>
/* Form fields */
.form-field { display: grid; gap: 0.3rem; }
.form-field span { font-size: var(--cds-text-sm); font-weight: var(--cds-font-semibold); color: var(--cds-dark); letter-spacing: 0.02em; }
.form-field select, .form-field input { border: 1.5px solid rgba(62, 60, 56, 0.25); border-radius: 0.5rem; padding: 0.62rem 0.75rem; font-size: var(--cds-text-base); background: var(--cds-white); color: var(--cds-dark); outline: none; width: 100%; box-sizing: border-box; }
.form-field select:focus, .form-field input:focus { border-color: var(--cds-primary); }
/* Capacitor visual inline */
.cap-visual-inline { display: flex; align-items: center; gap: 0.7rem; padding: 0.2rem 0 0.35rem; }
.cap-visual-inline img { width: 48px; height: 48px; object-fit: contain; }
.cap-visual-inline p { margin: 0; font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
/* Wide 2-col grid for unit inputs */
.form-grid-wide { grid-template-columns: repeat(2, minmax(0, 1fr)); }
@media (max-width: 580px) { .form-grid-wide { grid-template-columns: 1fr; } }
/* Unit input with tag */
.unit-input { display: grid; grid-template-columns: 1fr auto; border: 1.5px solid rgba(62, 60, 56, 0.25); border-radius: 0.5rem; overflow: hidden; background: var(--cds-white); }
.unit-input input { border: none; border-radius: 0; min-width: 0; }
.unit-tag { display: inline-flex; align-items: center; padding: 0 0.7rem; border-left: 1px solid rgba(62, 60, 56, 0.2); background: rgba(62, 60, 56, 0.05); color: var(--cds-dark); font-size: var(--cds-text-sm); font-weight: var(--cds-font-semibold); }
</style>
