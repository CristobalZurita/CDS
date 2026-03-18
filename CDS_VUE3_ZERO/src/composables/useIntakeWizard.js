/**
 * useIntakeWizard
 * 
 * Composable maestro para el flujo de ingreso unificado:
 * Cliente → Device → Repair → IntakeSheet → Fotos → Materiales
 * 
 * Modo: Single scroll page con validación en tiempo real
 */

import { ref, computed, reactive } from 'vue'
import { extractErrorMessage } from '@/services/api'
import {
  applyExistingClientToForm,
  buildIntakeWizardValidationValues,
  createIntakeWizardFormState,
  createIntakeWizardMaterial,
  INTAKE_WIZARD_VALIDATION_CONFIG,
  resetIntakeWizardFormState
} from './intakeWizardFormState'
import {
  getNextClientCode,
  getNextOtCode,
  listExistingClients,
  searchInventoryProducts,
  submitIntakeWizard
} from '@/services/intakeWizardService'
import { useFormValidation } from './useFormValidation'

export function useIntakeWizard() {
  // Estados de UI
  const isLoading = ref(false)
  const isSubmitting = ref(false)
  const generalError = ref('')
  const activeSection = ref('client') // Para scroll spy
  
  const form = reactive(createIntakeWizardFormState())
  
  // Flags de modo
  const useExistingClient = ref(false)
  const existingClients = ref([])
  const nextClientCode = ref('')
  const nextOtCode = ref('')
  
  // Setup validación
  const validation = useFormValidation(INTAKE_WIZARD_VALIDATION_CONFIG)
  
  // Computed
  const isValid = computed(() => validation.isValid.value)
  const errors = computed(() => validation.errors.value)
  
  const canSubmit = computed(() => {
    return !isSubmitting.value && 
           !isLoading.value && 
           validation.isValid.value &&
           form.client.name &&
           form.device.model &&
           form.repair.problem_reported
  })
  
  const progress = computed(() => {
    const sections = ['client', 'device', 'repair', 'intake']
    const completed = sections.filter(section => {
      switch(section) {
        case 'client': return !!form.client.name && !!form.client.email
        case 'device': return !!form.device.brand_other && !!form.device.model
        case 'repair': return !!form.repair.problem_reported
        case 'intake': return !!form.intake.equipment_name
        default: return false
      }
    }).length
    return Math.round((completed / sections.length) * 100)
  })
  
  // ==================== API CALLS ====================
  
  /**
   * Cargar clientes existentes
   */
  async function loadExistingClients() {
    existingClients.value = await listExistingClients()
  }
  
  /**
   * Obtener siguiente código de cliente
   */
  async function fetchNextClientCode() {
    nextClientCode.value = await getNextClientCode()
  }
  
  /**
   * Obtener siguiente código de OT
   */
  async function fetchNextOtCode(clientId = null) {
    nextOtCode.value = await getNextOtCode(clientId)
  }
  
  /**
   * Seleccionar cliente existente
   */
  function selectExistingClient(clientId) {
    const client = existingClients.value.find(c => c.id === clientId)
    if (!client) return

    applyExistingClientToForm(form, client)

    // Actualizar código OT basado en cliente
    fetchNextOtCode(client.id)
  }
  
  /**
   * Agregar material
   */
  function addMaterial() {
    form.materials.push(createIntakeWizardMaterial())
  }
  
  /**
   * Quitar material
   */
  function removeMaterial(index) {
    form.materials.splice(index, 1)
  }
  
  /**
   * Buscar producto por SKU
   */
  async function searchProduct(query, materialIndex) {
    return searchInventoryProducts(query)
  }
  
  // ==================== SUBMIT ====================
  
  /**
   * Submit del formulario completo
   */
  async function submit() {
    // Validar todo
    const values = buildIntakeWizardValidationValues(form)

    const validationResult = validation.validateAll(values)
    if (!validationResult.valid) {
      generalError.value = 'Por favor completa todos los campos obligatorios'
      scrollToFirstError()
      return { success: false, error: 'validation' }
    }
    
    isSubmitting.value = true
    generalError.value = ''
    
    try {
      const { clientId, deviceId, repairId } = await submitIntakeWizard(form, {
        useExistingClient: useExistingClient.value
      })

      // Éxito
      return { 
        success: true, 
        data: { 
          clientId, 
          deviceId, 
          repairId,
          clientCode: nextClientCode.value,
          otCode: nextOtCode.value
        } 
      }
      
    } catch (err) {
      const message = extractErrorMessage(err)
      generalError.value = message
      return { success: false, error: message }
    } finally {
      isSubmitting.value = false
    }
  }
  
  /**
   * Scroll al primer error
   */
  function scrollToFirstError() {
    setTimeout(() => {
      const firstError = document.querySelector('.is-invalid, .has-error')
      if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' })
        firstError.focus()
      }
    }, 100)
  }
  
  /**
   * Resetear formulario
   */
  function reset() {
    resetIntakeWizardFormState(form)

    useExistingClient.value = false
    generalError.value = ''
    validation.reset()
    
    fetchNextClientCode()
    fetchNextOtCode()
  }
  
  // Inicialización
  loadExistingClients()
  fetchNextClientCode()
  fetchNextOtCode()
  
  return {
    // Estado
    form,
    isLoading,
    isSubmitting,
    generalError,
    activeSection,
    useExistingClient,
    existingClients,
    nextClientCode,
    nextOtCode,
    
    // Validación
    validation,
    isValid,
    errors,
    canSubmit,
    progress,
    
    // Acciones
    loadExistingClients,
    fetchNextClientCode,
    fetchNextOtCode,
    selectExistingClient,
    addMaterial,
    removeMaterial,
    searchProduct,
    submit,
    reset,
    scrollToFirstError
  }
}

export default useIntakeWizard
