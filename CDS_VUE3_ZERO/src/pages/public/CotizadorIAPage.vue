<template>
  <div class="cotizador-page">

    <!-- Indicador de progreso -->
    <div class="progress-bar" aria-hidden="true">
      <div
        class="progress-fill"
        :style="{ width: `${(step / 4) * 100}%` }"
      ></div>
    </div>

    <!-- Error global -->
    <p v-if="error" class="alert-error" role="alert">{{ error }}</p>

    <!-- ── Paso 1: Selección de equipo ───────────────────────────── -->
    <div v-if="step === 1" class="cotizador-card">
      <header class="step-header">
        <span class="step-badge">Paso 1 de 4</span>
        <h1>Seleccionar equipo</h1>
        <p>Elige la marca y el modelo de tu instrumento.</p>
      </header>

      <div class="form-grid">
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

      <div v-if="loading" class="loading-row">
        <span class="spinner"></span> Cargando…
      </div>

      <div class="actions">
        <router-link to="/" class="btn-secondary">Cancelar</router-link>
        <button
          class="btn-primary"
          :disabled="!canContinueStep1 || loading"
          @click="step = 2"
        >
          Siguiente →
        </button>
      </div>
    </div>

    <!-- ── Paso 2: Selección de fallas ──────────────────────────── -->
    <div v-if="step === 2" class="cotizador-card">
      <header class="step-header">
        <span class="step-badge">Paso 2 de 4</span>
        <h1>Síntomas del equipo</h1>
        <p>Selecciona todo lo que presenta tu <strong>{{ selectedBrandName }} {{ selectedModelName }}</strong>.</p>
      </header>

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
      <header class="step-header">
        <span class="step-badge">Paso 3 de 4</span>
        <h1>Estimación referencial</h1>
        <p>Basada en los síntomas seleccionados y el perfil del equipo.</p>
      </header>

      <div v-if="quoteResult" class="result-box">
        <div class="result-equipment">
          <strong>{{ quoteResult.equipment_info.brand }} {{ quoteResult.equipment_info.model }}</strong>
        </div>

        <div class="result-faults">
          <span v-for="name in selectedFaultNames" :key="name" class="fault-tag">{{ name }}</span>
        </div>

        <div class="result-breakdown">
          <div class="breakdown-row">
            <span>Costo base de diagnóstico</span>
            <span>{{ formatCLP(quoteResult.base_cost) }}</span>
          </div>
          <div class="breakdown-row" v-if="quoteResult.complexity_factor !== 1">
            <span>Factor complejidad (marca)</span>
            <span>× {{ quoteResult.complexity_factor }}</span>
          </div>
          <div class="breakdown-row" v-if="quoteResult.value_factor !== 1">
            <span>Factor valor estimado</span>
            <span>× {{ quoteResult.value_factor }}</span>
          </div>
        </div>

        <div class="result-total">
          <span>Estimación total</span>
          <strong>{{ formattedFinalCost }}</strong>
        </div>
      </div>

      <div class="disclaimer">
        <p>Esta cotización es referencial y no vinculante. El presupuesto formal
           requiere revisión presencial en taller.</p>
      </div>

      <div class="actions">
        <button class="btn-secondary" @click="step = 2">← Atrás</button>
        <button class="btn-primary" @click="step = 4">
          Dejar mis datos →
        </button>
      </div>
    </div>

    <!-- ── Paso 4: Formulario de contacto ────────────────────────── -->
    <div v-if="step === 4" class="cotizador-card">
      <template v-if="!leadSubmitted">
        <header class="step-header">
          <span class="step-badge">Paso 4 de 4</span>
          <h1>Tus datos de contacto</h1>
          <p>Te contactaremos para coordinar la revisión de tu equipo.</p>
        </header>

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

        <TurnstileWidget @verify="onVerify" />

        <div class="actions">
          <button class="btn-secondary" @click="step = 3">← Atrás</button>
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
        <div class="success-box">
          <i class="fa-solid fa-circle-check success-icon"></i>
          <h2>¡Listo, {{ leadForm.nombre.split(' ')[0] }}!</h2>
          <p>
            Recibimos tu solicitud para el
            <strong>{{ selectedBrandName }} {{ selectedModelName }}</strong>.
            Estimación: <strong>{{ formattedFinalCost }}</strong>.
          </p>
          <p>Te contactaremos pronto para coordinar la revisión.</p>
        </div>

        <div class="actions actions--center">
          <button class="btn-secondary" @click="resetAll">Nueva cotización</button>
          <button class="btn-primary" @click="goToSchedule">Agendar ahora</button>
        </div>
      </template>
    </div>

  </div>
