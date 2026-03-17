<template>
  <BaseCalculatorPage title="Calculadora AWG" description="Convierte calibre AWG a diámetro, área y resistencia por kilómetro.">
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
  </BaseCalculatorPage>
</template>

<script setup>
import { BaseCalculatorPage, BaseButton } from '@/components/base'
import { BaseInput } from '@/components/base'
import { useAwgCalculator } from '@/composables/useAwgCalculator'

const { form, canCalculate, result, reset } = useAwgCalculator()
</script>

<style scoped src="./commonCalculatorPage.css"></style>
