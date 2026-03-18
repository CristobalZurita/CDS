import api from '@/services/api'
import { uploadImage } from '@/services/uploadService'

const DEFAULT_CLIENT_CODE = 'CDS-001'
const DEFAULT_OT_CODE = 'OT-001'

function buildClientPayload(form) {
  return {
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
  }
}

function buildDevicePayload(form, clientId) {
  return {
    client_id: clientId,
    model: form.device.model,
    brand_other: form.device.brand_other,
    serial_number: form.device.serial_number || null,
    description: form.device.description || null,
    condition_notes: form.device.condition_notes,
    year_manufactured: form.device.year_manufactured || null,
    accessories: form.device.accessories || null
  }
}

function buildRepairPayload(form, deviceId) {
  return {
    device_id: deviceId,
    problem_reported: form.repair.problem_reported,
    diagnosis: form.repair.diagnosis || null,
    priority: form.repair.priority,
    paid_amount: form.repair.paid_amount,
    payment_method: form.repair.payment_method,
    warranty_days: form.repair.warranty_days
  }
}

function buildIntakePayload(form, clientId, deviceId) {
  return {
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
  }
}

async function createClientIfNeeded(form, useExistingClient) {
  if (useExistingClient && form.client.id) {
    return form.client.id
  }

  const clientResponse = await api.post('/clients/', buildClientPayload(form))
  return clientResponse.data?.id
}

async function createDevice(form, clientId) {
  const deviceResponse = await api.post('/devices/', buildDevicePayload(form, clientId))
  return deviceResponse.data?.id
}

async function createRepair(form, deviceId) {
  const repairResponse = await api.post('/repairs/', buildRepairPayload(form, deviceId))
  return repairResponse.data?.id
}

async function attachRepairMaterials(repairId, materials) {
  for (const material of materials) {
    if (!material.sku || material.quantity <= 0) continue

    try {
      const products = await searchInventoryProducts(material.sku)
      const product = products.find((entry) => entry.sku === material.sku)
      if (!product) continue

      await api.post(`/repairs/${repairId}/components`, {
        component_table: 'products',
        component_id: product.id,
        quantity: material.quantity,
        notes: material.notes || null
      })
    } catch (error) {
      console.warn('No se pudo agregar material:', material.sku, error)
    }
  }
}

async function attachRepairPhotos(repairId, photos) {
  for (const photo of photos) {
    if (!photo.file) continue

    try {
      const photoUrl = await uploadImage(photo.file, 'uploads')
      if (!photoUrl) continue

      await api.post(`/repairs/${repairId}/photos`, {
        photo_url: photoUrl,
        caption: photo.caption || 'Foto de ingreso',
        photo_type: 'before'
      })
    } catch (error) {
      console.warn('Error subiendo foto:', error)
    }
  }
}

export async function listExistingClients() {
  try {
    const response = await api.get('/clients/')
    return response.data || []
  } catch {
    return []
  }
}

export async function getNextClientCode() {
  try {
    const response = await api.get('/clients/code/next')
    return response.data?.client_code || DEFAULT_CLIENT_CODE
  } catch {
    return DEFAULT_CLIENT_CODE
  }
}

export async function getNextOtCode(clientId = null) {
  try {
    const params = clientId ? { client_id: clientId } : {}
    const response = await api.get('/repairs/next-code', { params })
    return response.data?.repair_code || DEFAULT_OT_CODE
  } catch {
    return DEFAULT_OT_CODE
  }
}

export async function searchInventoryProducts(query) {
  if (!query || query.length < 2) return []

  try {
    const response = await api.get('/inventory/', {
      params: { search: query, limit: 5 }
    })
    return response.data || []
  } catch {
    return []
  }
}

export async function submitIntakeWizard(form, { useExistingClient = false } = {}) {
  const clientId = await createClientIfNeeded(form, useExistingClient)
  if (!clientId) {
    throw new Error('No se pudo crear el cliente')
  }

  const deviceId = await createDevice(form, clientId)
  if (!deviceId) {
    throw new Error('No se pudo registrar el equipo')
  }

  const repairId = await createRepair(form, deviceId)
  if (!repairId) {
    throw new Error('No se pudo crear la orden de trabajo')
  }

  await api.post(`/repairs/${repairId}/intake-sheet`, buildIntakePayload(form, clientId, deviceId))
  await attachRepairMaterials(repairId, form.materials)
  await attachRepairPhotos(repairId, form.device.photos)

  return {
    clientId,
    deviceId,
    repairId
  }
}
