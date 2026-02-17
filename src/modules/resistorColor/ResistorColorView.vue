<template>
  <PageSection variant="default" id="resistor-color-calculator">
    <PageSectionHeader
      title="*Calculadora* de Resistencias"
      subtitle="Codigo de colores para resistencias THT de 4, 5 y 6 bandas"
    />

    <PageSectionContent>
      <div class="resistor-layout">
        <div class="resistor-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-palette"></i>
              Parametros
            </div>
            <div class="panel-tabs">
              <button
                v-for="b in [4, 5, 6]"
                :key="b"
                type="button"
                class="panel-tab"
                :class="{ active: input.bands === b }"
                @click="setBands(b)"
              >
                {{ b }} bandas
              </button>
            </div>
          </div>

          <form class="panel-form" @submit.prevent="onCalculate">
            <div class="form-grid">
              <div class="form-field">
                <label>1ra banda</label>
                <select v-model="input.colors[0]">
                  <option v-for="c in digitColors" :key="c.value" :value="c.value">
                    {{ c.label }}
                  </option>
                </select>
              </div>
              <div class="form-field">
                <label>2da banda</label>
                <select v-model="input.colors[1]">
                  <option v-for="c in digitColors" :key="c.value" :value="c.value">
                    {{ c.label }}
                  </option>
                </select>
              </div>
              <div class="form-field" v-if="input.bands >= 5">
                <label>3ra banda</label>
                <select v-model="input.colors[2]">
                  <option v-for="c in digitColors" :key="c.value" :value="c.value">
                    {{ c.label }}
                  </option>
                </select>
              </div>
              <div class="form-field">
                <label>Multiplicador</label>
                <select v-model="input.colors[multiplierIndex]">
                  <option v-for="c in multiplierColors" :key="c.value" :value="c.value">
                    {{ c.label }}
                  </option>
                </select>
              </div>
              <div class="form-field">
                <label>Tolerancia</label>
                <select v-model="input.colors[toleranceIndex]">
                  <option v-for="c in toleranceColors" :key="c.value" :value="c.value">
                    {{ c.label }}
                  </option>
                </select>
              </div>
              <div class="form-field" v-if="input.bands === 6">
                <label>Tempco</label>
                <select v-model="input.colors[tempcoIndex]">
                  <option v-for="c in tempcoColors" :key="c.value" :value="c.value">
                    {{ c.label }}
                  </option>
                </select>
              </div>
            </div>

            <div class="form-actions">
              <button type="submit" class="btn-primary-action">
                Calcular
              </button>
              <button type="button" class="btn-secondary-action" @click="reset">
                Limpiar
              </button>
            </div>
          </form>
        </div>

        <div class="resistor-panel output-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-wave-square"></i>
              Resultado
            </div>
          </div>

          <div class="output-body">
            <div class="resistor-visual">
              <div class="resistor-body">
                <span
                  v-for="(color, index) in previewBands"
                  :key="`${color}-${index}`"
                  :class="['band', bandClass(color)]"
                ></span>
              </div>
            </div>

            <div class="output-value">
              <div class="value-label">Resistencia</div>
              <div class="value-main">{{ formattedResistance }}</div>
              <div class="value-range" v-if="resultValue">
                {{ formattedRange }}
              </div>
              <div class="value-meta" v-if="resultValue && resultValue.tempco_ppm">
                Tempco: {{ resultValue.tempco_ppm }} ppm
              </div>
            </div>

            <div class="output-hint">
              Selecciona las bandas y presiona calcular para obtener el valor.
            </div>

          </div>
        </div>
      </div>

      <div class="resistor-divider">
        <span>Resistencias SMD</span>
      </div>

      <div class="smd-layout">
        <div class="resistor-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-hashtag"></i>
              Codigo SMD
            </div>
          </div>

          <form class="panel-form" @submit.prevent="onSmdCalculate">
            <div class="form-grid">
              <div class="form-field">
                <label>Codigo</label>
                <input v-model.trim="smdInput.code" type="text" placeholder="Ej: 103, 01C" />
              </div>
              <div class="form-field">
                <label>Tipo</label>
                <select v-model="smdInput.type">
                  <option value="EIA3">EIA-3</option>
                  <option value="EIA4">EIA-4</option>
                  <option value="EIA96">EIA-96</option>
                </select>
              </div>
            </div>

            <div class="form-actions">
              <button type="submit" class="btn-primary-action">
                Calcular
              </button>
              <button type="button" class="btn-secondary-action" @click="resetSmd">
                Limpiar
              </button>
            </div>
          </form>
        </div>

        <div class="resistor-panel output-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-circle-dot"></i>
              Resultado
            </div>
          </div>

          <div class="output-body">
            <div class="output-value">
              <div class="value-label">Resistencia</div>
              <div class="value-main">{{ smdFormattedResistance }}</div>
            </div>
            <div class="output-hint">
              Ingresa el codigo impreso en la resistencia SMD.
            </div>
          </div>
        </div>
      </div>

      <div class="resistor-back">
        <Link url="/calculadoras">
          <span class="resistor-back-link">← VOLVER A CALCULADORAS</span>
        </Link>
      </div>
    </PageSectionContent>
  </PageSection>

  <Footer>
    <FooterBlock :darken="false" :row="true">
      <FooterColumn
        title="Sobre el taller"
        faIcon="pi pi-lightbulb me-2"
        :description="[
          `Cirujano de Sintetizadores es un taller especializado en reparación, restauración y modificación de sintetizadores, teclados y equipos de audio profesionales.`,
          `Trabajamos con diagnóstico detallado, repuestos de calidad y un enfoque orientado a conservar y realzar el carácter sonoro original de cada instrumento.`
        ]"
        :links="[]"
        :displayLinksAsButtons="false"
      />

      <FooterColumn
        title="Redes y presencia"
        faIcon=""
        :description="[]"
        :links="[
          { label: `Instagram`, href: `https://www.instagram.com/cirujanodesintetizadores/`, faIcon: `fa-brands fa-instagram` },
          { label: `Facebook`, href: `https://www.facebook.com/Cirujanodesintetizadores/`, faIcon: `fa-brands fa-facebook` }
        ]"
        :displayLinksAsButtons="true"
      />

      <FooterColumn
        title="Información de contacto"
        faIcon="pi pi-envelope me-2 pe-1"
        :description="[
          `Valparaíso – Chile`,
          `Atención con coordinación previa.`
        ]"
        :links="[
          { label: `+56 9 8295 7538`, href: `tel:+56982957538`, faIcon: 'pi pi-phone' },
          { label: `contacto@cirujanodesintetizadores.com`, href: `mailto:contacto@cirujanodesintetizadores.com`, faIcon: 'fa-regular fa-envelope' }
        ]"
        :displayLinksAsButtons="false"
      />
    </FooterBlock>

    <FooterBlock :darken="false" :row="false">
      <div class="footer-legal-row">
        <router-link to="/privacidad">Política de privacidad</router-link>
        <span class="footer-legal-sep">·</span>
        <router-link to="/terminos">Términos y condiciones</router-link>
        <span class="footer-legal-sep">·</span>
        <a href="https://github.com/CristobalZurita/cirujano-front" target="_blank" rel="noopener noreferrer">
          Repositorio del proyecto
        </a>
      </div>
    </FooterBlock>

    <FooterBlock :darken="true" :row="false">
      <FooterCopyright
        holder="Cirujano de Sintetizadores"
        url="https://www.cirujanodesintetizadores.cl"
        license="Todos los derechos reservados"
      />
    </FooterBlock>
  </Footer>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue'
