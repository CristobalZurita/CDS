<template>
  <div class="cotizador-page">
    <div class="cotizador-card" v-if="step === 1">
      <header class="step-header">
        <h1>Seleccionar Instrumento</h1>
        <p>Paso 1 de 4 - Marca y modelo del equipo.</p>
      </header>

      <div class="form-grid">
        <label class="field">
          <span>Marca</span>
          <input v-model.trim="instrumentBrand" type="text" placeholder="Ej: Korg" />
        </label>
        <label class="field">
          <span>Modelo</span>
          <input v-model.trim="instrumentModel" type="text" placeholder="Ej: MS-20" />
        </label>
      </div>

      <div class="actions">
        <router-link to="/" class="btn-secondary">Cancelar</router-link>
        <button class="btn-primary" :disabled="!canContinueStep1" @click="step = 2">Siguiente →</button>
      </div>
    </div>

    <div class="cotizador-card" v-if="step === 2">
      <header class="step-header">
        <h1>Diagnóstico Visual</h1>
        <p>Paso 2 de 4 - Describe síntomas visibles o funcionales.</p>
      </header>

      <label class="field">
        <span>Resumen del problema</span>
        <textarea
          v-model.trim="diagnosticSummary"
          rows="5"
          placeholder="Describe encendido, audio, controles, pantallas o conectividad."
        />
      </label>

      <div class="actions">
        <button class="btn-secondary" @click="step = 1">← Atrás</button>
        <button class="btn-primary" :disabled="!canContinueStep2" @click="step = 3">Siguiente →</button>
      </div>
    </div>

    <div class="cotizador-card" v-if="step === 3">
      <header class="step-header">
        <h1>Confirmación y Disclaimer</h1>
        <p>Paso 3 de 4 - Validación previa a la estimación.</p>
      </header>

      <div class="disclaimer">
        <p>La cotización es indicativa y no vinculante hasta revisión presencial en taller.</p>
        <p>El presupuesto formal tiene costo de diagnóstico según términos vigentes.</p>
      </div>

      <label class="checkbox-row">
        <input v-model="acceptedDisclaimer" type="checkbox" />
        <span>Acepto condiciones del cotizador referencial</span>
      </label>

      <TurnstileWidget @verify="onVerify" />

      <div class="actions">
        <button class="btn-secondary" @click="step = 2">← Atrás</button>
        <button class="btn-primary" :disabled="!canGenerate" @click="step = 4">Generar estimación</button>
      </div>
    </div>

    <div class="cotizador-card" v-if="step === 4">
      <header class="step-header">
        <h1>Estimación Referencial</h1>
        <p>Paso 4 de 4 - Resultado orientativo.</p>
      </header>

      <div class="result-box">
        <p><strong>Instrumento:</strong> {{ instrumentBrand }} {{ instrumentModel }}</p>
        <p><strong>Síntoma principal:</strong> {{ diagnosticSummary }}</p>
        <p><strong>Rango orientativo inicial:</strong> {{ quotationRange }}</p>
      </div>

      <div class="actions">
        <button class="btn-secondary" @click="resetAll">Nueva cotización</button>
        <button class="btn-primary" @click="goToSchedule">Agendar evaluación</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import TurnstileWidget from '@/components/widgets/TurnstileWidget.vue'
import { useCotizadorIAPage } from '@/composables/useCotizadorIAPage'

const {
  step,
  instrumentBrand,
  instrumentModel,
  diagnosticSummary,
  acceptedDisclaimer,
  canContinueStep1,
  canContinueStep2,
  canGenerate,
  quotationRange,
  onVerify,
  resetAll,
  goToSchedule
} = useCotizadorIAPage()
</script>

<style scoped>
.cotizador-page {
  padding: 1rem;
}

.cotizador-card {
  max-width: 920px;
  margin: 0 auto;
  background: var(--cds-white);
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
  border-radius: 0.95rem;
  padding: 1rem;
  display: grid;
  gap: 0.9rem;
}

.step-header h1 {
  margin: 0;
  font-size: var(--cds-text-2xl);
}

.step-header p {
  margin: 0.35rem 0 0;
  color: var(--cds-text-muted);
}

.form-grid {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: 1fr;
}

.field {
  display: grid;
  gap: 0.45rem;
}

.field span {
  font-size: var(--cds-text-sm);
}

.field input,
.field textarea {
  width: 100%;
  min-height: 44px;
  padding: 0.7rem 0.8rem;
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
  border-radius: 0.55rem;
  font-size: var(--cds-text-base);
}

.disclaimer {
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  border-radius: 0.7rem;
  padding: 0.8rem;
  background: color-mix(in srgb, var(--cds-light) 14%, white);
}

.disclaimer p {
  margin: 0.2rem 0;
}

.checkbox-row {
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
  font-size: var(--cds-text-base);
}

.result-box {
  border: 1px solid color-mix(in srgb, var(--cds-primary) 25%, white);
  border-radius: 0.7rem;
  padding: 0.85rem;
}

.result-box p {
  margin: 0.35rem 0;
}

.actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  min-height: 44px;
  padding: 0.65rem 0.95rem;
  border-radius: 0.55rem;
  font-size: var(--cds-text-base);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.btn-primary {
  border: 1px solid var(--cds-primary);
  background: var(--cds-primary);
  color: var(--cds-white);
}

.btn-secondary {
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  background: var(--cds-white);
  color: var(--cds-text-normal);
}

@media (min-width: 768px) {
  .form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
