<template>
  <main class="intake-wizard-page">
    <IntakeWizardHeader
      :next-client-code="nextClientCode"
      :next-ot-code="nextOtCode"
      :progress="progress"
    />

    <!-- Error general -->
    <div v-if="generalError" class="error-banner" role="alert">
      <span class="error-icon">⚠️</span>
      <span>{{ generalError }}</span>
      <button class="error-close" @click="generalError = ''">×</button>
    </div>

    <!-- Formulario scroll único -->
    <form class="wizard-form" @submit.prevent="handleSubmit">
      
      <!-- SECCIÓN 1: CLIENTE -->
      <section id="cliente" class="form-section">
        <div class="section-header">
          <h2>1. Datos del Cliente</h2>
          <label class="toggle-existing">
            <input 
              v-model="useExistingClient" 
              type="checkbox"
            />
            <span>Cliente existente</span>
          </label>
        </div>

        <!-- Selector cliente existente -->
        <div v-if="useExistingClient" class="field-group">
          <FormField
            v-model="selectedClientId"
            type="select"
            label="Seleccionar cliente"
            :options="clientOptions"
            placeholder="Selecciona..."
            @change="onClientSelect"
          />
        </div>

        <!-- Campos cliente -->
        <div class="field-grid cols-2">
          <FormField
            v-model="form.client.name"
            label="Nombre completo"
            placeholder="Ej: Juan Pérez"
            :error="errors['client.name']"
            required
            @blur="validateField('client.name', form.client.name)"
          />
          
          <FormField
            v-model="form.client.email"
            type="email"
            label="Email"
            placeholder="ejemplo@correo.com"
            :error="errors['client.email']"
            required
            @blur="validateField('client.email', form.client.email)"
          />
          
          <FormField
            v-model="form.client.phone"
            type="tel"
            label="Teléfono / WhatsApp"
            placeholder="+56912345678"
            :error="errors['client.phone']"
            required
            @blur="validateField('client.phone', form.client.phone)"
          />
          
          <FormField
            v-model="form.client.phone_alt"
            type="tel"
            label="Teléfono alternativo (opcional)"
            placeholder="+56987654321"
          />
          
          <FormField
            ref="addressFieldRef"
            v-model="form.client.address"
            label="Dirección"
            placeholder="Calle, número, depto"
            :error="errors['client.address']"
            required
            @blur="validateField('client.address', form.client.address)"
          />
          
          <FormField
            v-model="form.client.city"
            label="Ciudad"
            placeholder="Ej: Santiago"
            :error="errors['client.city']"
            required
            @blur="validateField('client.city', form.client.city)"
          />
          
          <FormField
            v-model="form.client.region"
            label="Región"
            placeholder="Ej: Metropolitana"
            :error="errors['client.region']"
            required
            @blur="validateField('client.region', form.client.region)"
          />
          
          <FormField
            v-model="form.client.country"
            label="País"
            placeholder="Chile"
            disabled
          />
        </div>

        <!-- Datos de facturación -->
        <div class="subsection">
          <h3>Datos de facturación (opcional)</h3>
          <div class="field-grid cols-3">
            <FormField
              v-model="form.client.tax_id"
              label="RUT"
              placeholder="12.345.678-9"
              :error="errors['client.tax_id']"
              @blur="validateField('client.tax_id', form.client.tax_id)"
            />
            
            <FormField
              v-model="form.client.company_name"
              label="Razón social"
              placeholder="Empresa SPA"
            />
            
            <FormField
              v-model="form.client.billing_address"
              label="Dirección de facturación"
              placeholder="Si es diferente"
            />
          </div>
        </div>

        <!-- Notas -->
        <div class="field-group">
          <FormField
            v-model="form.client.notes"
            type="textarea"
            label="Notas del cliente"
            placeholder="Información adicional..."
            :rows="2"
          />
        </div>
      </section>

      <!-- SECCIÓN 2: EQUIPO -->
      <section id="equipo" class="form-section">
        <div class="section-header">
          <h2>2. Datos del Equipo</h2>
        </div>

        <div class="field-grid cols-2">
          <FormField
            v-model="form.device.brand_other"
            label="Marca"
            placeholder="Ej: Korg, Roland, Yamaha"
            :error="errors['device.brand_other']"
            required
            @blur="validateField('device.brand_other', form.device.brand_other)"
          />
          
          <FormField
            v-model="form.device.model"
            label="Modelo"
            placeholder="Ej: MS-20, Juno-106"
            :error="errors['device.model']"
            required
            @blur="validateField('device.model', form.device.model)"
          />
          
          <FormField
            v-model="form.device.serial_number"
            label="Número de serie"
            placeholder="SN123456789"
          />
          
          <FormField
            v-model="form.device.year_manufactured"
            type="number"
            label="Año de fabricación"
            placeholder="2020"
            :min="1950"
            :max="2030"
          />
          
          <FormField
            v-model="form.device.accessories"
            label="Accesorios entregados"
            placeholder="Cable, manual, fuente..."
          />
        </div>

        <div class="field-group">
          <FormField
            v-model="form.device.condition_notes"
            type="textarea"
            label="Estado físico del equipo"
            placeholder="Describa el estado: rayones, golpes, piezas faltantes..."
            :error="errors['device.condition_notes']"
            required
            :rows="3"
            @blur="validateField('device.condition_notes', form.device.condition_notes)"
          />
        </div>

        <div class="field-group">
          <FormField
            v-model="form.device.description"
            type="textarea"
            label="Descripción adicional (opcional)"
            placeholder="Modificaciones, historia, etc."
            :rows="2"
          />
        </div>

        <!-- Fotos del equipo -->
        <div class="subsection">
          <h3>Fotos del equipo</h3>
          <PhotoUpload
            v-model="form.device.photos"
            :max="5"
            description="Fotos del estado inicial del equipo"
          />
        </div>
      </section>

      <!-- SECCIÓN 3: ORDEN DE TRABAJO -->
      <section id="ot" class="form-section">
        <div class="section-header">
          <h2>3. Orden de Trabajo</h2>
        </div>

        <div class="field-group">
          <FormField
            v-model="form.repair.problem_reported"
            type="textarea"
            label="Problema reportado"
            placeholder="Describa detalladamente el problema que presenta el equipo..."
            :error="errors['repair.problem_reported']"
            required
            :rows="4"
            @blur="validateField('repair.problem_reported', form.repair.problem_reported)"
          />
        </div>

        <div class="field-group">
          <FormField
            v-model="form.repair.diagnosis"
            type="textarea"
            label="Diagnóstico inicial (opcional)"
            placeholder="Si ya tiene una idea del problema..."
            :rows="3"
          />
        </div>

        <div class="field-grid cols-3">
          <FormField
            v-model="form.repair.priority"
            type="select"
            label="Prioridad"
            :options="[
              { value: 1, label: 'Alta' },
              { value: 2, label: 'Normal' },
              { value: 3, label: 'Baja' }
            ]"
            required
          />
          
          <FormField
            v-model="form.repair.paid_amount"
            type="number"
            label="Abono (CLP)"
            :min="0"
            :step="1000"
            :error="errors['repair.paid_amount']"
            required
          />
          
          <FormField
            v-model="form.repair.payment_method"
            type="select"
            label="Método de pago"
            :options="[
              { value: 'cash', label: 'Efectivo' },
              { value: 'transfer', label: 'Transferencia' },
              { value: 'web', label: 'Web' }
            ]"
            required
          />
        </div>

        <div class="field-group">
          <FormField
            v-model="form.repair.warranty_days"
            type="number"
            label="Días de garantía"
            :min="0"
            :max="365"
          />
        </div>
      </section>

      <!-- SECCIÓN 4: PLANILLA DE OPERACIONES -->
      <section id="operaciones" class="form-section">
        <div class="section-header">
          <h2>4. Planilla de Operaciones y Mantenimiento</h2>
        </div>

        <div class="field-grid cols-2">
          <FormField
            v-model="form.intake.equipment_name"
            label="Nombre del dispositivo"
            placeholder="Nombre técnico del equipo"
            :error="errors['intake.equipment_name']"
            required
            @blur="validateField('intake.equipment_name', form.intake.equipment_name)"
          />
          
          <FormField
            v-model="form.intake.equipment_model"
            label="Modelo del dispositivo"
            placeholder="Si difiere del modelo comercial"
          />
          
          <FormField
            v-model="form.intake.equipment_type"
            type="select"
            label="Tipo de equipo"
            :options="[
              { value: 'general', label: 'Equipo general' },
              { value: 'precision', label: 'Equipo de precisión' }
            ]"
          />
          
          <FormField
            v-model="form.intake.requested_service_type"
            type="select"
            label="Tipo de servicio"
            :options="[
              { value: 'emergency', label: 'Reparación de emergencia' },
              { value: 'maintenance', label: 'Mantenimiento general' }
            ]"
          />
        </div>

        <div class="field-group">
          <FormField
            v-model="form.intake.failure_cause"
            type="textarea"
            label="Causa del problema"
            placeholder="Descripción técnica de la causa del fallo..."
            :error="errors['intake.failure_cause']"
            required
            :rows="3"
            @blur="validateField('intake.failure_cause', form.intake.failure_cause)"
          />
        </div>

        <div class="field-grid cols-3">
          <FormField
            v-model="form.intake.estimated_repair_time"
            label="Tiempo estimado"
            placeholder="Ej: 7 días hábiles"
          />
          
          <FormField
            v-model="form.intake.estimated_completion_date"
            type="date"
            label="Fecha estimada de término"
          />
          
          <FormField
            v-model="form.intake.tabulator_name"
            label="Nombre del tabulador"
            placeholder="Quien llena esta planilla"
          />
        </div>

        <!-- Firmas (simplificadas - solo nombres) -->
        <div class="subsection">
          <h3>Firmas y aprobaciones</h3>
          <div class="field-grid cols-2">
            <FormField
              v-model="form.intake.operation_department_signed_by"
              label="Departamento de Operaciones"
              placeholder="Nombre y firma"
            />
            
            <FormField
              v-model="form.intake.finance_department_signed_by"
              label="Departamento de Finanzas"
              placeholder="Nombre y firma"
            />
            
            <FormField
              v-model="form.intake.factory_director_signed_by"
              label="Director de Fábrica"
              placeholder="Nombre y firma"
            />
            
            <FormField
              v-model="form.intake.general_manager_signed_by"
              label="Gerente General"
              placeholder="Nombre y firma"
            />
          </div>
        </div>

        <div class="field-group">
          <FormField
            v-model="form.intake.annotations"
            type="textarea"
            label="Anotaciones operativas"
            placeholder="Observaciones adicionales..."
            :rows="3"
          />
        </div>
      </section>

      <IntakeWizardMaterialsSection
        :materials="form.materials"
        @add-material="addMaterial"
        @remove-material="removeMaterial"
      />

      <!-- Acciones finales -->
      <div class="form-actions">
        <BaseButton
          type="button"
          variant="ghost"
          :disabled="isSubmitting"
          @click="resetForm"
        >
          Limpiar todo
        </BaseButton>
        
        <BaseButton
          type="submit"
          variant="primary"
          size="lg"
          :loading="isSubmitting"
          :disabled="!canSubmit"
        >
          {{ isSubmitting ? 'Creando OT...' : 'Crear Orden de Trabajo' }}
        </BaseButton>
      </div>
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
import IntakeWizardHeader from '@/components/admin/IntakeWizardHeader.vue'
import IntakeWizardMaterialsSection from '@/components/admin/IntakeWizardMaterialsSection.vue'
import IntakeWizardSectionNav from '@/components/admin/IntakeWizardSectionNav.vue'
import { useIntakeWizard } from '@/composables/useIntakeWizard'
import { usePlacesAutocomplete } from '@/composables/usePlacesAutocomplete'
import { FormField } from '@/components/composite'
import { BaseButton, BaseConfirmDialog } from '@/components/base'
import PhotoUpload from '@/components/business/PhotoUpload.vue'

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