</template>

<script setup>
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
  canContinueStep1,
  canContinueStep2,
  canSubmitLead,
  formattedFinalCost,
  selectedBrandName,
  selectedModelName,
  selectedFaultNames,
  onBrandSelect,
  onModelSelect,
  toggleFault,
  calculateQuote,
  submitLead,
  onVerify,
  goToSchedule,
  resetAll
} = useCotizadorIAPage()

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
  transition: width 0.35s ease;
}

/* Alerta de error */
.alert-error {
  max-width: 920px;
  margin: 0 auto;
  width: 100%;
  padding: 0.75rem 1rem;
  background: color-mix(in srgb, var(--cds-primary) 10%, white);
  border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, white);
  border-radius: 0.55rem;
  color: var(--cds-primary);
  font-size: var(--cds-text-sm);
}

/* Card principal */
.cotizador-card {
  max-width: 920px;
  margin: 0 auto;
  width: 100%;
  background: var(--cds-white);
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
  border-radius: 0.95rem;
  padding: 1.25rem 1rem;
  display: grid;
  gap: 1rem;
}

/* Encabezado del paso */
.step-badge {
  font-size: var(--cds-text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--cds-primary);
}

.step-header {
  display: grid;
  gap: 0.25rem;
}

.step-header h1 {
  margin: 0;
  font-size: var(--cds-text-2xl);
  line-height: 1.2;
}

.step-header p {
  margin: 0;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
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
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  border-radius: 0.55rem;
  font-size: 1rem;
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
  gap: 0.55rem;
}

.fault-card {
  display: grid;
  grid-template-columns: 2rem 1fr;
  grid-template-rows: auto auto auto;
  column-gap: 0.6rem;
  row-gap: 0.1rem;
  padding: 0.7rem 0.85rem;
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  border-radius: 0.55rem;
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

/* Caja de resultado */
.result-box {
  border: 1px solid color-mix(in srgb, var(--cds-primary) 25%, white);
  border-radius: 0.7rem;
  padding: 0.9rem;
  display: grid;
  gap: 0.75rem;
}

.result-equipment {
  font-size: var(--cds-text-base);
}

.result-faults {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.fault-tag {
  font-size: var(--cds-text-xs);
  padding: 0.2rem 0.5rem;
  background: color-mix(in srgb, var(--cds-light) 40%, white);
  border-radius: 0.35rem;
  color: var(--cds-text-normal);
}

.result-breakdown {
  display: grid;
  gap: 0.3rem;
  border-top: 1px solid color-mix(in srgb, var(--cds-light) 55%, white);
  padding-top: 0.65rem;
}

.breakdown-row {
  display: flex;
  justify-content: space-between;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.result-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 2px solid color-mix(in srgb, var(--cds-primary) 30%, white);
  padding-top: 0.65rem;
  font-size: var(--cds-text-base);
}

.result-total strong {
  font-size: var(--cds-text-2xl);
  color: var(--cds-primary);
}

/* Disclaimer */
.disclaimer {
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
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

/* Éxito */
.success-box {
  display: grid;
  gap: 0.6rem;
  text-align: center;
  padding: 1rem 0;
}

.success-icon {
  font-size: 2.5rem;
  color: var(--cds-primary);
  margin: 0 auto;
}

.success-box h2 {
  margin: 0;
  font-size: var(--cds-text-xl);
}

.success-box p {
  margin: 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
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
  border-radius: 0.55rem;
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
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  background: var(--cds-white);
  color: var(--cds-text-normal);
}

.btn-secondary:not(:disabled):hover {
  background: color-mix(in srgb, var(--cds-light) 20%, white);
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
