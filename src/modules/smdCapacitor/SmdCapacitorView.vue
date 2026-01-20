<template>
  <PageSection variant="default" id="smd-capacitor-calculator">
    <PageSectionHeader
      title="*Conversión* de Capacitancia"
      subtitle="Cerámicos y poliester: lectura por código"
    />

    <PageSectionContent>
      <div class="cap-layout">
        <div class="cap-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-scale-balanced"></i>
              Conversión de unidades
            </div>
          </div>

          <div class="panel-form">
            <div class="cap-visual-inline">
              <img src="/images/calculadoras/CAP_E.svg" alt="Capacitor electrolítico" />
              <p>Electrolítico (Cap E)</p>
            </div>
            <div class="form-grid form-grid-wide">
              <div class="form-field">
                <label>Picofarad</label>
                <div class="unit-input">
                  <input
                    v-model.number="conversion.pf"
                    type="number"
                    min="0"
                    step="0.1"
                    @input="onConversionInput('pf')"
                  />
                  <span class="unit-tag">pF</span>
                </div>
              </div>
              <div class="form-field">
                <label>Nanofarad</label>
                <div class="unit-input">
                  <input
                    v-model.number="conversion.nf"
                    type="number"
                    min="0"
                    step="0.1"
                    @input="onConversionInput('nf')"
                  />
                  <span class="unit-tag">nF</span>
                </div>
              </div>
              <div class="form-field">
                <label>Microfarad</label>
                <div class="unit-input">
                  <input
                    v-model.number="conversion.uf"
                    type="number"
                    min="0"
                    step="0.1"
                    @input="onConversionInput('uf')"
                  />
                  <span class="unit-tag">µF</span>
                </div>
              </div>
              <div class="form-field">
                <label>Farad</label>
                <div class="unit-input">
                  <input
                    v-model.number="conversion.f"
                    type="number"
                    min="0"
                    step="0.1"
                    @input="onConversionInput('f')"
                  />
                  <span class="unit-tag">F</span>
                </div>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" class="btn-secondary-action" @click="resetConversion">
                Limpiar
              </button>
            </div>
          </div>
        </div>

        <div class="cap-panel output-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-hashtag"></i>
              Código cerámico / poliester
            </div>
          </div>

          <form class="panel-form" @submit.prevent="onDecode">
            <div class="cap-visual-inline">
              <img src="/images/calculadoras/CAP_C.png" alt="Capacitor cerámico" />
              <p>Cerámico (Cap C)</p>
            </div>
            <div class="form-grid">
              <div class="form-field">
                <label>Código (3 dígitos)</label>
                <input v-model.trim="code.value" type="text" placeholder="Ej: 104, 472" />
              </div>
              <div class="form-field">
                <label>Tolerancia</label>
                <select v-model="code.tolerance">
                  <option value="">--</option>
                  <option v-for="t in toleranceOptions" :key="t.code" :value="t.code">
                    {{ t.code }} ({{ t.label }})
                  </option>
                </select>
              </div>
              <div class="form-field">
                <label>Tensión (código)</label>
                <select v-model="code.voltage">
                  <option value="">--</option>
                  <option v-for="v in voltageOptions" :key="v.code" :value="v.code">
                    {{ v.code }} ({{ v.voltage }}V)
                  </option>
                </select>
              </div>
            </div>

            <div class="form-actions">
              <button type="submit" class="btn-primary-action">
                Decodificar
              </button>
              <button type="button" class="btn-secondary-action" @click="resetCode">
                Limpiar
              </button>
            </div>
          </form>

          <div class="output-body">
            <div class="output-values">
              <div class="value-row">
                <span>pF</span>
                <strong>{{ codeValuePf }}</strong>
              </div>
              <div class="value-row">
                <span>nF</span>
                <strong>{{ codeValueNf }}</strong>
              </div>
              <div class="value-row">
                <span>µF</span>
                <strong>{{ codeValueUf }}</strong>
              </div>
              <div class="value-row">
                <span>Tolerancia</span>
                <strong>{{ codeToleranceLabel }}</strong>
              </div>
              <div class="value-row">
                <span>Tensión</span>
                <strong>{{ codeVoltageLabel }}</strong>
              </div>
            </div>
            <div class="output-hint">
              El código se interpreta en pF: dos dígitos + cantidad de ceros.
            </div>
          </div>
        </div>
      </div>

      <div class="cap-back">
        <Link url="/calculadoras">
          <span class="cap-back-link">← VOLVER A CALCULADORAS</span>
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
import { computed, reactive, ref } from 'vue'
import PageSection from '/src/vue/components/layout/PageSection.vue'
import PageSectionHeader from '/src/vue/components/layout/PageSectionHeader.vue'
import PageSectionContent from '/src/vue/components/layout/PageSectionContent.vue'
import Link from '/src/vue/components/generic/Link.vue'
import Footer from '/src/vue/components/footer/Footer.vue'
import FooterBlock from '/src/vue/components/footer/FooterBlock.vue'
import FooterColumn from '/src/vue/components/footer/FooterColumn.vue'
import FooterCopyright from '/src/vue/components/footer/FooterCopyright.vue'

