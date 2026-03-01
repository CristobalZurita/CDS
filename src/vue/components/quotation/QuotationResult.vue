<template>
  <div class="quotation-result">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Generando cotización...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <h3>⚠️ Error al generar cotización</h3>
      <p>{{ error }}</p>
      <button @click="$emit('new-quote')" class="btn-btn">Intentar nuevamente</button>
    </div>

    <!-- Success State -->
    <div v-else-if="quotation" class="result-container">
      <!-- Header -->
      <div class="result-header success-gradient">
        <div class="header-content">
          <h2>✓ Cotización Generada</h2>
          <p class="instrument-name">{{ quotation.instrument_name }}</p>
          <p class="tier-badge">{{ quotation.tier_label }}</p>
        </div>
      </div>

      <!-- Main Content -->
      <div class="result-content">
        <!-- Price Range Section -->
        <div class="price-section">
          <h3>Rango de Precio Estimado</h3>
          <div class="price-range">
            <div class="price-box min-price">
              <span class="label">Mínimo</span>
              <span class="amount">${{ formatPrice(quotation.min_price) }}</span>
            </div>
            <div class="price-box max-price">
              <span class="label">Máximo</span>
              <span class="amount">${{ formatPrice(quotation.max_price) }}</span>
            </div>
          </div>
          <p class="price-note">
            Rango base calculado: -20% a +30% del valor estimado
          </p>
        </div>

        <!-- Breakdown Section -->
        <div class="breakdown-section">
          <h3>Desglose de Fallas</h3>
          <div class="breakdown-list">
            <div v-for="fault in quotation.breakdown" :key="fault.fault_id" class="breakdown-item">
              <div class="fault-info">
                <span class="fault-name">{{ fault.name }}</span>
                <span v-if="fault.is_precedence" class="precedence-badge">Bloqueador</span>
              </div>
              <span class="fault-price">${{ formatPrice(fault.base_price) }}</span>
            </div>
          </div>
          <div class="breakdown-total">
            <span>Subtotal (× {{ quotation.multiplier }} por tier)</span>
            <span>${{ formatPrice(quotation.base_total * quotation.multiplier) }}</span>
          </div>
        </div>

        <!-- 50% Rule Warning -->
        <div
          v-if="quotation.exceeds_recommendation"
          class="warning-box"
        >
          <span class="warning-icon">⚠️</span>
          <div>
            <strong>Costo excede el 50% del valor del instrumento</strong>
            <p>
              El precio máximo (${{ formatPrice(quotation.max_price) }})
              supera nuestro compromiso de máximo 50% del valor
              (${{ formatPrice(quotation.max_recommended) }}).
            </p>
            <p>
              Considere si es rentable reparar versus comprar otro equipo.
            </p>
          </div>
        </div>

        <!-- Disclaimer Box -->
        <div class="disclaimer-box">
          <p>{{ quotation.disclaimer }}</p>
        </div>

        <!-- Budget Info -->
        <div class="budget-info">
          <h3>Presupuesto Formal</h3>
          <div class="budget-details">
            <p>
              Costo: <strong>${{ formatPrice(quotation.budget_cost) }}</strong>
            </p>
            <ul>
              <li>
                <strong>ABONABLE:</strong> Se descuenta del total si procede con reparación
              </li>
              <li>
                <strong>NO REEMBOLSABLE:</strong> Si rechaza la reparación, queda como pago
              </li>
            </ul>
          </div>
        </div>

        <!-- Timestamp -->
        <p class="timestamp">
          Cotización generada: {{ formatDateTime(quotation.created_at) }}
        </p>
      </div>

      <!-- Actions -->
      <div class="result-actions">
        <button @click="$emit('new-quote')" class="btn-secondary">
          ← Nueva Cotización
        </button>
        <button @click="$emit('schedule')" class="btn-primary">
          Continuar a Agendar Cita →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  quotation: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  }
})

defineEmits(['new-quote', 'schedule'])

const formatPrice = (price) => {
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(price).replace('$', '')
}

