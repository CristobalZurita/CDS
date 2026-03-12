/**
 * useIntakeWizard
 * 
 * Composable maestro para el flujo de ingreso unificado:
 * Cliente → Device → Repair → IntakeSheet → Fotos → Materiales
 * 
 * Modo: Single scroll page con validación en tiempo real
 */

import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api, { extractErrorMessage } from '@/services/api'
import { uploadImage } from '@/services/uploadService'
import { useFormValidation } from './useFormValidation'

// Configuración de validación por campo
const VALIDATION_CONFIG = {
  // Cliente
  'client.name': {
    required: true,
    minLength: 2,
    maxLength: 100,
    message: 'Nombre es obligatorio (2-100 caracteres)'
  },
  'client.email': {
    required: true,
    email: true,
    message: 'Email válido es obligatorio'
  },
  'client.phone': {
    required: true,
    phone: true,
    message: 'Teléfono chileno válido es obligatorio'
  },
  'client.address': {
    required: true,
    minLength: 5,
    message: 'Dirección es obligatoria'
  },
  'client.city': {
    required: true,
    message: 'Ciudad es obligatoria'
  },
  'client.region': {
    required: true,
    message: 'Región es obligatoria'
  },
  'client.tax_id': {
    rut: true,
    message: 'RUT inválido'
  },
  
  // Device
  'device.brand_other': {
    required: true,
    message: 'Marca es obligatoria'
  },
  'device.model': {
    required: true,
    message: 'Modelo es obligatorio'
  },
  'device.serial_number': {
    required: false
  },
  'device.condition_notes': {
    required: true,
    message: 'Describa el estado físico'
  },
  
  // Repair
  'repair.problem_reported': {
    required: true,
    minLength: 10,
    message: 'Describa el problema (mínimo 10 caracteres)'
  },
  'repair.priority': {
    required: true
  },
  'repair.paid_amount': {
    required: true,
    min: 0,
    numbersOnly: true,
    message: 'Monto de abono inválido'
  },
  
  // Intake Sheet
  'intake.equipment_name': {
    required: true,
    message: 'Nombre del equipo es obligatorio'
  },
  'intake.failure_cause': {
    required: true,
    message: 'Causa del problema es obligatoria'
  }
}

