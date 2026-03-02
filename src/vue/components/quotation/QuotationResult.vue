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
          <h2>✓ Estimación Referencial Generada</h2>
          <p class="instrument-name">{{ quotation.instrument_name }}</p>
          <p class="tier-badge">{{ quotation.summary?.range_label || 'Rango referencial' }}</p>
        </div>
      </div>

      <!-- Main Content -->
      <div class="result-content">
        <!-- Price Range Section -->
        <div class="price-section">
          <h3>Rango de Precio Estimado</h3>
          <div class="price-range">
            <div class="price-box min-price">
              <span class="label">Desde</span>
              <span class="amount">${{ formatPrice(quotation.min_price) }}</span>
            </div>
            <div class="price-box max-price">
              <span class="label">Hasta</span>
              <span class="amount">${{ formatPrice(quotation.max_price) }}</span>
            </div>
          </div>
          <p class="price-note">
            Este rango es orientativo. El valor real sólo se define después de la revisión física del equipo.
          </p>
        </div>

        <div class="breakdown-section">
          <h3>Factores considerados</h3>
          <div class="breakdown-list">
            <div class="breakdown-item">
              <div class="fault-info">
                <span class="fault-name">Perfil del equipo</span>
              </div>
              <span class="fault-price">{{ quotation.summary?.size_label || 'Equipo a revisar' }}</span>
            </div>
            <div class="breakdown-item">
              <div class="fault-info">
                <span class="fault-name">Síntomas guiados</span>
              </div>
              <span class="fault-price">{{ quotation.summary?.selected_symptom_count || 0 }}</span>
            </div>
            <div class="breakdown-item">
              <div class="fault-info">
                <span class="fault-name">Daños visibles marcados</span>
              </div>
              <span class="fault-price">{{ quotation.summary?.visual_issue_count || 0 }}</span>
            </div>
            <div class="breakdown-item">
              <div class="fault-info">
                <span class="fault-name">Observaciones del cliente</span>
              </div>
              <span class="fault-price">{{ quotation.summary?.notes_present ? 'Sí' : 'No' }}</span>
            </div>
          </div>
        </div>

        <!-- Disclaimer Box -->
        <div class="disclaimer-box">
          <p>{{ quotation.disclaimer }}</p>
        </div>

        <!-- Timestamp -->
        <p class="timestamp">
          Estimación generada: {{ formatDateTime(quotation.created_at) }}
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
