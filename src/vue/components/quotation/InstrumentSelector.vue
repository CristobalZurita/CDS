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

<style lang="scss" scoped>
@use "@/scss/_core.scss" as *;

// Colores legacy centralizados en abstracts/_variables.scss

.instrument-selector {
  padding: $spacer-md;
}

.selection-section {
  margin-bottom: $spacer-xxl;
  padding-bottom: $spacer-xl;
  border-bottom: 2px solid $color-border-light-legacy;

  h3 {
    margin: 0 0 $spacer-lg 0;
    color: $color-text-dark-legacy;
    font-size: $text-xl;
    font-weight: $fw-semibold;
  }
}

.search-box {
  margin-bottom: $spacer-xl;
}

.search-input {
  width: 100%;
  padding: $text-sm $spacer-md;
  font-size: $text-base;
  border: 2px solid $color-border-light-legacy;
  border-radius: $border-radius-md;
  transition: $transition-fast;

  &:focus {
    outline: none;
    border-color: $color-green-primary-legacy;
    box-shadow: 0 0 0 3px rgba($color-green-primary-legacy, 0.1);
  }
}

// Brands Grid
.brands-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: $spacer-md;
}

.brand-card {
  padding: $spacer-lg;
  border: 2px solid $color-border-light-legacy;
  border-radius: $border-radius-lg;
  background: $color-white;
  cursor: pointer;
  text-align: center;
  transition: $transition-fast;
  display: flex;
  flex-direction: column;
  gap: $spacer-sm;

  &:hover {
    border-color: $color-border-hover-legacy;
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba($color-black, 0.08);
  }

  &.active {
    border-color: $color-green-primary-legacy;
    background: $color-green-light-bg-legacy;
    box-shadow: 0 0 0 3px rgba($color-green-primary-legacy, 0.1);
  }
}

.brand-name {
  font-weight: $fw-semibold;
  color: $color-text-dark-legacy;
  font-size: $text-lg;
}

.brand-tier {
  font-size: $text-sm;
  color: $color-text-medium-legacy;
}

.brand-year {
  font-size: $text-xs;
  color: $color-text-light-legacy;
}

// Instruments Grid
.instruments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: $spacer-md;
}

.instrument-card {
  padding: $spacer-md;
  border: 2px solid $color-border-light-legacy;
  border-radius: $border-radius-lg;
  background: $color-white;
  cursor: pointer;
  text-align: center;
  transition: $transition-fast;
  display: flex;
  flex-direction: column;
  gap: $spacer-md;

  &:hover {
    border-color: $color-border-hover-legacy;
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba($color-black, 0.08);
  }

  &.active {
    border-color: $color-green-primary-legacy;
    background: $color-green-light-bg-legacy;
    box-shadow: 0 0 0 3px rgba($color-green-primary-legacy, 0.1);
  }
}

.instrument-image {
  width: 100%;
  height: 150px;
  background: $color-bg-light-legacy;
  border-radius: $border-radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;

  img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;

    &.img-broken {
      display: none !important;
    }
  }
}

.no-image {
  font-size: 3rem;
  color: $color-border-hover-legacy;
}

.instrument-info {
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: $spacer-sm;
}

.instrument-model {
  font-weight: $fw-semibold;
  color: $color-text-dark-legacy;
}

.instrument-year {
  font-size: $text-sm;
  color: $color-text-medium-legacy;
}

.instrument-value {
  font-size: $text-sm;
  color: $color-green-primary-legacy;
  font-weight: $fw-medium;
}

// Confirmation Section
.confirmation-section {
  margin-top: $spacer-xl;
  padding: $spacer-xl;
  background: $color-green-light-bg-legacy;
  border: 2px solid $color-green-border-legacy;
  border-radius: $border-radius-lg;

  h3 {
    margin: 0 0 $spacer-lg 0;
    color: $color-green-text-legacy;
  }
}

.summary-card {
  background: $color-white;
  padding: $spacer-lg;
  border-radius: $border-radius-md;
  margin-bottom: $spacer-lg;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid $color-green-light-bg-legacy;

  &:last-child {
    border-bottom: none;
  }

  .label {
    font-weight: $fw-semibold;
    color: $color-text-dark-legacy;
  }

  .value {
    color: $color-text-gray-legacy;
    text-align: right;
  }
}

.btn-proceed {
  width: 100%;
  padding: $spacer-md;
  background: linear-gradient(135deg, $color-green-primary-legacy, $color-green-dark-legacy);
  color: $color-white;
  border: none;
  border-radius: $border-radius-md;
  font-size: $text-base;
  font-weight: $fw-semibold;
  cursor: pointer;
  transition: $transition-fast;
  box-shadow: 0 4px 12px rgba($color-green-primary-legacy, 0.3);

  &:hover {
    background: linear-gradient(135deg, $color-green-dark-legacy, $color-green-darker-legacy);
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba($color-green-primary-legacy, 0.4);
  }
}

@include media-breakpoint-down(md) {
  .brands-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }

  .instruments-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }

  .confirmation-section {
    padding: $spacer-lg;
  }
}
</style>