import { useCalculator } from '@/composables/useCalculator'
import { ResistorColorInput, ResistorColorOutput } from '@/domain/resistorColor/contract'
import { SmdResistorInput, SmdResistorOutput } from '@/domain/smdResistor/contract'
import { calculateResistorColor } from '@/domain/resistorColor/model'
import { calculateSmdResistor } from '@/domain/smdResistor/model'
import { createValidationResult } from '@/validation'
import PageSection from '/src/vue/components/layout/PageSection.vue'
import PageSectionHeader from '/src/vue/components/layout/PageSectionHeader.vue'
import PageSectionContent from '/src/vue/components/layout/PageSectionContent.vue'
import Link from '/src/vue/components/generic/Link.vue'
import Footer from '/src/vue/components/footer/Footer.vue'
import FooterBlock from '/src/vue/components/footer/FooterBlock.vue'
import FooterColumn from '/src/vue/components/footer/FooterColumn.vue'
import FooterCopyright from '/src/vue/components/footer/FooterCopyright.vue'

type ColorOption = {
  value: string
  label: string
  bg: string
  fg: string
}

const getBandColor = (name: string) => {
  if (typeof window === 'undefined') return 'transparent'
  const root = document.getElementById('resistor-color-calculator')
  const styles = root ? getComputedStyle(root) : null
  return styles?.getPropertyValue(name).trim() || 'transparent'
}