/* Error banner */
.error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  margin-bottom: 1rem;
  background: var(--cds-invalid-bg);
  border: 1px solid var(--cds-invalid-border);
  border-radius: var(--cds-radius-md);
  color: var(--cds-invalid-text);
}

.error-close {
  margin-left: auto;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0 0.25rem;
}

/* Formulario */
.wizard-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Secciones */
.form-section {
  background: var(--cds-white);
  border-radius: var(--cds-radius-lg);
  padding: 1.5rem;
  box-shadow: var(--cds-shadow-sm);
  scroll-margin-top: 120px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid var(--cds-light-2);
}

.section-header h2 {
  margin: 0;
  font-size: var(--cds-text-lg);
  color: var(--cds-text-normal);
}

.toggle-existing {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--cds-text-sm);
  cursor: pointer;
}

.subsection {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--cds-light-2);
}

.subsection h3 {
  margin: 0 0 1rem;
  font-size: var(--cds-text-base);
  color: var(--cds-text-muted);
}

/* Grids */
.field-grid {
  display: grid;
  gap: 1rem;
  margin-bottom: 1rem;
}

.field-grid.cols-2 {
  grid-template-columns: repeat(2, 1fr);
}

.field-grid.cols-3 {
  grid-template-columns: repeat(3, 1fr);
}

.field-group {
  margin-bottom: 1rem;
}

/* Acciones */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 2px solid var(--cds-light-2);
  position: sticky;
  bottom: 0;
  background: var(--cds-surface-1);
  backdrop-filter: blur(8px);
  padding: 1rem;
  margin: 0 -1rem -1rem;
  border-radius: var(--cds-radius-lg) var(--cds-radius-lg) 0 0;
}

/* Responsive */
@media (max-width: 768px) {
  .intake-wizard-page {
    padding: 0.5rem;
  }
  
  .field-grid.cols-2,
  .field-grid.cols-3 {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }
  
  .form-actions :deep(.base-button) {
    width: 100%;
  }
}
</style>