const conversion = reactive({
  pf: null as number | null,
  nf: null as number | null,
  uf: null as number | null,
  f: null as number | null
})

const isUpdating = ref(false)

const roundValue = (value: number) => Number(value.toFixed(6))

const syncConversion = (basePf: number) => {
  conversion.pf = roundValue(basePf)
  conversion.nf = roundValue(basePf / 1_000)
  conversion.uf = roundValue(basePf / 1_000_000)
  conversion.f = roundValue(basePf / 1_000_000_000_000)
}

const onConversionInput = (field: 'pf' | 'nf' | 'uf' | 'f') => {
  if (isUpdating.value) return
  const value = conversion[field]
  if (!Number.isFinite(value)) {
    resetConversion()
    return
  }

  let basePf = value as number
  if (field === 'nf') basePf = (value as number) * 1_000
  if (field === 'uf') basePf = (value as number) * 1_000_000
  if (field === 'f') basePf = (value as number) * 1_000_000_000_000

  isUpdating.value = true
  syncConversion(basePf)
  isUpdating.value = false
}

const resetConversion = () => {
  conversion.pf = null
  conversion.nf = null
  conversion.uf = null
  conversion.f = null
}

const toleranceOptions = [
  { code: 'B', label: '±0.10 pF' },
  { code: 'C', label: '±0.25 pF' },
  { code: 'D', label: '±0.5 pF' },
  { code: 'E', label: '±0.5%' },
  { code: 'F', label: '±1%' },
  { code: 'G', label: '±2%' },
  { code: 'H', label: '±3%' },
  { code: 'J', label: '±5%' },
  { code: 'K', label: '±10%' },
  { code: 'M', label: '±20%' },
  { code: 'N', label: '±30%' },
  { code: 'P', label: '+100% -0%' },
  { code: 'Z', label: '+80% -20%' }
]

const voltageOptions = [
  { code: '0G', voltage: 4 },
  { code: '0L', voltage: 5.5 },
  { code: '0J', voltage: 6.3 },
  { code: '1A', voltage: 10 },
  { code: '1C', voltage: 16 },
  { code: '1E', voltage: 25 },
  { code: '1H', voltage: 50 },
  { code: '1J', voltage: 63 },
  { code: '1K', voltage: 80 },
  { code: '2A', voltage: 100 },
  { code: '2Q', voltage: 110 },
  { code: '2B', voltage: 125 },
  { code: '2C', voltage: 160 },
  { code: '2Z', voltage: 180 },
  { code: '2D', voltage: 200 },
  { code: '2P', voltage: 220 },
  { code: '2E', voltage: 250 },
  { code: '2F', voltage: 315 },
  { code: '2V', voltage: 350 },
  { code: '2G', voltage: 400 },
  { code: '2W', voltage: 450 },
  { code: '2H', voltage: 500 },
  { code: '2J', voltage: 630 },
  { code: '3A', voltage: 1000 }
]