const colorMap: Record<string, { bg: string; fg: string }> = {
  black: { bg: getBandColor('--resistor-black-bg'), fg: getBandColor('--resistor-black-fg') },
  brown: { bg: getBandColor('--resistor-brown-bg'), fg: getBandColor('--resistor-brown-fg') },
  red: { bg: getBandColor('--resistor-red-bg'), fg: getBandColor('--resistor-red-fg') },
  orange: { bg: getBandColor('--resistor-orange-bg'), fg: getBandColor('--resistor-orange-fg') },
  yellow: { bg: getBandColor('--resistor-yellow-bg'), fg: getBandColor('--resistor-yellow-fg') },
  green: { bg: getBandColor('--resistor-green-bg'), fg: getBandColor('--resistor-green-fg') },
  blue: { bg: getBandColor('--resistor-blue-bg'), fg: getBandColor('--resistor-blue-fg') },
  violet: { bg: getBandColor('--resistor-violet-bg'), fg: getBandColor('--resistor-violet-fg') },
  gray: { bg: getBandColor('--resistor-gray-bg'), fg: getBandColor('--resistor-gray-fg') },
  white: { bg: getBandColor('--resistor-white-bg'), fg: getBandColor('--resistor-white-fg') },
  gold: { bg: getBandColor('--resistor-gold-bg'), fg: getBandColor('--resistor-gold-fg') },
  silver: { bg: getBandColor('--resistor-silver-bg'), fg: getBandColor('--resistor-silver-fg') }
}

const digitColors: ColorOption[] = [
  'black',
  'brown',
  'red',
  'orange',
  'yellow',
  'green',
  'blue',
  'violet',
  'gray',
  'white'
].map((value, index) => ({
  value,
  label: `${value.charAt(0).toUpperCase()}${value.slice(1)} (${index})`,
  ...colorMap[value]
}))

const multiplierColors: ColorOption[] = [
  { value: 'black', label: 'Negro (x1)' },
  { value: 'brown', label: 'Cafe (x10)' },
  { value: 'red', label: 'Rojo (x100)' },
  { value: 'orange', label: 'Naranjo (x1k)' },
  { value: 'yellow', label: 'Amarillo (x10k)' },
  { value: 'green', label: 'Verde (x100k)' },
  { value: 'blue', label: 'Azul (x1M)' },
  { value: 'violet', label: 'Violeta (x10M)' },
  { value: 'gray', label: 'Gris (x100M)' },
  { value: 'white', label: 'Blanco (x1G)' },
  { value: 'gold', label: 'Dorado (x0.1)' },
  { value: 'silver', label: 'Plateado (x0.01)' }
].map((option) => ({
  ...option,
  ...colorMap[option.value]
}))

const toleranceColors: ColorOption[] = [
  { value: 'brown', label: 'Cafe (±1%)' },
  { value: 'red', label: 'Rojo (±2%)' },
  { value: 'green', label: 'Verde (±0.5%)' },
  { value: 'blue', label: 'Azul (±0.25%)' },
  { value: 'violet', label: 'Violeta (±0.1%)' },
  { value: 'gray', label: 'Gris (±0.05%)' },
  { value: 'gold', label: 'Dorado (±5%)' },
  { value: 'silver', label: 'Plateado (±10%)' }
].map((option) => ({
  ...option,
  ...colorMap[option.value]
}))

const tempcoColors: ColorOption[] = [
  { value: 'brown', label: 'Cafe (100 ppm)' },
  { value: 'red', label: 'Rojo (50 ppm)' },
  { value: 'orange', label: 'Naranjo (15 ppm)' },
  { value: 'yellow', label: 'Amarillo (25 ppm)' },
  { value: 'blue', label: 'Azul (10 ppm)' },
  { value: 'violet', label: 'Violeta (5 ppm)' }
].map((option) => ({
  ...option,
  ...colorMap[option.value]
}))

const input = reactive<ResistorColorInput>({
  bands: 4,
  colors: ['brown', 'black', 'red', 'gold']
})

const { result, calculate } = useCalculator(
  () => createValidationResult(),
  calculateResistorColor
)

const smdInput = reactive<SmdResistorInput>({
  code: '',
  type: 'EIA3'
})

const { result: smdResult, calculate: calculateSmd } = useCalculator(
  () => createValidationResult(),
  calculateSmdResistor
)

const multiplierIndex = computed(() => (input.bands >= 5 ? 3 : 2))
const toleranceIndex = computed(() => multiplierIndex.value + 1)
const tempcoIndex = computed(() => toleranceIndex.value + 1)

