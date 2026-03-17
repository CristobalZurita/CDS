<template>
  <div class="cotizador-page">

    <!-- Indicador de progreso -->
    <div class="progress-bar" aria-hidden="true">
      <div class="progress-fill"></div>
    </div>

    <!-- Error global -->
    <p v-if="error" class="alert-error" role="alert">{{ error }}</p>

    <!-- ── Paso 1: Selección de equipo ───────────────────────────── -->
    <div v-if="step === 1" class="cotizador-card">
      <CotizadorStepHeader
        :badge="notFoundMode ? 'Paso 1 de 2' : 'Paso 1 de 4'"
        title="Seleccionar equipo"
      >
        <template #description>
          {{ notFoundMode ? 'Escribe la marca y el modelo de tu instrumento.' : 'Elige la marca y el modelo de tu instrumento.' }}
        </template>
      </CotizadorStepHeader>

      <!-- Modo normal: selects de marca y modelo -->
      <div v-if="!notFoundMode" class="form-grid">
        <label class="field">
          <span>Marca</span>
          <select
            :value="selectedBrand"
            :disabled="loading"
            @change="onBrandSelect($event.target.value)"
          >
            <option value="">— Selecciona una marca —</option>
            <option v-for="b in brands" :key="b.id" :value="b.id">
              {{ b.name }}
            </option>
          </select>
        </label>

        <label class="field">
          <span>Modelo</span>
          <select
            :value="selectedModel"
            :disabled="!selectedBrand || loading"
            @change="onModelSelect($event.target.value)"
          >
            <option value="">— Selecciona un modelo —</option>
            <option v-for="m in models" :key="m.id" :value="m.id">
              {{ m.model }}
            </option>
          </select>
          <span v-if="selectedBrand && models.length === 0 && !loading" class="field-hint">
            No hay modelos registrados para esta marca aún.
          </span>
        </label>
      </div>

      <!-- Modo "no encontrado": inputs libres -->
      <div v-else class="form-grid">
        <label class="field">
          <span>Marca <em class="required">*</em></span>
          <input
            v-model.trim="manualBrand"
            type="text"
            placeholder="Ej: Yamaha, Roland, Korg…"
            autocomplete="off"
          />
        </label>
        <label class="field">
          <span>Modelo <em class="required">*</em></span>
          <input
            v-model.trim="manualModel"
            type="text"
            placeholder="Ej: DX7, Juno-106, Minilogue…"
            autocomplete="off"
          />
        </label>
      </div>

      <div v-if="loading && !notFoundMode" class="loading-row">
        <span class="spinner"></span> Cargando…
      </div>

      <!-- Toggle "no encontré / volver a lista" -->
      <div class="not-found-toggle">
        <button
          v-if="!notFoundMode"
          type="button"
          class="btn-link"
          @click="activateNotFoundMode"
        >
          <i class="fas fa-question-circle"></i>
          Mi instrumento no está en la lista
        </button>
        <button
          v-else
          type="button"
          class="btn-link"
          @click="deactivateNotFoundMode"
        >
          <i class="fas fa-arrow-left"></i>
          Volver a la lista
        </button>
      </div>

      <div class="actions">
        <router-link to="/" class="btn-secondary">Cancelar</router-link>
        <button
          class="btn-primary"
          :disabled="!canContinueStep1 || loading"
          @click="notFoundMode ? goToLeadStep() : (step = 2)"
        >
          Siguiente →
        </button>
      </div>
    </div>

    <!-- ── Paso 2: Selección de fallas ──────────────────────────── -->
    <div v-if="step === 2" class="cotizador-card">
      <CotizadorStepHeader badge="Paso 2 de 4" title="Síntomas del equipo">
        <template #description>
          Selecciona todo lo que presenta tu <strong>{{ selectedBrandName }} {{ selectedModelName }}</strong>.
        </template>
      </CotizadorStepHeader>

      <div v-if="loading" class="loading-row">
        <span class="spinner"></span> Cargando fallas disponibles…
      </div>

      <div v-else class="faults-grid">
        <label
          v-for="fault in faults"
          :key="fault.id"
          class="fault-card"
          :class="{ 'fault-card--selected': selectedFaultIds.includes(fault.id) }"
        >
          <input
            type="checkbox"
            class="sr-only"
            :value="fault.id"
            :checked="selectedFaultIds.includes(fault.id)"
            @change="toggleFault(fault.id)"
          />
          <span class="fault-icon">
            <i :class="`fa-solid ${fault.icon || 'fa-wrench'}`"></i>
          </span>
          <span class="fault-name">{{ fault.name }}</span>
          <span class="fault-desc">{{ fault.description }}</span>
          <span v-if="fault.isPrecedence" class="fault-precedence">
            Anula otras fallas
          </span>
        </label>
      </div>

      <TurnstileWidget
        v-if="!loading"
        :key="quoteTurnstileRenderKey"
        @verify="onQuoteVerify"
      />

      <div class="actions">
        <button class="btn-secondary" @click="step = 1">← Atrás</button>
        <button
          class="btn-primary"
          :disabled="!canContinueStep2 || loading"
          @click="calculateQuote"
        >
          <span v-if="loading"><span class="spinner spinner--sm"></span> Calculando…</span>
          <span v-else>Ver estimación →</span>
        </button>
      </div>
    </div>

    <!-- ── Paso 3: Resultado del cálculo ────────────────────────── -->
    <div v-if="step === 3" class="cotizador-card">
      <CotizadorStepHeader badge="Paso 3 de 4" title="Estimación referencial">
        <template #description>
          Basada en los síntomas seleccionados y el perfil del equipo.
        </template>
      </CotizadorStepHeader>

      <CotizadorQuoteSummary
        :quote-result="quoteResult"
        :selected-fault-names="selectedFaultNames"
        :formatted-final-cost="formattedFinalCost"
        :format-clp="formatCLP"
      />

      <div class="disclaimer">
        <p>Esta cotización es referencial y no vinculante. El presupuesto formal
           requiere revisión presencial en taller.</p>
      </div>

      <div class="actions">
        <button class="btn-secondary" @click="step = 2">← Atrás</button>
        <button class="btn-primary" @click="goToLeadStep">
          Dejar mis datos →
        </button>
      </div>
    </div>

    <!-- ── Paso 4: Formulario de contacto ────────────────────────── -->
    <div v-if="step === 4" class="cotizador-card">
      <template v-if="!leadSubmitted">
        <CotizadorStepHeader
          :badge="notFoundMode ? 'Paso 2 de 2' : 'Paso 4 de 4'"
          title="Tus datos de contacto"
        >
          <template #description>
            Te contactaremos para coordinar la revisión de tu equipo.
          </template>
        </CotizadorStepHeader>

        <div class="form-grid">
          <label class="field">
            <span>Nombre completo <em class="required">*</em></span>
            <input
              v-model.trim="leadForm.nombre"
              type="text"
              autocomplete="name"
              placeholder="Tu nombre"
            />
          </label>
          <label class="field">
            <span>Email <em class="required">*</em></span>
            <input
              v-model.trim="leadForm.email"
              type="email"
              autocomplete="email"
              placeholder="correo@dominio.com"
            />
          </label>
          <label class="field">
            <span>Teléfono <em class="optional">(opcional)</em></span>
            <input
              v-model.trim="leadForm.telefono"
              type="tel"
              autocomplete="tel"
              placeholder="+56 9 1234 5678"
            />
          </label>
        </div>

        <label class="checkbox-row">
          <input v-model="acceptedDisclaimer" type="checkbox" />
          <span>Acepto las condiciones del servicio de cotización referencial</span>
        </label>

        <TurnstileWidget :key="leadTurnstileRenderKey" @verify="onLeadVerify" />

        <div class="actions">
          <button class="btn-secondary" @click="notFoundMode ? (step = 1) : (step = 3)">← Atrás</button>
          <button
            class="btn-primary"
            :disabled="!canSubmitLead || loading"
            @click="submitLead"
          >
            <span v-if="loading"><span class="spinner spinner--sm"></span> Enviando…</span>
            <span v-else>Enviar y agendar</span>
          </button>
        </div>
      </template>

      <!-- Éxito -->
      <template v-else>
        <CotizadorLeadSuccess
          :lead-name="leadForm.nombre"
          :selected-brand-name="selectedBrandName"
          :selected-model-name="selectedModelName"
          :formatted-final-cost="formattedFinalCost"
          :not-found-mode="notFoundMode"
        />

        <div class="actions actions--center">
          <button class="btn-secondary" @click="resetAll">Nueva cotización</button>
          <button class="btn-primary" @click="goToSchedule">Agendar ahora</button>
        </div>
      </template>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import CotizadorLeadSuccess from '@/components/business/CotizadorLeadSuccess.vue'