const formatDateTime = (isoString) => {
  if (!isoString) return '-'
  const date = new Date(isoString)
  return date.toLocaleDateString('es-CL', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped lang="scss">
@use '@/scss/core' as *;

.quotation-result {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

// Loading State
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: $spacer-xl;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid $light-2;
  border-top-color: $color-success;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state p {
  font-size: $h6-size;
  color: $light-7;
  font-weight: $fw-medium;
}

// Error State
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: $spacer-lg;
  padding: $spacer-xl;
  background: $color-red-50-legacy;
  border: 2px solid $color-danger;
  border-radius: $border-radius-lg;
}

.error-state h3 {
  color: $color-danger;
  margin: 0;
  font-size: $h5-size;
}

.error-state p {
  color: $color-red-900-legacy;
  text-align: center;
  max-width: 400px;
}

// Result Container
.result-container {
  background: white;
  border-radius: $border-radius-lg;
  overflow: hidden;
  box-shadow: $shadow-lg;
  display: flex;
  flex-direction: column;
  height: 100%;
}

// Header
.result-header {
  padding: $spacer-xl;
  color: white;
  border-bottom: 1px solid rgba($color-black, 0.1);
}

.success-gradient {
  background: linear-gradient(135deg, $color-success, darken($color-success, 10%));
}

.header-content h2 {
  margin: 0 0 $spacer-xs 0;
  font-size: $h3-size;
}

.instrument-name {
  font-size: $h5-size;
  margin: $spacer-xs 0;
  opacity: 0.95;
}

.tier-badge {
  display: inline-block;
  background: rgba($color-white, 0.2);
  padding: $spacer-xs $spacer-md;
  border-radius: $border-radius-pill;
  font-size: $text-sm;
  font-weight: $fw-medium;
  margin-top: $spacer-xs;
}

// Content
.result-content {
  padding: $spacer-xl;
  flex: 1;
  overflow-y: auto;
}

// Price Section
.price-section {
  margin-bottom: $spacer-xl;
  padding-bottom: $spacer-xl;
  border-bottom: 1px solid $light-2;
}

.price-section h3 {
  margin: 0 0 $spacer-lg 0;
  color: $dark;
  font-size: $h6-size;
}

.price-range {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $spacer-md;
  margin-bottom: $spacer-md;
}

.price-box {
  padding: $spacer-lg;
  border-radius: $border-radius-md;
  text-align: center;
}

.price-box .label {
  display: block;
  font-size: $text-xs;
  color: $light-6;
  font-weight: $fw-medium;
  margin-bottom: $spacer-xs;
  text-transform: uppercase;
}

.price-box .amount {
  display: block;
  font-size: $h3-size;
  font-weight: $fw-bold;
  color: $dark;
}

.min-price {
  background: $color-green-light-bg-legacy;
  border: 2px solid $color-green-border-legacy;
}

.max-price {
  background: $color-amber-100-legacy;
  border: 2px solid $color-amber-300-legacy;
}

.price-note {
  color: $light-6;
  font-size: $text-sm;
  text-align: center;
  margin: 0;
}

// Breakdown Section
.breakdown-section {
  margin-bottom: $spacer-xl;
  padding-bottom: $spacer-xl;
  border-bottom: 1px solid $light-2;
}

.breakdown-section h3 {
  margin: 0 0 $spacer-md 0;
  color: $dark;
  font-size: $h6-size;
}

.breakdown-list {
  background: $light-1;
  border-radius: $border-radius-md;
  overflow: hidden;
  margin-bottom: $spacer-md;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacer-md;
  border-bottom: 1px solid $light-2;
}

.breakdown-item:last-child {
  border-bottom: none;
}

.fault-info {
  display: flex;
  align-items: center;
  gap: $spacer-sm;
}

.fault-name {
  font-weight: $fw-medium;
  color: $dark;
}

.precedence-badge {
  background: $color-danger;
  color: white;
  padding: $spacer-xs $spacer-sm;
  border-radius: $border-radius-lg;
  font-size: $text-2xs;
  font-weight: $fw-semibold;
  text-transform: uppercase;
}

.fault-price {
  font-weight: $fw-semibold;
  color: $color-success;
  min-width: 120px;
  text-align: right;
}

.breakdown-total {
  display: flex;
  justify-content: space-between;
  padding: $spacer-md;
  background: white;
  border-top: 2px solid $light-4;
  font-weight: $fw-semibold;
  color: $dark;
}

// Warning Box
.warning-box {
  display: flex;
  gap: $spacer-md;
  padding: $spacer-lg;
  background: $color-red-50-legacy;
  border-left: 4px solid $color-danger;
  border-radius: $border-radius-md;
  margin-bottom: $spacer-xl;
}

.warning-icon {
  font-size: $h2-size;
  flex-shrink: 0;
}

.warning-box strong {
  color: $color-danger;
  display: block;
  margin-bottom: $spacer-xs;
}

.warning-box p {
  margin: $spacer-xs 0;
  color: $color-red-900-legacy;
  font-size: $text-base;
  line-height: $lh-normal;
}

// Disclaimer Box
.disclaimer-box {
  background: $color-green-light-bg-legacy;
  border: 2px solid $color-green-border-legacy;
  border-radius: $border-radius-md;
  padding: $spacer-lg;
  margin-bottom: $spacer-xl;
}

.disclaimer-box p {
  margin: 0;
  color: $color-green-text-legacy;
  font-size: $text-base;
  line-height: $lh-relaxed;
  white-space: pre-wrap;
}

// Budget Info
.budget-info {
  background: $light-1;
  border: 1px solid $light-4;
  border-radius: $border-radius-md;
  padding: $spacer-lg;
  margin-bottom: $spacer-md;
}

.budget-info h3 {
  margin: 0 0 $spacer-md 0;
  color: $dark;
  font-size: $text-base;
}

.budget-details p {
  margin: 0 0 $spacer-sm 0;
  color: $dark;
}

.budget-details strong {
  color: $color-success;
  font-weight: $fw-semibold;
}

.budget-details ul {
  margin: $spacer-sm 0 0 0;
  padding-left: $spacer-lg;
  list-style: none;
}

.budget-details li {
  margin: $spacer-xs 0;
  padding-left: $spacer-lg;
  position: relative;
  color: $light-7;
  font-size: $text-sm;
}

.budget-details li:before {
  content: '✓';
  position: absolute;
  left: 0;
  color: $color-success;
  font-weight: bold;
}

// Timestamp
.timestamp {
  text-align: center;
  color: $light-5;
  font-size: $text-xs;
  margin: 0;
}

// Actions
.result-actions {
  display: flex;
  gap: $spacer-md;
  padding: $spacer-xl;
  border-top: 1px solid $light-2;
  background: $light-1;
  flex-shrink: 0;
}

.btn-primary,
.btn-secondary {
  flex: 1;
  padding: $spacer-md $spacer-lg;
  border-radius: $border-radius-md;
  font-size: $text-base;
  font-weight: $fw-semibold;
  border: none;
  cursor: pointer;
  transition: $transition-fast;
}

.btn-primary {
  background: linear-gradient(135deg, $color-success, darken($color-success, 10%));
  color: white;
  box-shadow: $shadow-md;
}

.btn-primary:hover {
  background: linear-gradient(135deg, darken($color-success, 10%), darken($color-success, 15%));
  transform: translateY(-2px);
  box-shadow: $shadow-lg;
}

.btn-secondary {
  background: white;
  color: $light-7;
  border: 2px solid $light-4;
}

.btn-secondary:hover {
  background: $light-1;
  border-color: $light-5;
}

.btn-btn {
  padding: $spacer-sm $spacer-lg;
  background: $color-success;
  color: white;
  border: none;
  border-radius: $border-radius-md;
  cursor: pointer;
  font-weight: $fw-semibold;
  transition: $transition-fast;
}

.btn-btn:hover {
  background: darken($color-success, 10%);
}

// Responsive
@include media-breakpoint-down(sm) {
  .result-content {
    padding: $spacer-md;
  }

  .price-range {
    grid-template-columns: 1fr;
  }

  .result-header {
    padding: $spacer-lg;
  }

  .header-content h2 {
    font-size: $h4-size;
  }

  .result-actions {
    flex-direction: column;
    padding: $spacer-md;
  }

  .btn-primary,
  .btn-secondary {
    padding: $spacer-sm;
  }

  .warning-box,
  .disclaimer-box,
  .budget-info {
    padding: $spacer-md;
  }
}
</style>
