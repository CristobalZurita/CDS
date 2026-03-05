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
          data-testid="quotation-brand-card"
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
          data-testid="quotation-instrument-card"
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

      <button @click="proceed" class="btn-proceed" data-testid="quotation-proceed">
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
  event.target.classList.add('img-broken')
}

const proceed = () => {
  if (selectedInstrument.value) {
    quotationStore.setInstrument(selectedInstrument.value)
    emit('selected', selectedInstrument.value)
  }
}
</script>