import CotizadorQuoteSummary from '@/components/business/CotizadorQuoteSummary.vue'
import CotizadorStepHeader from '@/components/business/CotizadorStepHeader.vue'
import TurnstileWidget from '@/components/widgets/TurnstileWidget.vue'
import { useCotizadorIAPage } from '@/composables/useCotizadorIAPage'

const {
  step,
  loading,
  error,
  brands,
  selectedBrand,
  models,
  selectedModel,
  faults,
  selectedFaultIds,
  quoteResult,
  leadForm,
  acceptedDisclaimer,
  leadSubmitted,
  notFoundMode,
  manualBrand,
  manualModel,
  canContinueStep1,
  canContinueStep2,
  canSubmitLead,
  formattedFinalCost,
  selectedBrandName,
  selectedModelName,
  selectedFaultNames,
  quoteTurnstileRenderKey,
  leadTurnstileRenderKey,
  onBrandSelect,
  onModelSelect,
  toggleFault,
  calculateQuote,
  submitLead,
  onQuoteVerify,
  onLeadVerify,
  goToLeadStep,
  goToSchedule,
  resetAll,
  activateNotFoundMode,
  deactivateNotFoundMode,
} = useCotizadorIAPage()

const progressScale = computed(() => {
  const currentStep = Number(step.value || 1)
  if (notFoundMode.value) {
    return currentStep === 1 ? '0.5' : '1'
  }
  const normalized = Math.min(Math.max(currentStep / 4, 0), 1)
  return String(normalized)
})

