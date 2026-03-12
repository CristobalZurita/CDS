<template>
  <main class="calc-page">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Calculadora AWG</h1>
        <p>Convierte calibre AWG a diámetro, área y resistencia por kilómetro.</p>
      </header>

      <div class="calc-layout">
        <section class="calc-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-sliders"></i>
              Parámetros
            </div>
          </div>

          <div class="panel-body">
            <BaseInput
              id="awg-value"
              v-model.number="form.awg"
              label="Calibre AWG"
              type="number"
              inputmode="numeric"
              min="0"
              step="1"
              placeholder="Ej: 24"
            />

            <div class="form-actions">
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
            <div v-if="canCalculate && result" class="output-values">
              <div class="value-row">
                <span>Diámetro</span>
                <strong>{{ result.diameter_mm }} mm</strong>
              </div>
              <div class="value-row">
                <span>Área</span>
                <strong>{{ result.area_mm2 }} mm²</strong>
              </div>
              <div class="value-row">
                <span>Resistencia</span>
                <strong>{{ result.resistance_ohm_per_km }} Ω/km</strong>
              </div>
            </div>
            <p v-else class="result-hint">Ingresa un AWG válido.</p>
          </div>
        </section>
      </div>

      <router-link to="/calculadoras" class="back-link">← Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { BaseButton, BaseInput } from '@/components/ui'
import { useAwgCalculator } from '@/composables/useAwgCalculator'

const { form, canCalculate, result, reset } = useAwgCalculator()
</script>

<style scoped src="./commonCalculatorPage.css"></style>
