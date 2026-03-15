<template>
  <BaseCalculatorPage
    title="Calculadora de Resistencias SMD"
    description="Decodifica resistencias SMD con EIA-3, EIA-4, EIA-96 y notación R."
  >
    <section class="calc-panel">
      <div class="panel-header">
        <div class="panel-title">
          <i class="fa-solid fa-hashtag"></i>
          Parámetros
        </div>
      </div>

      <div class="panel-body">
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
          <button type="button" class="action-btn" @click="reset">
            <i class="fa-solid fa-rotate-left"></i>
            Resetear parámetros
          </button>
        </div>
      </div>
    </section>

    <section class="calc-panel">
      <div class="panel-header">
        <div class="panel-title">
          <i class="fa-solid fa-wave-square"></i>
          Resultado
        </div>
      </div>

      <div class="panel-body">
        <div class="diagram-card">
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

        <p class="result-hint" v-if="!isValid">Ingresa un código válido según el formato seleccionado.</p>
      </div>
    </section>
  </BaseCalculatorPage>
</template>

<script setup>
import { computed } from 'vue'
import { BaseCalculatorPage } from '@/components/base'
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

<style scoped src="./commonCalculatorPage.css"></style>
<style scoped>
/* Form fields */
.form-field { display: grid; gap: 0.3rem; }
.form-field span { font-size: var(--cds-text-sm); font-weight: var(--cds-font-semibold); color: var(--cds-dark); }
.form-field select, .form-field input { border: 1.5px solid rgba(62, 60, 56, 0.25); border-radius: 0.5rem; padding: 0.62rem 0.75rem; font-size: var(--cds-text-base); background: var(--cds-white); color: var(--cds-dark); outline: none; width: 100%; box-sizing: border-box; }
.form-field select:focus, .form-field input:focus { border-color: var(--cds-primary); }
/* Helper examples */
.helper-block { display: grid; gap: 0.45rem; }
.helper-title { margin: 0; font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.example-list { display: flex; flex-wrap: wrap; gap: 0.45rem; }
.example-chip { border: 1px solid rgba(62, 60, 56, 0.25); background: var(--cds-white); color: var(--cds-dark); border-radius: 999px; min-height: 32px; padding: 0 0.7rem; font-size: var(--cds-text-sm); font-weight: var(--cds-font-semibold); cursor: pointer; }
/* Chip preview */
.chip-preview { min-height: 64px; border-radius: 0.8rem; border: 1px solid rgba(62, 60, 56, 0.25); background: linear-gradient(135deg, #292a2d, #17181a); display: flex; align-items: center; justify-content: center; }
.chip-preview--active { box-shadow: 0 0 0 1px color-mix(in srgb, var(--cds-primary) 45%, transparent) inset; }
.chip-text { color: #f2f2f2; font-size: 1.2rem; font-weight: 700; letter-spacing: 0.05em; }
</style>