function formatCLP(value) {
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(Number(value || 0))
}
</script>

<style scoped>
.cotizador-page {
  padding: 0.5rem 1rem 2rem;
  display: grid;
  gap: 1rem;
}

/* Barra de progreso */
.progress-bar {
  height: 4px;
  background: color-mix(in srgb, var(--cds-light) 60%, white);
  border-radius: 4px;
  overflow: hidden;
  max-width: 920px;
  margin: 0 auto;
  width: 100%;
}

.progress-fill {
  height: 100%;
  background: var(--cds-primary);
  transform: scaleX(v-bind(progressScale));
  transform-origin: left center;
  transition: transform 0.35s ease;
}

/* Alerta de error */
.alert-error {
  max-width: 920px;
  margin: 0 auto;
  width: 100%;
  padding: 0.75rem 1rem;
  background: color-mix(in srgb, var(--cds-primary) 10%, white);
  border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, white);
  border-radius: var(--cds-radius-sm);
  color: var(--cds-primary);
  font-size: var(--cds-text-sm);
}

/* Card principal */
.cotizador-card {
  max-width: 920px;
  margin: 0 auto;
  width: 100%;
  background: var(--cds-white);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-md);
  padding: 1.25rem 1rem;
  display: grid;
  gap: 1rem;
}

/* Grid de formulario */
.form-grid {
  display: grid;
  gap: 0.75rem;
}

.field {
  display: grid;
  gap: 0.4rem;
}

.field > span {
  font-size: var(--cds-text-sm);
  font-weight: 500;
}

.field input,
.field select {
  width: 100%;
  min-height: 44px;
  padding: 0.65rem 0.8rem;
  border: 1px solid var(--cds-border-input);
  border-radius: var(--cds-radius-sm);
  font-size: var(--cds-text-base);
  background: var(--cds-white);
  color: var(--cds-text-normal);
  appearance: auto;
}