const previewBands = computed(() => {
  const bands = input.colors.slice(0, toleranceIndex.value + 1)
  if (input.bands === 6) {
    bands.push(input.colors[tempcoIndex.value] || 'brown')
  }
  return bands
})

const resultValue = computed(() => (result.value?.state === 'OK' ? (result.value.value as ResistorColorOutput) : null))
const smdResultValue = computed(() =>
  smdResult.value?.state === 'OK' ? (smdResult.value.value as SmdResistorOutput) : null
)

const formattedResistance = computed(() => {
  if (!resultValue.value) return '---'
  const value = resultValue.value.resistance_ohm
  return formatOhms(value)
})

const formattedRange = computed(() => {
  if (!resultValue.value) return ''
  const min = formatOhms(resultValue.value.min_ohm)
  const max = formatOhms(resultValue.value.max_ohm)
  return `Rango: ${min} — ${max}`
})

const smdFormattedResistance = computed(() => {
  if (!smdResultValue.value || !Number.isFinite(smdResultValue.value.resistance_ohm)) {
    return '---'
  }
  return formatOhms(smdResultValue.value.resistance_ohm)
})

function onCalculate() {
  calculate(input)
}

function setBands(bands: number) {
  input.bands = bands
  if (bands === 4) {
    input.colors = ['brown', 'black', 'red', 'gold']
  }
  if (bands === 5) {
    input.colors = ['brown', 'black', 'black', 'red', 'brown']
  }
  if (bands === 6) {
    input.colors = ['brown', 'black', 'black', 'red', 'brown', 'brown']
  }
}

function reset() {
  setBands(4)
  result.value = null
}

function onSmdCalculate() {
  calculateSmd(smdInput)
}

function resetSmd() {
  smdInput.code = ''
  smdInput.type = 'EIA3'
  smdResult.value = null
}

function bandClass(color: string) {
  const normalized = String(color || '').toLowerCase()
  if (!normalized) return 'band-default'
  return `band-${normalized}`
}

function formatOhms(value: number) {
  if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(2)} GΩ`
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(2)} MΩ`
  if (value >= 1_000) return `${(value / 1_000).toFixed(2)} kΩ`
  return `${value.toFixed(2)} Ω`
}
</script>

<style scoped lang="scss">
@import "/src/scss/_theming.scss";

