<template>
  <div class="cotizador-card">
    <CotizadorStepHeader badge="Paso 2 de 4" title="Síntomas del equipo">
      <template #description>
        Selecciona todo lo que presenta tu <strong>{{ selectedBrandName }} {{ selectedModelName }}</strong>.
      </template>
    </CotizadorStepHeader>

    <div v-if="loading" class="loading-row">
      <span class="spinner"></span> Cargando fallas disponibles…
    </div>

    <template v-else>
      <!-- Imagen interactiva del instrumento -->
      <div v-if="modelImage && faultsWithCoords.length" class="instrument-map-wrap">
        <div class="instrument-map" :style="{ backgroundImage: `url(${resolvedImage})` }">
          <img
            :src="resolvedImage"
            :alt="selectedModelName"
            class="instrument-map-img"
            @error="imageError = true"
          />
          <!-- Zonas clicables sobre la imagen -->
          <button
            v-for="fault in faultsWithCoords"
            :key="fault.id"
            type="button"
            class="zone-btn"
            :class="{ 'zone-btn--selected': selectedFaultIds.includes(fault.id) }"
            :style="{
              left:   fault.coords.x + '%',
              top:    fault.coords.y + '%',
              width:  fault.coords.w + '%',
              height: fault.coords.h + '%',
            }"
            :title="fault.name"
            @click="emit('toggle-fault', fault.id)"
          >
            <span class="zone-label">{{ fault.name }}</span>
          </button>
        </div>
        <p class="map-hint"><i class="fas fa-hand-pointer"></i> Toca las zonas afectadas en la imagen o usa las tarjetas debajo</p>
      </div>

      <!-- Tarjetas de fallas (siempre visibles) -->
      <div class="faults-grid">
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
            @change="emit('toggle-fault', fault.id)"
          />
          <span class="fault-icon">
            <i :class="`fa-solid ${zoneIcon(fault.id)}`"></i>
          </span>
          <span class="fault-name">{{ fault.name }}</span>
          <span v-if="fault.fallas_comunes?.length" class="fault-desc">
            {{ fault.fallas_comunes.slice(0, 2).join(' · ') }}
          </span>
        </label>
      </div>

      <TurnstileWidget
        :key="quoteTurnstileRenderKey"
        @verify="emit('quote-verify', $event)"
      />
    </template>

    <div class="actions">
      <button class="btn-secondary" @click="emit('back')">← Atrás</button>
      <button
        class="btn-primary"
        :disabled="!canContinueStep2 || loading"
        @click="emit('continue')"
      >
        <span v-if="loading"><span class="spinner spinner--sm"></span> Calculando…</span>
        <span v-else>Ver estimación →</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import CotizadorStepHeader from '@/components/business/CotizadorStepHeader.vue'
import TurnstileWidget from '@/components/widgets/TurnstileWidget.vue'

const props = defineProps({
  loading:               { type: Boolean, default: false },
  selectedBrandName:     { type: String,  required: true },
  selectedModelName:     { type: String,  required: true },
  modelImage:            { type: String,  default: '' },
  faults:                { type: Array,   default: () => [] },
  selectedFaultIds:      { type: Array,   default: () => [] },
  quoteTurnstileRenderKey: { type: Number, default: 0 },
  canContinueStep2:      { type: Boolean, default: false },
})

const emit = defineEmits(['toggle-fault', 'quote-verify', 'back', 'continue'])

const imageError = ref(false)

const resolvedImage = computed(() => {
  if (!props.modelImage || imageError.value) return ''
  if (props.modelImage.startsWith('http')) return props.modelImage
  return `/images/INVENTARIO/${props.modelImage}`
})

// Solo zonas que tienen coords definidos
const faultsWithCoords = computed(() =>
  props.faults.filter(f => f.coords?.w && f.coords?.h)
)

const _ZONE_ICONS = {
  keys: 'fa-piano-keyboard',
  psu: 'fa-bolt',
  display: 'fa-display',
  voice_board: 'fa-microchip',
  dsp_board: 'fa-microchip',
  audio_io: 'fa-plug',
  midi: 'fa-music',
  encoders: 'fa-rotate',
  pads: 'fa-table-cells',
  faders: 'fa-sliders',
  ribbon: 'fa-arrows-left-right',
  screen: 'fa-display',
  firmware: 'fa-code',
}

function zoneIcon(id) {
  return _ZONE_ICONS[id] || 'fa-wrench'
}
</script>

<style scoped>
@import './cotizadorStepShared.css';

/* ── Mapa interactivo ─────────────────────────────────────────── */
.instrument-map-wrap {
  margin-bottom: var(--cds-space-md);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.instrument-map {
  position: relative;
  width: 100%;
  border-radius: var(--cds-radius-md);
  overflow: hidden;
  border: 1px solid var(--cds-border-card);
  background: var(--cds-surface-2) center/cover no-repeat;
  user-select: none;
}

.instrument-map-img {
  width: 100%;
  height: auto;
  display: block;
  max-height: 260px;
  object-fit: cover;
  pointer-events: none;
}

.zone-btn {
  position: absolute;
  background: rgba(236,107,0, 0.10);
  border: 2px solid rgba(236,107,0, 0.35);
  border-radius: var(--cds-radius-sm);
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
  display: flex;
  align-items: flex-end;
  padding: 0.2rem 0.35rem;
  overflow: hidden;
}

.zone-btn:hover {
  background: rgba(236,107,0, 0.22);
  border-color: var(--cds-primary);
}

.zone-btn--selected {
  background: rgba(236,107,0, 0.30);
  border-color: var(--cds-primary);
  border-width: 2px;
}

.zone-label {
  font-size: 0.6rem;
  font-weight: 700;
  color: var(--cds-primary);
  text-shadow: 0 1px 2px rgba(255,255,255,0.9);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  line-height: 1;
  pointer-events: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.zone-btn--selected .zone-label {
  color: var(--cds-white);
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}

.map-hint {
  font-size: var(--cds-text-xs);
  color: var(--cds-text-muted);
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin: 0;
}

/* ── Tarjetas de falla ────────────────────────────────────────── */
.faults-grid {
  display: grid;
  gap: var(--cds-space-xs);
}

.fault-card {
  display: grid;
  grid-template-columns: 2rem 1fr;
  grid-template-rows: auto auto;
  column-gap: 0.6rem;
  row-gap: 0.1rem;
  padding: 0.7rem 0.85rem;
  border: 1px solid var(--cds-border-input);
  border-radius: var(--cds-radius-sm);
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.fault-card:hover        { border-color: var(--cds-border-card); background: var(--cds-surface-2); }
.fault-card--selected    { border-color: var(--cds-primary);     background: var(--cds-surface-1); }

.fault-icon {
  grid-row: 1 / 3;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--cds-primary);
  font-size: 1rem;
}

.fault-name { font-weight: 600; font-size: var(--cds-text-sm); align-self: end; }

.fault-desc {
  grid-column: 2;
  font-size: var(--cds-text-xs);
  color: var(--cds-text-muted);
  line-height: 1.4;
}

@media (min-width: 640px) {
  .faults-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .instrument-map-img { max-height: 300px; }
}

@media (min-width: 1024px) {
  .faults-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
</style>