.field input:focus,
.field select:focus {
  outline: 2px solid var(--cds-primary);
  outline-offset: 1px;
}

.field-hint {
  font-size: var(--cds-text-xs);
  color: var(--cds-text-muted);
}

.required {
  color: var(--cds-primary);
  font-style: normal;
}

.optional {
  color: var(--cds-text-muted);
  font-weight: 400;
  font-style: normal;
}

/* Cargando */
.loading-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
}

.spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid color-mix(in srgb, var(--cds-primary) 25%, white);
  border-top-color: var(--cds-primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

.spinner--sm {
  width: 14px;
  height: 14px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Grid de fallas */
.faults-grid {
  display: grid;
  gap: var(--cds-space-xs);
}

.fault-card {
  display: grid;
  grid-template-columns: 2rem 1fr;
  grid-template-rows: auto auto auto;
  column-gap: 0.6rem;
  row-gap: 0.1rem;
  padding: 0.7rem 0.85rem;
  border: 1px solid var(--cds-border-input);
  border-radius: var(--cds-radius-sm);
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.fault-card:hover {
  border-color: color-mix(in srgb, var(--cds-primary) 40%, white);
  background: color-mix(in srgb, var(--cds-primary) 4%, white);
}

.fault-card--selected {
  border-color: var(--cds-primary);
  background: color-mix(in srgb, var(--cds-primary) 8%, white);
}

.fault-icon {
  grid-row: 1 / 3;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--cds-primary);
  font-size: 1rem;
}

.fault-name {
  font-weight: 600;
  font-size: var(--cds-text-sm);
  align-self: end;
}

.fault-desc {
  grid-column: 2;
  font-size: var(--cds-text-xs);
  color: var(--cds-text-muted);
  line-height: 1.4;
}

.fault-precedence {
  grid-column: 2;
  font-size: var(--cds-text-xs);
  font-weight: 600;
  color: var(--cds-primary);
  margin-top: 0.1rem;
}

/* Disclaimer */
.disclaimer {
  border: 1px solid var(--cds-border-input);
  border-radius: 0.7rem;
  padding: 0.75rem;
  background: color-mix(in srgb, var(--cds-light) 14%, white);
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.disclaimer p {
  margin: 0;
}

/* Checkbox */
.checkbox-row {
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
  font-size: var(--cds-text-sm);
  cursor: pointer;
}

.checkbox-row input[type="checkbox"] {
  margin-top: 0.15rem;
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  accent-color: var(--cds-primary);
}

/* Acciones */
.actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.actions--center {
  justify-content: center;
}

.btn-primary,
.btn-secondary {
  min-height: 44px;
  padding: 0.65rem 1.1rem;
  border-radius: var(--cds-radius-sm);
  font-size: var(--cds-text-base);
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  text-decoration: none;
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn-primary:disabled,
.btn-secondary:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-primary {
  border: 1px solid var(--cds-primary);
  background: var(--cds-primary);
  color: var(--cds-white);
}

.btn-primary:not(:disabled):hover {
  opacity: 0.88;
}

.btn-secondary {
  border: 1px solid var(--cds-border-input);
  background: var(--cds-white);
  color: var(--cds-text-normal);
}

.btn-secondary:not(:disabled):hover {
  background: color-mix(in srgb, var(--cds-light) 20%, white);
}

/* Toggle "no encontré mi instrumento" */
.not-found-toggle {
  display: flex;
  justify-content: flex-start;
}

.btn-link {
  background: none;
  border: none;
  padding: 0;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  text-decoration: underline;
  text-underline-offset: 2px;
  transition: color 0.15s;
}

.btn-link:hover {
  color: var(--cds-primary);
}

/* Accesibilidad */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (min-width: 640px) {
  .cotizador-page {
    padding: 1rem 1.5rem 2.5rem;
  }

  .cotizador-card {
    padding: 1.75rem 1.5rem;
  }

  .form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .faults-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .faults-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
