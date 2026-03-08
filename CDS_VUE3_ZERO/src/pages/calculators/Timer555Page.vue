<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Calculadora Timer 555</h1>
        <p>Modo astable y monostable para estimar frecuencia y tiempos.</p>
      </header>

      <section class="calc-card">
        <label class="field-label" for="timer555-mode">
          Modo
          <select id="timer555-mode" v-model="form.mode" class="field-control">
            <option v-for="item in timer555ModeOptions" :key="item.value" :value="item.value">
              {{ item.label }}
            </option>
          </select>
        </label>

        <div class="field-grid" v-if="isAstable">
          <BaseInput id="timer-r1" v-model.number="form.r1_value" label="R1" type="number" inputmode="decimal" />
          <label class="field-label" for="timer-r1-unit">
            Unidad R1
            <select id="timer-r1-unit" v-model="form.r1_unit" class="field-control">
              <option value="ohm">Ω</option>
              <option value="kohm">kΩ</option>
              <option value="mohm">MΩ</option>
            </select>
          </label>
          <BaseInput id="timer-r2" v-model.number="form.r2_value" label="R2" type="number" inputmode="decimal" />
          <label class="field-label" for="timer-r2-unit">
            Unidad R2
            <select id="timer-r2-unit" v-model="form.r2_unit" class="field-control">
              <option value="ohm">Ω</option>
              <option value="kohm">kΩ</option>
              <option value="mohm">MΩ</option>
            </select>
          </label>
        </div>

        <div class="field-grid" v-else>
          <BaseInput id="timer-r" v-model.number="form.r_value" label="R" type="number" inputmode="decimal" />
          <label class="field-label" for="timer-r-unit">
            Unidad R
            <select id="timer-r-unit" v-model="form.r_unit" class="field-control">
              <option value="ohm">Ω</option>
              <option value="kohm">kΩ</option>
              <option value="mohm">MΩ</option>
            </select>
          </label>
        </div>

        <div class="field-grid">
          <BaseInput id="timer-c" v-model.number="form.c_value" label="C" type="number" inputmode="decimal" />
          <label class="field-label" for="timer-c-unit">
            Unidad C
            <select id="timer-c-unit" v-model="form.c_unit" class="field-control">
              <option value="pf">pF</option>
              <option value="nf">nF</option>
              <option value="uf">µF</option>
            </select>
          </label>
          <BaseInput id="timer-vcc" v-model.number="form.vcc_v" label="Vcc (V)" type="number" inputmode="decimal" />
        </div>

        <div class="calc-actions">
          <BaseButton type="button" variant="ghost" class="reset-button" @click="reset">Limpiar</BaseButton>
        </div>
      </section>

      <section class="result-card">
        <template v-if="canCalculate && result">
          <p class="result-value">Frecuencia: {{ result.frequency_hz ?? '—' }} Hz</p>
          <p class="result-value">Periodo: {{ result.period_s ?? '—' }} s</p>
          <p v-if="isAstable" class="result-value">T alto: {{ result.t_high_s ?? '—' }} s</p>
          <p v-if="isAstable" class="result-value">T bajo: {{ result.t_low_s ?? '—' }} s</p>
          <p v-if="isAstable" class="result-value">Duty: {{ result.duty_cycle ?? '—' }}</p>
        </template>
        <p v-else class="result-hint">Completa los campos para calcular.</p>
      </section>

      <router-link to="/calculadoras" class="back-link">Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { BaseButton, BaseInput } from '@new/components/ui'
import { timer555ModeOptions, useTimer555Calculator } from '@new/composables/useTimer555Calculator'

const { form, isAstable, canCalculate, result, reset } = useTimer555Calculator()
</script>

<style scoped>
.calc-page { padding: 1rem; }
.calc-container { max-width: 1040px; margin: 0 auto; display: grid; gap: 1rem; }
.calc-header h1 { margin: 0; font-size: var(--cds-text-3xl); line-height: var(--cds-leading-tight); }
.calc-header p { margin: 0.4rem 0 0; color: var(--cds-text-muted); font-size: var(--cds-text-base); }
.calc-card, .result-card { background: var(--cds-white); border: 1px solid color-mix(in srgb, var(--cds-light) 75%, white); border-radius: 0.8rem; padding: 1rem; }
.calc-card { display: grid; gap: 0.9rem; }
.field-grid { display: grid; gap: 0.75rem; }
.field-label { display: grid; gap: 0.35rem; font-size: var(--cds-text-sm); font-weight: var(--cds-font-medium); color: var(--cds-text-normal); }
.field-control { min-height: 44px; border: 2px solid var(--cds-light-4); border-radius: 0.5rem; padding: 0.75rem 0.875rem; font-size: var(--cds-text-base); background: var(--cds-white); color: var(--cds-text-normal); }
.calc-actions { display: flex; gap: 0.75rem; }
.reset-button { width: auto; }
.result-value { margin: 0.2rem 0; font-size: var(--cds-text-lg); color: var(--cds-primary); font-weight: var(--cds-font-semibold); }
.result-hint { margin: 0; font-size: var(--cds-text-base); color: var(--cds-text-muted); }
.back-link { display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 0.65rem 1rem; border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, white); border-radius: 0.6rem; text-decoration: none; color: var(--cds-primary); width: fit-content; }
@media (min-width: 768px) { .field-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
</style>
