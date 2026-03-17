<template>
  <main class="intake-wizard-page">
    <IntakeWizardHeader
      :next-client-code="nextClientCode"
      :next-ot-code="nextOtCode"
      :progress="progress"
    />

    <IntakeWizardErrorBanner
      :message="generalError"
      @close="generalError = ''"
    />

    <!-- Formulario scroll único -->
    <form class="wizard-form" @submit.prevent="handleSubmit">
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

    <IntakeWizardSectionNav
      :sections="sections"
      :active-section="activeSection"
      @navigate="scrollToSection"
    />

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
import IntakeWizardHeader from '@/components/admin/IntakeWizardHeader.vue'
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
  { id: 'operaciones', label: 'Operaciones' },
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
  padding: 1rem;
  padding-bottom: 4rem;
  max-width: 900px;
  margin: 0 auto;
}

/* Formulario */
.wizard-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Responsive */
@media (max-width: 768px) {
  .intake-wizard-page {
    padding: 0.5rem;
  }
}
</style>
