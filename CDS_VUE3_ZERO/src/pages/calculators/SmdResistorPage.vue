<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Decodificador SMD Resistor</h1>
        <p>Interpreta códigos EIA-3, EIA-4 y EIA-96 para resistencias SMD.</p>
      </header>

      <section class="calc-card">
        <BaseInput
          id="smd-resistor-code"
          v-model.trim="form.code"
          label="Código SMD"
          type="text"
          placeholder="Ej: 103 o 01C"
        />

        <label class="field-label" for="smd-resistor-type">
          Tipo de código
          <select id="smd-resistor-type" v-model="form.type" class="field-control">
            <option v-for="item in smdResistorTypeOptions" :key="item.value" :value="item.value">
              {{ item.label }}
            </option>
          </select>
        </label>
      </section>

      <section class="result-card">
        <p v-if="isValid" class="result-value">Resistencia: {{ formattedResistance }}</p>
        <p v-else class="result-hint">Código inválido para el tipo seleccionado.</p>
      </section>

      <router-link to="/calculadoras" class="back-link">Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { BaseInput } from '@new/components/ui'
import { smdResistorTypeOptions, useSmdResistorCalculator } from '@new/composables/useSmdResistorCalculator'

const { form, isValid, formattedResistance } = useSmdResistorCalculator()
</script>

<style scoped>
.calc-page { padding: 1rem; }
.calc-container { max-width: 960px; margin: 0 auto; display: grid; gap: 1rem; }
.calc-header h1 { margin: 0; font-size: var(--cds-text-3xl); line-height: var(--cds-leading-tight); }
.calc-header p { margin: 0.4rem 0 0; color: var(--cds-text-muted); font-size: var(--cds-text-base); }
.calc-card, .result-card { background: var(--cds-white); border: 1px solid color-mix(in srgb, var(--cds-light) 75%, white); border-radius: 0.8rem; padding: 1rem; }
.calc-card { display: grid; gap: 0.9rem; }
.field-label { display: grid; gap: 0.35rem; font-size: var(--cds-text-sm); font-weight: var(--cds-font-medium); color: var(--cds-text-normal); }
.field-control { min-height: 44px; border: 2px solid var(--cds-light-4); border-radius: 0.5rem; padding: 0.75rem 0.875rem; font-size: var(--cds-text-base); background: var(--cds-white); color: var(--cds-text-normal); }
.result-value { margin: 0.2rem 0; font-size: var(--cds-text-lg); color: var(--cds-primary); font-weight: var(--cds-font-semibold); }
.result-hint { margin: 0; font-size: var(--cds-text-base); color: var(--cds-text-muted); }
.back-link { display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 0.65rem 1rem; border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, white); border-radius: 0.6rem; text-decoration: none; color: var(--cds-primary); width: fit-content; }
</style>
