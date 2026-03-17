<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Convertidor de Temperatura</h1>
        <p>Convierte entre Celsius, Fahrenheit, Kelvin y Rankine.</p>
      </header>

      <div class="calc-layout">
        <section class="calc-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-temperature-high"></i>
              Parámetros
            </div>
          </div>

          <div class="panel-body panel-form">
            <BaseInput
              id="temperature-value"
              v-model.number="form.value"
              label="Valor"
              type="number"
              inputmode="decimal"
              placeholder="Ej: 25"
            />

            <div class="field-grid">
              <label class="field-label" for="temperature-from">
                Escala origen
                <select id="temperature-from" v-model="form.from" class="field-control">
                  <option v-for="scale in temperatureScales" :key="scale.value" :value="scale.value">{{ scale.label }}</option>
                </select>
              </label>

              <label class="field-label" for="temperature-to">
                Escala destino
                <select id="temperature-to" v-model="form.to" class="field-control">
                  <option v-for="scale in temperatureScales" :key="`to-${scale.value}`" :value="scale.value">{{ scale.label }}</option>
                </select>
              </label>
            </div>

            <div class="form-actions">
              <BaseButton type="button" variant="ghost" class="swap-button" @click="swapScales">Intercambiar escalas</BaseButton>
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
            <div class="output-values">
              <div class="value-row">
                <span>Conversión</span>
                <strong>{{ canConvert ? `${result} °${form.to}` : '—' }}</strong>
              </div>
              <div class="value-row">
                <span>Celsius</span>
                <strong>{{ formatScale(displayScales.C, '°C') }}</strong>
              </div>
              <div class="value-row">
                <span>Fahrenheit</span>
                <strong>{{ formatScale(displayScales.F, '°F') }}</strong>
              </div>
              <div class="value-row">
                <span>Kelvin</span>
                <strong>{{ formatScale(displayScales.K, 'K') }}</strong>
              </div>
            </div>

            <div class="thermo-grid">
              <article
                v-for="item in thermoItems"
                :key="item.key"
                class="thermo-card"
              >
                <header class="thermo-card-head">
                  <span>{{ item.label }}</span>
                  <strong>{{ formatScale(item.value, item.unit) }}</strong>
                </header>

                <div
                  class="thermo-track"
                  :style="{
                    '--thermo-fill': `${fillPercent(item)}%`,
                    '--thermo-color': item.tone
                  }"
                >
                  <span class="thermo-column"></span>
                  <span class="thermo-bulb"></span>
                </div>
              </article>
            </div>
            <p v-if="!canConvert" class="result-hint">Ingresa un valor numérico para actualizar la conversión.</p>
          </div>
        </section>
      </div>

      <router-link to="/calculadoras" class="back-link">← Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { BaseButton, BaseInput } from '@/components/base'
import { temperatureScales, useTemperatureCalculator } from '@/composables/useTemperatureCalculator'

const { form, canConvert, result, allScales, reset } = useTemperatureCalculator()

const displayScales = computed(() => (
  allScales.value || {
    C: 0,
    F: 32,
    K: 273.15,
    R: 491.67
  }
))

const thermoItems = computed(() => ([
  {
    key: 'C',
    label: 'Celsius',
    unit: '°C',
    value: displayScales.value.C,
    min: -50,
    max: 150,
    tone: '#ec6b00'
  },
  {
    key: 'F',
    label: 'Fahrenheit',
    unit: '°F',
    value: displayScales.value.F,
    min: -58,
    max: 302,
    tone: '#c74f33'
  },
  {
    key: 'K',
    label: 'Kelvin',
    unit: 'K',
    value: displayScales.value.K,
    min: 223.15,
    max: 423.15,
    tone: '#2b8bd7'
  }
]))

function fillPercent(item) {
  if (!Number.isFinite(item.value)) return 0
  const span = item.max - item.min
  if (!(span > 0)) return 0
  const ratio = ((item.value - item.min) / span) * 100
  return Math.min(100, Math.max(0, ratio))
}

function formatScale(value, unit) {
  if (!Number.isFinite(value)) return `— ${unit}`
  return `${value.toFixed(2)} ${unit}`
}

function swapScales() {
  const nextFrom = form.to
  form.to = form.from
  form.from = nextFrom
}
</script>

<style scoped src="./commonCalculatorPage.css"></style>
<style scoped src="./TemperaturePage.css"></style>
