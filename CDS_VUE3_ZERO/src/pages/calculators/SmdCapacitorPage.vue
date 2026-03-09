<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Decodificador SMD Capacitor</h1>
        <p>Interpreta códigos de capacitores SMD y convierte unidades de capacitancia.</p>
      </header>

      <section class="calc-card">
        <BaseInput
          id="smd-capacitor-code"
          v-model.trim="form.code"
          label="Código SMD"
          type="text"
          placeholder="Ej: 104 o 472"
        />

        <label class="field-label" for="smd-capacitor-type">
          Tipo de código
          <select id="smd-capacitor-type" v-model="form.type" class="field-control">
            <option v-for="item in smdCapacitorTypeOptions" :key="item.value" :value="item.value">
              {{ item.label }}
            </option>
          </select>
        </label>
      </section>

      <section class="result-card">
        <template v-if="isValidCode">
          <p class="result-value">pF: {{ decoded.pf }}</p>
          <p class="result-value">nF: {{ decoded.nf }}</p>
          <p class="result-value">µF: {{ decoded.uf }}</p>
        </template>
        <p v-else class="result-hint">Código inválido para el tipo seleccionado.</p>
      </section>

      <section class="calc-card">
        <h2>Conversión manual</h2>
        <div class="field-grid">
          <label class="field-label" for="cap-pf">
            pF
            <input id="cap-pf" v-model.number="form.pf" type="number" inputmode="decimal" class="field-control" @input="convertFrom('pf')" />
          </label>
          <label class="field-label" for="cap-nf">
            nF
            <input id="cap-nf" v-model.number="form.nf" type="number" inputmode="decimal" class="field-control" @input="convertFrom('nf')" />
          </label>
          <label class="field-label" for="cap-uf">
            µF
            <input id="cap-uf" v-model.number="form.uf" type="number" inputmode="decimal" class="field-control" @input="convertFrom('uf')" />
          </label>
          <label class="field-label" for="cap-f">
            F
            <input id="cap-f" v-model.number="form.f" type="number" inputmode="decimal" class="field-control" @input="convertFrom('f')" />
          </label>
        </div>
      </section>

      <router-link to="/calculadoras" class="back-link">Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { BaseInput } from '@/components/ui'
import { smdCapacitorTypeOptions, useSmdCapacitorCalculator } from '@/composables/useSmdCapacitorCalculator'

const { form, decoded, isValidCode, convertFrom } = useSmdCapacitorCalculator()
</script>

<style scoped>
.calc-page { padding: 1rem; }
.calc-container { max-width: 960px; margin: 0 auto; display: grid; gap: 1rem; }
.calc-header h1 { margin: 0; font-size: var(--cds-text-3xl); line-height: var(--cds-leading-tight); }
.calc-header p { margin: 0.4rem 0 0; color: var(--cds-text-muted); font-size: var(--cds-text-base); }
.calc-card, .result-card { background: var(--cds-white); border: 1px solid color-mix(in srgb, var(--cds-light) 75%, white); border-radius: 0.8rem; padding: 1rem; }
.calc-card { display: grid; gap: 0.9rem; }
.calc-card h2 { margin: 0; font-size: var(--cds-text-xl); }
.field-label { display: grid; gap: 0.35rem; font-size: var(--cds-text-sm); font-weight: var(--cds-font-medium); color: var(--cds-text-normal); }
.field-control { min-height: 44px; border: 2px solid var(--cds-light-4); border-radius: 0.5rem; padding: 0.75rem 0.875rem; font-size: var(--cds-text-base); background: var(--cds-white); color: var(--cds-text-normal); }
.field-grid { display: grid; gap: 0.75rem; }
.result-value { margin: 0.2rem 0; font-size: var(--cds-text-lg); color: var(--cds-primary); font-weight: var(--cds-font-semibold); }
.result-hint { margin: 0; font-size: var(--cds-text-base); color: var(--cds-text-muted); }
.back-link { display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 0.65rem 1rem; border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, white); border-radius: 0.6rem; text-decoration: none; color: var(--cds-primary); width: fit-content; }
@media (min-width: 768px) { .field-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