#resistor-color-calculator {
  --resistor-default-band: #{$color-sand-300-legacy};
  --resistor-black-bg: #{$color-resistor-black-legacy};
  --resistor-black-fg: #{$color-resistor-white-legacy};
  --resistor-brown-bg: #{$color-resistor-brown-legacy};
  --resistor-brown-fg: #{$color-resistor-white-legacy};
  --resistor-red-bg: #{$color-resistor-red-legacy};
  --resistor-red-fg: #{$color-resistor-white-legacy};
  --resistor-orange-bg: #{$color-resistor-orange-legacy};
  --resistor-orange-fg: #{$color-resistor-darktext-legacy};
  --resistor-yellow-bg: #{$color-resistor-yellow-legacy};
  --resistor-yellow-fg: #{$color-resistor-darktext-legacy};
  --resistor-green-bg: #{$color-resistor-green-legacy};
  --resistor-green-fg: #{$color-resistor-white-legacy};
  --resistor-blue-bg: #{$color-resistor-blue-legacy};
  --resistor-blue-fg: #{$color-resistor-white-legacy};
  --resistor-violet-bg: #{$color-resistor-violet-legacy};
  --resistor-violet-fg: #{$color-resistor-white-legacy};
  --resistor-gray-bg: #{$color-resistor-gray-legacy};
  --resistor-gray-fg: #{$color-resistor-white-legacy};
  --resistor-white-bg: #{$color-resistor-white-legacy};
  --resistor-white-fg: #{$color-resistor-darktext-legacy};
  --resistor-gold-bg: #{$color-resistor-gold-legacy};
  --resistor-gold-fg: #{$color-resistor-darktext-legacy};
  --resistor-silver-bg: #{$color-resistor-silver-legacy};
  --resistor-silver-fg: #{$color-resistor-darktext-legacy};
  .resistor-layout {
    display: grid;
    grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
    gap: 1.6rem;

    @include media-breakpoint-down(lg) {
      grid-template-columns: 1fr;
    }
  }

  .resistor-panel {
    background: rgba($light-1, 0.8);
    border: 1px solid rgba($dark, 0.1);
    border-radius: 22px;
    padding: 1.8rem;
    box-shadow: 0 20px 40px rgba($dark, 0.08);
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .panel-title {
    font-family: 'Cervo Neue', $headings-font-family;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: $dark;
    display: flex;
    align-items: center;
    gap: 0.6rem;
  }

  .panel-tabs {
    display: flex;
    gap: 0.5rem;
    background: rgba($dark, 0.05);
    padding: 0.35rem;
    border-radius: 999px;
  }

  .panel-tab {
    border: none;
    background: transparent;
    padding: 0.35rem 0.95rem;
    border-radius: 999px;
    font-family: 'Cervo Neue', $font-family-base;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-size: 0.75rem;
    color: $dark;
    cursor: pointer;
  }

  .panel-tab.active {
    background: $primary;
    color: $light-1;
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;

    @include media-breakpoint-down(sm) {
      grid-template-columns: 1fr;
    }
  }

  .form-field {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    font-family: 'Cervo Neue', $font-family-base;
    color: $dark;
  }

  .form-field label {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
  }

  .form-field select {
    border: 1px solid rgba($dark, 0.2);
    border-radius: 12px;
    padding: 0.65rem 0.75rem;
    font-family: 'Cervo Neue', $font-family-base;
    font-size: 0.95rem;
    background: $light-1;
    color: $dark;
  }

  .form-actions {
    display: flex;
    gap: 0.8rem;
    margin-top: 1.5rem;
  }

  .btn-primary-action,
  .btn-secondary-action {
    border: none;
    border-radius: 999px;
    padding: 0.65rem 1.6rem;
    font-family: 'Cervo Neue', $font-family-base;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    cursor: pointer;
  }

  .btn-primary-action {
    background: $primary;
    color: $light-1;
  }

  .btn-secondary-action {
    background: transparent;
    border: 1px solid rgba($dark, 0.3);
    color: $dark;
  }

  .output-panel {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .output-body {
    display: flex;
    flex-direction: column;
    gap: 1.4rem;
    align-items: center;
    text-align: center;
  }

  .resistor-visual {
    width: 100%;
    display: flex;
    justify-content: center;
  }

  .resistor-body {
    position: relative;
    width: min(100%, 320px);
    height: 70px;
    background: $color-sand-200-legacy;
    border-radius: 40px;
    box-shadow: inset 0 0 0 6px rgba($color-black, 0.05);
    display: flex;
    align-items: center;
    justify-content: space-evenly;
    padding: 0 1.2rem;
  }

  .band {
    width: 12px;
    height: 60%;
    border-radius: 6px;
    box-shadow: inset 0 0 0 2px rgba($color-black, 0.1);
  }

  .band-default { background: var(--resistor-default-band); }
  .band-black { background: var(--resistor-black-bg); }
  .band-brown { background: var(--resistor-brown-bg); }
  .band-red { background: var(--resistor-red-bg); }
  .band-orange { background: var(--resistor-orange-bg); }
  .band-yellow { background: var(--resistor-yellow-bg); }
  .band-green { background: var(--resistor-green-bg); }
  .band-blue { background: var(--resistor-blue-bg); }
  .band-violet { background: var(--resistor-violet-bg); }
  .band-gray { background: var(--resistor-gray-bg); }
  .band-white { background: var(--resistor-white-bg); }
  .band-gold { background: var(--resistor-gold-bg); }
  .band-silver { background: var(--resistor-silver-bg); }

  .output-value {
    font-family: 'Cervo Neue', $headings-font-family;
    color: $dark;
  }

  .value-label {
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.75rem;
    color: $text-muted;
  }

  .value-main {
    font-size: 2.1rem;
    font-weight: 800;
    margin-top: 0.3rem;
  }

  .value-range,
  .value-meta {
    font-family: 'Cervo Neue', $font-family-base;
    font-size: 0.9rem;
    color: $text-muted;
  }

  .output-hint {
    font-size: 0.85rem;
    color: $text-muted;
    max-width: 260px;
  }

  .resistor-divider {
    margin: 2.8rem 0 1.6rem;
    text-align: center;
    font-family: 'Cervo Neue', $headings-font-family;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: $primary;
  }

  .smd-layout {
    display: grid;
    grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
    gap: 1.6rem;

    @include media-breakpoint-down(lg) {
      grid-template-columns: 1fr;
    }
  }

  .resistor-back {
    display: flex;
    justify-content: center;
    margin-top: 2.5rem;
  }

  .resistor-back-link {
    font-family: 'Cervo Neue', $headings-font-family;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: $primary;
  }
}
</style>
