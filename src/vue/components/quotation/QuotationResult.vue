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
