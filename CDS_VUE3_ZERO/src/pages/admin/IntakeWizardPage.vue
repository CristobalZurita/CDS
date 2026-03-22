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
        @validate-field="validateField"
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
  </main>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
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
  reset
} = useIntakeWizard()

const { initAutocomplete } = usePlacesAutocomplete()
const addressFieldRef = ref(null)
let _cleanupAddressAc = () => {}

// Estado local
const selectedClientId = ref('')
const activeSection = ref('cliente')
const showResetDialog = ref(false)

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
    // Redirigir a la OT creada
    router.push({
      name: 'admin-repair-detail',
      params: { id: result.data.repairId }
    })
  }
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
</style>
