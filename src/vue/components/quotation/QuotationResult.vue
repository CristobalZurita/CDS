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
@import '@/scss/_core.scss';

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
  background: #fff5f5;
  border: 2px solid $color-danger;
  border-radius: $border-radius-lg;
}

.error-state h3 {
  color: $color-danger;
  margin: 0;
  font-size: $h5-size;
}

.error-state p {
  color: #742a2a;
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
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
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
  background: rgba(255, 255, 255, 0.2);
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
  background: #f0fdf4;
  border: 2px solid #86efac;
}

.max-price {
  background: #fef3c7;
  border: 2px solid #fcd34d;
}

.price-note {
  color: $light-6;
  font-size: $text-sm;
  text-align: center;
  margin: 0;
}

/* Breakdown Section */
.breakdown-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e2e8f0;
}

.breakdown-section h3 {
  margin: 0 0 1rem 0;
  color: #2d3748;
  font-size: 1.1rem;
}

.breakdown-list {
  background: #f7fafc;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.breakdown-item:last-child {
  border-bottom: none;
}

.fault-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.fault-name {
  font-weight: 500;
  color: #2d3748;
}

.precedence-badge {
  background: #c53030;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.fault-price {
  font-weight: 600;
  color: #2f855a;
  min-width: 120px;
  text-align: right;
}

.breakdown-total {
  display: flex;
  justify-content: space-between;
  padding: 1rem;
  background: white;
  border-top: 2px solid #cbd5e0;
  font-weight: 600;
  color: #2d3748;
}

/* Warning Box */
.warning-box {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: #fff5f5;
  border-left: 4px solid #c53030;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.warning-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.warning-box strong {
  color: #c53030;
  display: block;
  margin-bottom: 0.5rem;
}

.warning-box p {
  margin: 0.5rem 0;
  color: #742a2a;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Disclaimer Box */
.disclaimer-box {
  background: #f0fdf4;
  border: 2px solid #86efac;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.disclaimer-box p {
  margin: 0;
  color: #166534;
  font-size: 0.95rem;
  line-height: 1.6;
  white-space: pre-wrap;
}

/* Budget Info */
.budget-info {
  background: #edf2f7;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.budget-info h3 {
  margin: 0 0 1rem 0;
  color: #2d3748;
  font-size: 1rem;
}

.budget-details p {
  margin: 0 0 0.75rem 0;
  color: #2d3748;
}

.budget-details strong {
  color: #2f855a;
  font-weight: 600;
}

.budget-details ul {
  margin: 0.75rem 0 0 0;
  padding-left: 1.5rem;
  list-style: none;
}

.budget-details li {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
  position: relative;
  color: #4a5568;
  font-size: 0.9rem;
}

.budget-details li:before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #2f855a;
  font-weight: bold;
}

/* Timestamp */
.timestamp {
  text-align: center;
  color: #a0aec0;
  font-size: 0.85rem;
  margin: 0;
}

/* Actions */
.result-actions {
  display: flex;
  gap: 1rem;
  padding: 2rem;
  border-top: 1px solid #e2e8f0;
  background: #f9fafb;
  flex-shrink: 0;
}

.btn-primary,
.btn-secondary {
  flex: 1;
  padding: 1rem 1.75rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #2f855a, #276749);
  color: white;
  box-shadow: 0 4px 12px rgba(47, 133, 90, 0.3);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #276749, #22543d);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(47, 133, 90, 0.4);
}

.btn-secondary {
  background: white;
  color: #4a5568;
  border: 2px solid #cbd5e0;
}

.btn-secondary:hover {
  background: #edf2f7;
  border-color: #a0aec0;
}

.btn-btn {
  padding: 0.75rem 1.5rem;
  background: #2f855a;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-btn:hover {
  background: #276749;
}

/* Responsive */
@media (max-width: 640px) {
  .result-content {
    padding: 1rem;
  }

  .price-range {
    grid-template-columns: 1fr;
  }

  .result-header {
    padding: 1.5rem;
  }

  .header-content h2 {
    font-size: 1.4rem;
  }

  .result-actions {
    flex-direction: column;
    padding: 1rem;
  }

  .btn-primary,
  .btn-secondary {
    padding: 0.75rem;
  }

  .warning-box,
  .disclaimer-box,
  .budget-info {
    padding: 1rem;
  }
}
</style>
