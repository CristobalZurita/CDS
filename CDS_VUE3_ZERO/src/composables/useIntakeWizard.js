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
import { useIntakeAI } from './useIntakeAI'
import {
  applyExistingClientToForm,
  buildIntakeWizardValidationValues,
  createIntakeWizardFormState,
  createIntakeWizardMaterial,
  INTAKE_WIZARD_VALIDATION_CONFIG,
  resolveIntakeWizardCanSubmit,
  resolveIntakeWizardProgress,
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

  // IA para asistencia en ingreso
  const { aiLoading, aiError, aiSuggestion, consultarIA, clearAI } = useIntakeAI()

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
  
  const canSubmit = computed(() => resolveIntakeWizardCanSubmit({
    isSubmitting: isSubmitting.value,
    isLoading: isLoading.value,
    isValid: validation.isValid.value,
    form
  }))
  
  const progress = computed(() => resolveIntakeWizardProgress(form))
  
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
    
    // IA
    aiLoading,
    aiError,
    aiSuggestion,
    consultarIA,
    clearAI,

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
