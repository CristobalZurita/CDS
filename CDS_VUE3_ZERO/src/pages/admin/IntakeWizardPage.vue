<template>
  <main class="intake-wizard-page">
    <IntakeWizardSectionNav
      :sections="sections"
      :active-section="activeSection"
      :progress="progress"
      :next-client-code="nextClientCode"
      :next-ot-code="nextOtCode"
      @navigate="scrollToSection"
    />

    <IntakeWizardErrorBanner
      :message="generalError"
      @close="generalError = ''"
    />

    <!-- Formulario scroll único -->
    <form class="wizard-form" @submit.prevent="handleSubmit" @focusin="onFocusIn">
      <IntakeWizardClientSection
        v-model:use-existing-client="useExistingClient"
        v-model:selected-client-id="selectedClientId"
        :client="form.client"
        :errors="errors"
        :client-options="clientOptions"
        :address-field-ref="setAddressFieldRef"
        @validate-field="validateField"
        @select-client="onClientSelect"
      />

      <IntakeWizardDeviceSection
        :device="form.device"
        :errors="errors"
        @validate-field="validateField"
      />

      <IntakeWizardRepairSection
        :repair="form.repair"
        :errors="errors"
        :device-brand="form.device.brand"
        :device-model="form.device.model"
        :ai-loading="aiLoading"
        :ai-error="aiError"
        :ai-suggestion="aiSuggestion"
        @validate-field="validateField"
        @consultar-ia="consultarIA"
        @clear-ai="clearAI"
        @set-cobro="(v) => { form.repair.paid_amount = v }"
      />

      <IntakeWizardOperationsSection
        :intake="form.intake"
        :errors="errors"
        @validate-field="validateField"
      />

      <IntakeWizardMaterialsSection
        :materials="form.materials"
        @add-material="addMaterial"
        @remove-material="removeMaterial"
      />

      <IntakeWizardFormActions
        :is-submitting="isSubmitting"
        :can-submit="canSubmit"
        @reset="resetForm"
      />
    </form>

    <BaseConfirmDialog
      :open="showResetDialog"
      title="Limpiar formulario"
      message="¿Estás seguro de limpiar todo el formulario?"
      confirm-label="Limpiar todo"
      confirm-variant="warning"
      @cancel="showResetDialog = false"
      @confirm="confirmReset"
    />

    <!-- Modal T&C + firma de ingreso -->
    <div v-if="showActivateModal" class="tc-overlay" role="dialog" aria-modal="true" aria-labelledby="tc-title">
      <div class="tc-modal">
        <h2 id="tc-title" class="tc-title">Orden de Trabajo — Términos de ingreso</h2>
        <div class="tc-body">
          <p>El cliente declara que el equipo es de su propiedad y autoriza al taller a realizar el diagnóstico y las reparaciones acordadas. El costo final se confirma tras la revisión. El taller no se responsabiliza por daños preexistentes no informados ni por equipos no retirados en 90 días.</p>
          <p>Al firmar, el cliente acepta estos términos y condiciones de servicio.</p>
        </div>
        <div class="tc-canvas-wrap">
          <p class="tc-canvas-label"><i class="fas fa-signature"></i> Firma del cliente (opcional)</p>
          <canvas
            ref="signatureCanvas"
            class="tc-canvas"
            width="480"
            height="160"
            @pointerdown="startDraw"
            @pointermove="draw"
            @pointerup="endDraw"
            @pointerleave="endDraw"
          ></canvas>
          <button type="button" class="tc-clear-btn" @click="clearSignature">Borrar firma</button>
        </div>
        <div class="tc-actions">
          <button type="button" class="btn-secondary" :disabled="isActivating" @click="skipActivate">
            Omitir firma
          </button>
          <button type="button" class="btn-primary" :disabled="isActivating" @click="confirmActivate">
            <span v-if="isActivating"><span class="spinner spinner--sm"></span> Activando…</span>
            <span v-else><i class="fas fa-check"></i> Activar OT</span>
          </button>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { activateRepairById } from '@/services/repairDetailAdminService'
import IntakeWizardErrorBanner from '@/components/admin/IntakeWizardErrorBanner.vue'
import IntakeWizardFormActions from '@/components/admin/IntakeWizardFormActions.vue'
import IntakeWizardClientSection from '@/components/admin/IntakeWizardClientSection.vue'
import IntakeWizardDeviceSection from '@/components/admin/IntakeWizardDeviceSection.vue'
import IntakeWizardMaterialsSection from '@/components/admin/IntakeWizardMaterialsSection.vue'
import IntakeWizardOperationsSection from '@/components/admin/IntakeWizardOperationsSection.vue'
import IntakeWizardRepairSection from '@/components/admin/IntakeWizardRepairSection.vue'
import IntakeWizardSectionNav from '@/components/admin/IntakeWizardSectionNav.vue'
import { useIntakeWizard } from '@/composables/useIntakeWizard'
import { usePlacesAutocomplete } from '@/composables/usePlacesAutocomplete'
import { BaseConfirmDialog } from '@/components/base'

