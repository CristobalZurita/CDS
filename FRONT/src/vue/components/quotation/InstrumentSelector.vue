<template>
  <div class="instrument-selector">
    <!-- Brand Selection -->
    <div class="selection-section">
      <h3>1. Selecciona la Marca</h3>
      <div class="search-box">
        <input
          v-model="brandSearch"
          type="text"
          placeholder="Busca marca (Moog, Korg, Roland, etc.)"
          class="search-input"
        />
      </div>

      <div class="brands-grid">
        <button
          v-for="brand in filteredBrands"
          :key="brand.id"
          @click="selectBrand(brand)"
          :class="['brand-card', { active: selectedBrand?.id === brand.id }]"
        >
          <div class="brand-name">{{ brand.name }}</div>
          <div class="brand-tier">{{ getTierLabel(brand.tier) }}</div>
          <div class="brand-year">{{ brand.founded || '—' }}</div>
        </button>
      </div>
    </div>

    <!-- Instrument Selection -->
    <div v-if="selectedBrand" class="selection-section">
      <h3>2. Selecciona el Modelo</h3>
      <div class="search-box">
        <input
          v-model="instrumentSearch"
          type="text"
          placeholder="Busca modelo (Minimoog, TR-808, etc.)"
          class="search-input"
        />
      </div>

      <div class="instruments-grid">
        <button
          v-for="instrument in filteredInstruments"
          :key="instrument.id"
          @click="selectInstrument(instrument)"
          :class="['instrument-card', { active: selectedInstrument?.id === instrument.id }]"
        >
          <div class="instrument-image">
            <img
              v-if="instrument.imagen_url"
              :src="instrument.imagen_url"
              :alt="instrument.model"
              @error="onImageError"
            />
            <div v-else class="no-image">📷</div>
          </div>
          <div class="instrument-info">
            <div class="instrument-model">{{ instrument.model }}</div>
            <div class="instrument-year">{{ instrument.year || '—' }}</div>
            <div v-if="instrument.valor_min" class="instrument-value">
              ${{ formatPrice(instrument.valor_min) }} - ${{ formatPrice(instrument.valor_max) }}
            </div>
          </div>
        </button>
      </div>
    </div>

    <!-- Confirmation -->
    <div v-if="selectedInstrument" class="confirmation-section">
      <div class="selected-summary">
        <h3>Selección Confirmada</h3>
        <div class="summary-card">
          <div class="summary-row">
            <span class="label">Marca:</span>
            <span class="value">{{ selectedBrand.name }}</span>
          </div>
          <div class="summary-row">
            <span class="label">Modelo:</span>
            <span class="value">{{ selectedInstrument.model }}</span>
          </div>
          <div class="summary-row">
            <span class="label">Año:</span>
            <span class="value">{{ selectedInstrument.year || '—' }}</span>
          </div>
          <div class="summary-row">
            <span class="label">Valor Mercado:</span>
            <span class="value">
              ${{ formatPrice(selectedInstrument.valor_min || 0) }} -
              ${{ formatPrice(selectedInstrument.valor_max || 0) }}
            </span>
          </div>
        </div>
      </div>

      <button @click="proceed" class="btn-proceed">
        Continuar al Diagnóstico →
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useInstrumentsCatalog } from '@/composables/useInstrumentsCatalog'
import { useQuotationStore } from '@/stores/quotation'

const emit = defineEmits(['selected'])
const quotationStore = useQuotationStore()

const { brands, getInstrumentsByBrand } = useInstrumentsCatalog()

// State
const brandSearch = ref('')
const instrumentSearch = ref('')
const selectedBrand = ref(null)
const selectedInstrument = ref(null)

// Computed
const filteredBrands = computed(() => {
  if (!brandSearch.value) return brands.value
  const search = brandSearch.value.toLowerCase()
  return brands.value.filter(brand =>
    brand.name.toLowerCase().includes(search) ||
    (brand.country && brand.country.toLowerCase().includes(search))
  )
})

const availableInstruments = computed(() => {
  if (!selectedBrand.value) return []
  return getInstrumentsByBrand(selectedBrand.value.id)
})