const code = reactive({
  value: '',
  tolerance: '',
  voltage: ''
})

const decodedPf = computed(() => {
  const text = code.value.trim()
  if (!/^\d{3}$/.test(text)) return NaN
  const sig = Number(text.slice(0, 2))
  const mult = Math.pow(10, Number(text[2]))
  return sig * mult
})

const codeValuePf = computed(() => (Number.isFinite(decodedPf.value) ? `${decodedPf.value} pF` : '---'))
const codeValueNf = computed(() =>
  Number.isFinite(decodedPf.value) ? `${(decodedPf.value / 1_000).toFixed(3)} nF` : '---'
)
const codeValueUf = computed(() =>
  Number.isFinite(decodedPf.value) ? `${(decodedPf.value / 1_000_000).toFixed(6)} µF` : '---'
)

const codeToleranceLabel = computed(() => {
  if (!code.tolerance) return '---'
  const entry = toleranceOptions.find((t) => t.code === code.tolerance)
  return entry ? entry.label : '---'
})

const codeVoltageLabel = computed(() => {
  if (!code.voltage) return '---'
  const entry = voltageOptions.find((v) => v.code === code.voltage)
  return entry ? `${entry.voltage} V` : '---'
})

function onDecode() {
  return true
}

function resetCode() {
  code.value = ''
  code.tolerance = ''
  code.voltage = ''
}
</script>

<style scoped lang="scss">
@import "/src/scss/_theming.scss";

#smd-capacitor-calculator {
  :deep(.container-xxl) {
    max-width: 2000px;
    padding-left: 1.2rem;
    padding-right: 1.2rem;
  }

  .cap-layout {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 2.6rem;

    @include media-breakpoint-down(lg) {
      grid-template-columns: 1fr;
    }
  }

  .cap-panel {
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
    gap: 10rem;
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

  .form-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;

    @include media-breakpoint-down(sm) {
      grid-template-columns: 1fr;
    }
  }

  .form-grid-wide {
    grid-template-columns: 1fr;
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

  .form-field input,
  .form-field select {
    border: 1px solid rgba($dark, 0.2);
    border-radius: 12px;
    padding: 0.65rem 0.75rem;
    font-family: 'Cervo Neue', $font-family-base;
    font-size: 0.95rem;
    background: $light-1;
    color: $dark;
  }

  .unit-input {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 0.5rem;
    align-items: center;
  }

  .unit-tag {
    border: 1px solid rgba($dark, 0.15);
    border-radius: 12px;
    padding: 0.6rem 0.75rem;
    font-family: 'Cervo Neue', $font-family-base;
    font-size: 0.9rem;
    background: rgba($light-2, 0.7);
    color: $dark;
    min-width: 64px;
    text-align: center;
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
    margin-top: 1.2rem;
  }

  .output-values {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    font-family: 'Cervo Neue', $font-family-base;
    color: $dark;
  }

  .value-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.45rem 0.75rem;
    border-radius: 12px;
    background: rgba($dark, 0.04);
  }

  .value-row strong {
    font-weight: 800;
  }

  .output-hint {
    font-size: 0.85rem;
    color: $text-muted;
    max-width: 280px;
  }

  .cap-back {
    display: flex;
    justify-content: center;
    margin-top: 2.5rem;
  }

  .cap-visuals,
  .cap-visual-card,
  .cap-visual-half,
  .cap-visual-divider {
    display: none;
  }

  .cap-visual-inline {
    display: grid;
    place-items: center;
    gap: 0.4rem;
    margin-bottom: 1.1rem;
  }

  .cap-visual-inline img {
    max-width: 160px;
    width: 100%;
    height: auto;
    display: block;
  }

  .cap-visual-inline p {
    margin: 0;
    font-family: 'Cervo Neue', $headings-font-family;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: $dark;
  }

  .cap-back-link {
    font-family: 'Cervo Neue', $headings-font-family;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: $primary;
  }
}
</style>