const router = useRouter()

// Usar el composable maestro
const {
  form,
  isSubmitting,
  generalError,
  useExistingClient,
  existingClients,
  nextClientCode,
  nextOtCode,
  progress,
  validation,
  canSubmit,
  selectExistingClient,
  addMaterial,
  removeMaterial,
  submit,
  reset,
  aiLoading,
  aiError,
  aiSuggestion,
  consultarIA,
  clearAI
} = useIntakeWizard()

const { initAutocomplete } = usePlacesAutocomplete()
const addressFieldRef = ref(null)
let _cleanupAddressAc = () => {}

// Estado local
const selectedClientId = ref('')
const activeSection = ref('cliente')
const showResetDialog = ref(false)

// Estado modal T&C / firma
const showActivateModal = ref(false)
const pendingRepairId = ref(null)
const isActivating = ref(false)
const signatureCanvas = ref(null)
let _drawing = false

const errors = computed(() => validation.errors.value)

// Opciones para selector de clientes
const clientOptions = computed(() => {
  return existingClients.value.map(c => ({
    value: c.id,
    label: `${c.client_code || `#${c.id}`} - ${c.name}`
  }))
})

// Secciones para navegación
const sections = [
  { id: 'cliente', label: 'Cliente' },
  { id: 'equipo', label: 'Equipo' },
  { id: 'ot', label: 'OT' },
  { id: 'operaciones', label: 'Planificación' },
  { id: 'materiales', label: 'Materiales' }
]

// Métodos
function validateField(field, value) {
  validation.validateField(field, value)
}

function onClientSelect(clientId) {
  if (clientId) {
    selectExistingClient(clientId)
  }
}

function setAddressFieldRef(element) {
  addressFieldRef.value = element
}

async function handleSubmit() {
  const result = await submit()

  if (result.success) {
    pendingRepairId.value = result.data.repairId
    showActivateModal.value = true
  }
}

// ── Firma sobre canvas ──────────────────────────────────────────────
function _getCanvasPos(e) {
  const rect = signatureCanvas.value.getBoundingClientRect()
  const scaleX = signatureCanvas.value.width / rect.width
  const scaleY = signatureCanvas.value.height / rect.height
  return {
    x: (e.clientX - rect.left) * scaleX,
    y: (e.clientY - rect.top) * scaleY,
  }
}

function startDraw(e) {
  e.preventDefault()
  _drawing = true
  const ctx = signatureCanvas.value.getContext('2d')
  const { x, y } = _getCanvasPos(e)
  ctx.beginPath()
  ctx.moveTo(x, y)
  signatureCanvas.value.setPointerCapture(e.pointerId)
}

function draw(e) {
  if (!_drawing) return
  e.preventDefault()
  const ctx = signatureCanvas.value.getContext('2d')
  ctx.strokeStyle = '#3e3c38'
  ctx.lineWidth = 2
  ctx.lineCap = 'round'
  const { x, y } = _getCanvasPos(e)
  ctx.lineTo(x, y)
  ctx.stroke()
}

function endDraw() {
  _drawing = false
}

function clearSignature() {
  const canvas = signatureCanvas.value
  if (canvas) {
    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
  }
}

function _canvasIsBlank() {
  if (!signatureCanvas.value) return true
  const ctx = signatureCanvas.value.getContext('2d')
  const data = ctx.getImageData(0, 0, signatureCanvas.value.width, signatureCanvas.value.height).data
  return !data.some(v => v !== 0)
}

async function confirmActivate() {
  isActivating.value = true
  const signatureData = _canvasIsBlank() ? null : signatureCanvas.value.toDataURL('image/png')
  try {
    await activateRepairById(pendingRepairId.value, {
      signatureData,
      termsAccepted: true,
    })
  } catch {
    // Best-effort — activate no bloquea el flujo
  } finally {
    isActivating.value = false
    showActivateModal.value = false
    router.push({ name: 'admin-repair-detail', params: { id: pendingRepairId.value } })
  }
}

function skipActivate() {
  showActivateModal.value = false
  router.push({ name: 'admin-repair-detail', params: { id: pendingRepairId.value } })
}

function resetForm() {
  showResetDialog.value = true
}

function confirmReset() {
  reset()
  selectedClientId.value = ''
  showResetDialog.value = false
}

function scrollToSection(sectionId) {
  const element = document.getElementById(sectionId)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    activeSection.value = sectionId
  }
}