const filteredInstruments = computed(() => {
  if (!instrumentSearch.value) return availableInstruments.value
  const search = instrumentSearch.value.toLowerCase()
  return availableInstruments.value.filter(instrument =>
    instrument.model.toLowerCase().includes(search) ||
    (instrument.id && instrument.id.toLowerCase().includes(search))
  )
})

// Methods
const getTierLabel = (tier) => {
  const tierLabels = {
    legendary: '⭐ Legendario',
    professional: '🏆 Profesional',
    historic: '📜 Histórico',
    boutique: '✨ Boutique',
    specialized: '🎯 Especializado',
    standard: '📦 Estándar'
  }
  return tierLabels[tier] || tier
}

const selectBrand = (brand) => {
  selectedBrand.value = brand
  selectedInstrument.value = null
  instrumentSearch.value = ''
}

const selectInstrument = (instrument) => {
  selectedInstrument.value = instrument
}

const formatPrice = (price) => {
  if (!price) return '0'
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(price).replace('$', '')
}

const onImageError = (event) => {
  event.target.style.display = 'none'
}

const proceed = () => {
  if (selectedInstrument.value) {
    quotationStore.setInstrument(selectedInstrument.value)
    emit('selected', selectedInstrument.value)
  }
}
</script>

<style scoped>
.instrument-selector {
  padding: 1rem;
}

.selection-section {
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 2px solid #e2e8f0;
}

.selection-section h3 {
  margin: 0 0 1.5rem 0;
  color: #2d3748;
  font-size: 1.25rem;
  font-weight: 600;
}

.search-box {
  margin-bottom: 2rem;
}

.search-input {
  width: 100%;
  padding: 0.875rem 1rem;
  font-size: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #2f855a;
  box-shadow: 0 0 0 3px rgba(47, 133, 90, 0.1);
}

/* Brands Grid */
.brands-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 1rem;
}

.brand-card {
  padding: 1.5rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  text-align: center;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.brand-card:hover {
  border-color: #cbd5e0;
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
}

.brand-card.active {
  border-color: #2f855a;
  background: #f0fdf4;
  box-shadow: 0 0 0 3px rgba(47, 133, 90, 0.1);
}

.brand-name {
  font-weight: 600;
  color: #2d3748;
  font-size: 1.1rem;
}

.brand-tier {
  font-size: 0.85rem;
  color: #718096;
}

.brand-year {
  font-size: 0.8rem;
  color: #a0aec0;
}

/* Instruments Grid */
.instruments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.instrument-card {
  padding: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  text-align: center;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.instrument-card:hover {
  border-color: #cbd5e0;
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
}

.instrument-card.active {
  border-color: #2f855a;
  background: #f0fdf4;
  box-shadow: 0 0 0 3px rgba(47, 133, 90, 0.1);
}

.instrument-image {
  width: 100%;
  height: 150px;
  background: #f7fafc;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.instrument-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.no-image {
  font-size: 3rem;
  color: #cbd5e0;
}

.instrument-info {
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.instrument-model {
  font-weight: 600;
  color: #2d3748;
}

.instrument-year {
  font-size: 0.85rem;
  color: #718096;
}

.instrument-value {
  font-size: 0.9rem;
  color: #2f855a;
  font-weight: 500;
}

/* Confirmation Section */
.confirmation-section {
  margin-top: 2rem;
  padding: 2rem;
  background: #f0fdf4;
  border: 2px solid #86efac;
  border-radius: 12px;
}

.confirmation-section h3 {
  margin: 0 0 1.5rem 0;
  color: #166534;
}

.summary-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f0fdf4;
}

.summary-row:last-child {
  border-bottom: none;
}

.summary-row .label {
  font-weight: 600;
  color: #2d3748;
}

.summary-row .value {
  color: #4a5568;
  text-align: right;
}

.btn-proceed {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #2f855a, #276749);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(47, 133, 90, 0.3);
}

.btn-proceed:hover {
  background: linear-gradient(135deg, #276749, #22543d);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(47, 133, 90, 0.4);
}

@media (max-width: 768px) {
  .brands-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }

  .instruments-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }

  .confirmation-section {
    padding: 1.5rem;
  }
}
</style>
