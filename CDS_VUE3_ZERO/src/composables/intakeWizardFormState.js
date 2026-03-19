export const INTAKE_WIZARD_VALIDATION_CONFIG = {
  'client.name': {
    required: true,
    minLength: 2,
    maxLength: 100,
    message: 'Nombre es obligatorio (2-100 caracteres)'
  },
  'client.email': {
    required: true,
    email: true,
    message: 'Email valido es obligatorio'
  },
  'client.phone': {
    required: true,
    phone: true,
    message: 'Telefono chileno valido es obligatorio'
  },
  'client.address': {
    required: true,
    minLength: 5,
    message: 'Direccion es obligatoria'
  },
  'client.city': {
    required: true,
    message: 'Ciudad es obligatoria'
  },
  'client.region': {
    required: true,
    message: 'Region es obligatoria'
  },
  'client.tax_id': {
    rut: true,
    message: 'RUT invalido'
  },
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
    message: 'Describa el estado fisico'
  },
  'repair.problem_reported': {
    required: true,
    minLength: 10,
    message: 'Describa el problema (minimo 10 caracteres)'
  },
  'repair.priority': {
    required: true
  },
  'repair.paid_amount': {
    required: true,
    min: 0,
    numbersOnly: true,
    message: 'Monto de abono invalido'
  },
  'intake.equipment_name': {
    required: true,
    message: 'Nombre del equipo es obligatorio'
  },
  'intake.failure_cause': {
    required: true,
    message: 'Causa del problema es obligatoria'
  }
}

function createDefaultClient() {
  return {
    id: null,
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
  }
}

function createDefaultDevice() {
  return {
    brand_other: '',
    model: '',
    serial_number: '',
    year_manufactured: null,
    description: '',
    condition_notes: '',
    accessories: '',
    photos: []
  }
}

function createDefaultRepair() {
  return {
    problem_reported: '',
    diagnosis: '',
    priority: 2,
    paid_amount: 20000,
    payment_method: 'cash',
    warranty_days: 90
  }
}

function createDefaultIntake() {
  return {
    equipment_name: '',
    equipment_model: '',
    equipment_type: 'general',
    requested_service_type: 'maintenance',
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
  }
}

export function createIntakeWizardFormState() {
  return {
    client: createDefaultClient(),
    device: createDefaultDevice(),
    repair: createDefaultRepair(),
    intake: createDefaultIntake(),
    materials: []
  }
}

export function applyExistingClientToForm(form, client) {
  if (!client) return

  Object.assign(form.client, createDefaultClient(), {
    id: client.id ?? null,
    name: client.name || '',
    email: client.email || '',
    phone: client.phone || '',
    phone_alt: client.phone_alt || '',
    address: client.address || '',
    city: client.city || '',
    region: client.region || '',
    country: client.country || 'Chile',
    tax_id: client.tax_id || '',
    company_name: client.company_name || '',
    billing_address: client.billing_address || '',
    customer_segment: client.customer_segment || 'regular',
    language_preference: client.language_preference || 'es',
    service_preference: client.service_preference || 'whatsapp',
    notes: client.notes || '',
    internal_notes: client.internal_notes || ''
  })
}

export function buildIntakeWizardValidationValues(form) {
  return {
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
}

export function resolveIntakeWizardCanSubmit({
  isSubmitting = false,
  isLoading = false,
  isValid = false,
  form
} = {}) {
  return !isSubmitting &&
    !isLoading &&
    isValid &&
    form?.client?.name &&
    form?.device?.model &&
    form?.repair?.problem_reported
}

export function resolveIntakeWizardProgress(form) {
  const sections = ['client', 'device', 'repair', 'intake']
  const completed = sections.filter((section) => {
    switch (section) {
      case 'client':
        return !!form.client.name && !!form.client.email
      case 'device':
        return !!form.device.brand_other && !!form.device.model
      case 'repair':
        return !!form.repair.problem_reported
      case 'intake':
        return !!form.intake.equipment_name
      default:
        return false
    }
  }).length

  return Math.round((completed / sections.length) * 100)
}

export function createIntakeWizardMaterial() {
  return {
    id: Date.now(),
    sku: '',
    quantity: 1,
    notes: '',
    product_id: null
  }
}

export function resetIntakeWizardFormState(form) {
  Object.assign(form.client, createDefaultClient())
  Object.assign(form.device, createDefaultDevice())
  Object.assign(form.repair, createDefaultRepair())
  Object.assign(form.intake, createDefaultIntake())
  form.materials = []
}