// Centrar viewport en el campo enfocado al navegar con Tab
function onFocusIn(e) {
  const target = e.target
  if (!target || !['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName)) return
  target.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' })
}

// Scroll spy
onMounted(async () => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          activeSection.value = entry.target.id
        }
      })
    },
    { rootMargin: '-20% 0px -80% 0px' }
  )

  sections.forEach(section => {
    const element = document.getElementById(section.id)
    if (element) observer.observe(element)
  })

  // Google Places Autocomplete on address field
  const inputEl = addressFieldRef.value?.$el?.querySelector('input')
  if (inputEl) {
    _cleanupAddressAc = await initAutocomplete(inputEl, ({ address, city, region, country }) => {
      form.client.address = address
      if (city)    form.client.city    = city
      if (region)  form.client.region  = region
      if (country) form.client.country = country
    })
  }
})

onUnmounted(() => _cleanupAddressAc())
</script>

<style scoped>
.intake-wizard-page {
  --intake-page-padding: 0px;
  --intake-page-padding-mobile: 0px;
  --intake-page-padding-bottom: 4rem;
  --intake-page-max-width: 100%;
  --intake-form-gap: var(--cds-space-xl);
  --intake-section-padding: var(--cds-space-lg);
  --intake-section-scroll-margin-top: 56px;
  --intake-section-header-margin-bottom: var(--cds-space-lg);
  --intake-section-header-padding-bottom: 0.75rem;
  --intake-subsection-offset: var(--cds-space-lg);
  --intake-field-gap: var(--cds-space-md);
  --intake-field-margin-bottom: var(--cds-space-md);
  --intake-toggle-gap: 0.5rem;
  --intake-header-padding: 1.25rem;
  --intake-header-margin-bottom: var(--cds-space-lg);
  --intake-header-gap: var(--cds-space-md);
  --intake-progress-gap: 0.75rem;
  --intake-code-box-padding-block: 0.5rem;
  --intake-code-box-padding-inline: var(--cds-space-md);
  --intake-error-gap: 0.75rem;
  --intake-error-padding: var(--cds-space-md);
  --intake-error-margin-bottom: var(--cds-space-md);
  --intake-form-actions-gap: var(--cds-space-md);
  --intake-form-actions-padding: var(--cds-space-md);
  --intake-form-actions-offset: -1rem;
  --intake-material-item-gap: 0.75rem;
  --intake-material-item-padding: var(--cds-space-md);
  --intake-empty-padding: var(--cds-space-xl);
  --intake-nav-offset-inline: var(--cds-space-xl);
  --intake-nav-padding: 0.5rem;
  --intake-nav-link-pad-block: 0.5rem;
  --intake-nav-link-pad-inline: 0.75rem;
  padding: var(--intake-page-padding, 1rem);
  padding-bottom: var(--intake-page-padding-bottom, 4rem);
}

/* Formulario */
.wizard-form {
  display: flex;
  flex-direction: column;
  gap: var(--intake-form-gap, 2rem);
  padding-top: var(--cds-space-md, 1rem);
}

/* Responsive */
@media (max-width: 768px) {
  .intake-wizard-page {
    padding: var(--intake-page-padding-mobile, 0.5rem);
  }
}

/* ── Modal T&C / Firma ─────────────────────────────────────────── */
.tc-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9000;
  padding: 1rem;
}

.tc-modal {
  background: var(--cds-surface-1);
  border-radius: var(--cds-radius-md);
  padding: 1.5rem;
  width: 100%;
  max-width: 560px;
  display: grid;
  gap: 1.25rem;
  box-shadow: var(--cds-shadow-lg);
}

.tc-title {
  font-size: var(--cds-text-lg);
  font-weight: 700;
  color: var(--cds-text-heading);
  margin: 0;
}

.tc-body {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  line-height: 1.6;
  display: grid;
  gap: 0.5rem;
}

.tc-body p { margin: 0; }

.tc-canvas-wrap {
  display: grid;
  gap: 0.5rem;
}

.tc-canvas-label {
  font-size: var(--cds-text-xs);
  font-weight: 600;
  color: var(--cds-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.tc-canvas {
  width: 100%;
  height: 120px;
  border: 1.5px solid var(--cds-border-input);
  border-radius: var(--cds-radius-sm);
  background: var(--cds-white, #fff);
  touch-action: none;
  cursor: crosshair;
}

.tc-clear-btn {
  align-self: start;
  background: none;
  border: none;
  padding: 0;
  font-size: var(--cds-text-xs);
  color: var(--cds-text-muted);
  cursor: pointer;
  text-decoration: underline;
}

.tc-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  flex-wrap: wrap;
}
</style>