export function useIntakeWizard() {
  const router = useRouter()
  
  // Estados de UI
  const isLoading = ref(false)
  const isSubmitting = ref(false)
  const generalError = ref('')
  const activeSection = ref('client') // Para scroll spy
  
  // Datos del formulario (estructura anidada)
  const form = reactive({
    // Cliente
    client: {
      id: null, // Si es cliente existente
      name: '',
      email: '',
      phone: '',
      phone_alt: '',
      address: '',
      city: '',
      region: '',
      country: 'Chile',
      tax_id: '',
      company_name: '',
      billing_address: '',
      customer_segment: 'regular',
      language_preference: 'es',
      service_preference: 'whatsapp',
      notes: '',
      internal_notes: ''
    },
    
    // Device (instrumento)
    device: {
      brand_other: '',
      model: '',
      serial_number: '',
      year_manufactured: null,
      description: '',
      condition_notes: '',
      accessories: '',
      photos: []
    },
    
    // Repair (OT)
    repair: {
      problem_reported: '',
      diagnosis: '',
      priority: 2, // 1=Alta, 2=Normal, 3=Baja
      paid_amount: 20000,
      payment_method: 'cash',
      warranty_days: 90
    },
    
    // Intake Sheet (planilla operaciones)
    intake: {
      equipment_name: '',
      equipment_model: '',
      equipment_type: 'general', // general | precision
      requested_service_type: 'maintenance', // emergency | maintenance
      downtime_description: '',
      failure_cause: '',
      repair_tariff: 0,
      material_tariff: 0,
      estimated_repair_time: '',
      estimated_completion_date: '',
      operation_department_signed_by: '',
      operation_department_signed_at: '',
      finance_department_signed_by: '',
      finance_department_signed_at: '',
      factory_director_signed_by: '',
      factory_director_signed_at: '',
      general_manager_signed_by: '',
      general_manager_signed_at: '',
      tabulator_name: '',
      form_date: '',
      annotations: ''
    },
    
    // Materiales a usar
    materials: []
  })
  
  // Flags de modo
  const useExistingClient = ref(false)
  const existingClients = ref([])
  const nextClientCode = ref('')
  const nextOtCode = ref('')
  
  // Setup validación
  const validation = useFormValidation(VALIDATION_CONFIG)
  
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
    try {
      const response = await api.get('/clients/')
      existingClients.value = response.data || []
    } catch (err) {
      existingClients.value = []
    }
  }
  
  /**
   * Obtener siguiente código de cliente
   */
  async function fetchNextClientCode() {
    try {
      const response = await api.get('/clients/code/next')
      nextClientCode.value = response.data?.client_code || 'CDS-001'
    } catch {
      nextClientCode.value = 'CDS-001'
    }
  }
  
  /**
   * Obtener siguiente código de OT
   */
  async function fetchNextOtCode(clientId = null) {
    try {
      const params = clientId ? { client_id: clientId } : {}
      const response = await api.get('/repairs/next-code', { params })
      nextOtCode.value = response.data?.repair_code || 'OT-001'
    } catch {
      nextOtCode.value = 'OT-001'
    }
  }
  
  /**
   * Seleccionar cliente existente
   */
  function selectExistingClient(clientId) {
    const client = existingClients.value.find(c => c.id === clientId)
    if (!client) return
    
    form.client.id = client.id
    form.client.name = client.name || ''
    form.client.email = client.email || ''
    form.client.phone = client.phone || ''
    form.client.phone_alt = client.phone_alt || ''
    form.client.address = client.address || ''
    form.client.city = client.city || ''
    form.client.region = client.region || ''
    form.client.country = client.country || 'Chile'
    form.client.tax_id = client.tax_id || ''
    form.client.company_name = client.company_name || ''
    form.client.billing_address = client.billing_address || ''
    form.client.customer_segment = client.customer_segment || 'regular'
    form.client.language_preference = client.language_preference || 'es'
    form.client.service_preference = client.service_preference || 'whatsapp'
    form.client.notes = client.notes || ''
    form.client.internal_notes = client.internal_notes || ''
    
    // Actualizar código OT basado en cliente
    fetchNextOtCode(client.id)
  }
  
  /**
   * Agregar material
   */
  function addMaterial() {
    form.materials.push({
      id: Date.now(),
      sku: '',
      quantity: 1,
      notes: '',
      product_id: null
    })
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
    if (!query || query.length < 2) return
    
    try {
      const response = await api.get('/inventory/', { 
        params: { search: query, limit: 5 } 
      })
      return response.data || []
    } catch {
      return []
    }
  }
  
  // ==================== SUBMIT ====================
  
  /**
   * Submit del formulario completo
   */
  async function submit() {
    // Validar todo
    const values = {
      'client.name': form.client.name,
      'client.email': form.client.email,
      'client.phone': form.client.phone,
      'client.address': form.client.address,
      'client.city': form.client.city,
      'client.region': form.client.region,
      'device.brand_other': form.device.brand_other,
      'device.model': form.device.model,
      'device.condition_notes': form.device.condition_notes,
      'repair.problem_reported': form.repair.problem_reported,
      'repair.paid_amount': form.repair.paid_amount,
      'intake.equipment_name': form.intake.equipment_name,
      'intake.failure_cause': form.intake.failure_cause
    }
    
    const validationResult = validation.validateAll(values)
    if (!validationResult.valid) {
      generalError.value = 'Por favor completa todos los campos obligatorios'
      scrollToFirstError()
      return { success: false, error: 'validation' }
    }
    
    isSubmitting.value = true
    generalError.value = ''
    
    try {
      // 1. Crear o usar cliente
      let clientId = form.client.id
      if (!useExistingClient.value || !clientId) {
        const clientResponse = await api.post('/clients/', {
          name: form.client.name,
          email: form.client.email,
          phone: form.client.phone,
          phone_alt: form.client.phone_alt || null,
          address: form.client.address,
          city: form.client.city,
          region: form.client.region,
          country: form.client.country,
          tax_id: form.client.tax_id || null,
          company_name: form.client.company_name || null,
          billing_address: form.client.billing_address || null,
          customer_segment: form.client.customer_segment,
          language_preference: form.client.language_preference,
          service_preference: form.client.service_preference,
          notes: form.client.notes || null,
          internal_notes: form.client.internal_notes || null
        })
        clientId = clientResponse.data?.id
      }
      
      if (!clientId) throw new Error('No se pudo crear el cliente')
      
      // 2. Crear device
      const deviceResponse = await api.post('/devices/', {
        client_id: clientId,
        model: form.device.model,
        brand_other: form.device.brand_other,
        serial_number: form.device.serial_number || null,
        description: form.device.description || null,
        condition_notes: form.device.condition_notes,
        year_manufactured: form.device.year_manufactured || null,
        accessories: form.device.accessories || null
      })
      const deviceId = deviceResponse.data?.id
      
      if (!deviceId) throw new Error('No se pudo registrar el equipo')
      
      // 3. Crear repair (OT)
      const repairResponse = await api.post('/repairs/', {
        device_id: deviceId,
        problem_reported: form.repair.problem_reported,
        diagnosis: form.repair.diagnosis || null,
        priority: form.repair.priority,
        paid_amount: form.repair.paid_amount,
        payment_method: form.repair.payment_method,
        warranty_days: form.repair.warranty_days
      })
      const repairId = repairResponse.data?.id
      
      if (!repairId) throw new Error('No se pudo crear la orden de trabajo')
      
      // 4. Crear intake sheet
      await api.post(`/repairs/${repairId}/intake-sheet`, {
        client_id: clientId,
        device_id: deviceId,
        equipment_name: form.intake.equipment_name,
        equipment_model: form.intake.equipment_model || form.device.model,
        equipment_type: form.intake.equipment_type,
        requested_service_type: form.intake.requested_service_type,
        downtime_description: form.intake.downtime_description || null,
        failure_cause: form.intake.failure_cause,
        repair_tariff: form.intake.repair_tariff || 0,
        material_tariff: form.intake.material_tariff || 0,
        estimated_repair_time: form.intake.estimated_repair_time || null,
        estimated_completion_date: form.intake.estimated_completion_date || null,
        operation_department_signed_by: form.intake.operation_department_signed_by || null,
        operation_department_signed_at: form.intake.operation_department_signed_at || null,
        finance_department_signed_by: form.intake.finance_department_signed_by || null,
        finance_department_signed_at: form.intake.finance_department_signed_at || null,
        factory_director_signed_by: form.intake.factory_director_signed_by || null,
        factory_director_signed_at: form.intake.factory_director_signed_at || null,
        general_manager_signed_by: form.intake.general_manager_signed_by || null,
        general_manager_signed_at: form.intake.general_manager_signed_at || null,
        tabulator_name: form.intake.tabulator_name || null,
        form_date: form.intake.form_date || null,
        annotations: form.intake.annotations || null
      })
      
      // 5. Agregar materiales si hay
      for (const material of form.materials) {
        if (material.sku && material.quantity > 0) {
          try {
            // Buscar producto
            const invResponse = await api.get('/inventory/', {
              params: { search: material.sku }
            })
            const products = invResponse.data || []
            const product = products.find(p => p.sku === material.sku)
            
            if (product) {
              await api.post(`/repairs/${repairId}/components`, {
                component_table: 'products',
                component_id: product.id,
                quantity: material.quantity,
                notes: material.notes || null
              })
            }
          } catch (err) {
            console.warn('No se pudo agregar material:', material.sku)
          }
        }
      }
      
      // 6. Subir fotos si hay (upload directo a Cloudinary)
      for (const photo of form.device.photos) {
        if (photo.file) {
          try {
            // Obtener firma para upload directo
            const signatureRes = await api.post('/uploads/signature?destination=uploads')
            const sig = signatureRes.data?.data
            
            if (sig) {
              // Upload directo a Cloudinary
              const cloudForm = new FormData()
              cloudForm.append('file', photo.file)
              cloudForm.append('api_key', sig.api_key)
              cloudForm.append('timestamp', sig.timestamp)
              cloudForm.append('signature', sig.signature)
              cloudForm.append('folder', sig.folder)
              
              const cloudRes = await fetch(
                `https://api.cloudinary.com/v1_1/${sig.cloud_name}/image/upload`,
                { method: 'POST', body: cloudForm }
              )
              
              if (!cloudRes.ok) throw new Error('Cloudinary upload failed')
              const cloudData = await cloudRes.json()
              const photoUrl = cloudData.secure_url
              
              if (photoUrl) {
                await api.post(`/repairs/${repairId}/photos`, {
                  photo_url: photoUrl,
                  caption: photo.caption || 'Foto de ingreso',
                  photo_type: 'before'
                })
              }
            } else {
              // Fallback: upload tradicional por backend
              const formData = new FormData()
              formData.append('file', photo.file)
              const uploadResponse = await api.post('/uploads/images', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
              })
              const photoUrl = uploadResponse.data?.path
              if (photoUrl) {
                await api.post(`/repairs/${repairId}/photos`, {
                  photo_url: photoUrl,
                  caption: photo.caption || 'Foto de ingreso',
                  photo_type: 'before'
                })
              }
            }
          } catch (uploadErr) {
            console.warn('Error subiendo foto:', uploadErr)
          }
        }
      }
      
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
    form.client.id = null
    form.client.name = ''
    form.client.email = ''
    form.client.phone = ''
    form.client.phone_alt = ''
    form.client.address = ''
    form.client.city = ''
    form.client.region = ''
    form.client.tax_id = ''
    form.client.company_name = ''
    form.client.billing_address = ''
    form.client.notes = ''
    form.client.internal_notes = ''
    
    form.device.brand_other = ''
    form.device.model = ''
    form.device.serial_number = ''
    form.device.year_manufactured = null
    form.device.description = ''
    form.device.condition_notes = ''
    form.device.accessories = ''
    form.device.photos = []
    
    form.repair.problem_reported = ''
    form.repair.diagnosis = ''
    form.repair.priority = 2
    form.repair.paid_amount = 20000
    form.repair.payment_method = 'cash'
    form.repair.warranty_days = 90
    
    form.intake.equipment_name = ''
    form.intake.equipment_model = ''
    form.intake.equipment_type = 'general'
    form.intake.requested_service_type = 'maintenance'
    form.intake.downtime_description = ''
    form.intake.failure_cause = ''
    form.intake.repair_tariff = 0
    form.intake.material_tariff = 0
    form.intake.estimated_repair_time = ''
    form.intake.estimated_completion_date = ''
    form.intake.operation_department_signed_by = ''
    form.intake.operation_department_signed_at = ''
    form.intake.finance_department_signed_by = ''
    form.intake.finance_department_signed_at = ''
    form.intake.factory_director_signed_by = ''
    form.intake.factory_director_signed_at = ''
    form.intake.general_manager_signed_by = ''
    form.intake.general_manager_signed_at = ''
    form.intake.tabulator_name = ''
    form.intake.form_date = ''
    form.intake.annotations = ''
    
    form.materials = []
    
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
