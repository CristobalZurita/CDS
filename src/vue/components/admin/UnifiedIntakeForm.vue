<template>
  <div class="intake-sheet">
    <div class="sheet-header">
      <div>
        <h2 class="sheet-title">Orden de Trabajo</h2>
        <div class="sheet-subtitle">Ingreso único de Cliente + Instrumento + OT</div>
        <div class="sheet-context">
          <span><strong>Cliente:</strong> {{ client.name || 'SIN_DATO' }}</span>
          <span><strong>Instrumento:</strong> {{ instruments[0]?.model || 'SIN_DATO' }}</span>
        </div>
      </div>
      <div class="code-block">
        <div class="code-label">Código Cliente</div>
        <div class="code-value">{{ clientCode }}</div>
        <div class="code-label mt-2">Código OT (base)</div>
        <div class="code-value">{{ otBaseCode }}</div>
      </div>
    </div>

    <div class="sheet-actions">
      <label class="form-check">
        <input v-model="useExistingClient" type="checkbox" class="form-check-input" />
        <span class="form-check-label">Usar cliente existente</span>
      </label>
      <button class="btn btn-sm btn-outline-secondary" @click="reloadCodes">Actualizar códigos</button>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

    <section class="sheet-section">
      <h4>Cliente</h4>
      <div class="row g-2">
        <div v-if="useExistingClient" class="col-md-6">
          <label class="form-label">Cliente existente *</label>
          <select v-model.number="existingClientId" class="form-select" @change="onClientSelected">
            <option :value="null">Selecciona cliente</option>
            <option v-for="c in clients" :key="c.id" :value="c.id">
              {{ c.client_code }} - {{ c.name }}
            </option>
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label">Nombre *</label>
          <input v-model="client.name" class="form-control" :class="invalidClass('client.name')" />
        </div>
        <div class="col-md-6">
          <label class="form-label">Email *</label>
          <input v-model="client.email" type="email" class="form-control" :class="invalidClass('client.email')" />
        </div>
        <div class="col-md-6">
          <label class="form-label">Teléfono / WhatsApp *</label>
          <input v-model="client.phone" class="form-control" :class="invalidClass('client.phone')" />
        </div>
        <div class="col-md-6">
          <label class="form-label">Dirección *</label>
          <input v-model="client.address" class="form-control" :class="invalidClass('client.address')" />
        </div>
        <div class="col-md-4">
          <label class="form-label">Ciudad *</label>
          <input v-model="client.city" class="form-control" :class="invalidClass('client.city')" />
        </div>
        <div class="col-md-4">
          <label class="form-label">Región *</label>
          <input v-model="client.region" class="form-control" :class="invalidClass('client.region')" />
        </div>
        <div class="col-md-4">
          <label class="form-label">País *</label>
          <input v-model="client.country" class="form-control" :class="invalidClass('client.country')" />
        </div>
        <div class="col-md-4">
          <label class="form-label">RUT *</label>
          <input v-model="client.tax_id" class="form-control" :class="invalidClass('client.tax_id')" />
        </div>
        <div class="col-md-4">
          <label class="form-label">Razón Social *</label>
          <input v-model="client.company_name" class="form-control" :class="invalidClass('client.company_name')" />
        </div>
        <div class="col-md-4">
          <label class="form-label">Dirección de facturación *</label>
          <input v-model="client.billing_address" class="form-control" :class="invalidClass('client.billing_address')" />
        </div>
        <div class="col-md-4">
          <label class="form-label">Segmento *</label>
          <select v-model="client.customer_segment" class="form-select" :class="invalidClass('client.customer_segment')">
            <option value="regular">Regular</option>
            <option value="vip">VIP</option>
            <option value="new">Nuevo</option>
            <option value="inactive">Inactivo</option>
          </select>
        </div>
        <div class="col-md-4">
          <label class="form-label">Idioma *</label>
          <select v-model="client.language_preference" class="form-select" :class="invalidClass('client.language_preference')">
            <option value="es">Español</option>
            <option value="en">Inglés</option>
          </select>
        </div>
        <div class="col-12">
          <label class="form-label">Notas *</label>
          <textarea v-model="client.notes" class="form-control" rows="2" :class="invalidClass('client.notes')"></textarea>
        </div>
        <div class="col-12">
          <label class="form-label">Notas internas *</label>
          <textarea v-model="client.internal_notes" class="form-control" rows="2" :class="invalidClass('client.internal_notes')"></textarea>
        </div>
      </div>
    </section>

    <section class="sheet-section">
      <div class="d-flex justify-content-between align-items-center">
        <h4>Instrumentos y OT</h4>
        <button class="btn btn-sm btn-outline-primary" @click="addInstrument">Agregar instrumento</button>
      </div>

      <div v-for="(instrument, idx) in instruments" :key="instrument.key" class="instrument-card">
        <div class="instrument-header">
          <div>
            <h5>Instrumento {{ idx + 1 }}</h5>
            <div class="code-small">Código instrumento: {{ instrumentCode(idx) }}</div>
          </div>
          <button v-if="instruments.length > 1" class="btn btn-sm btn-outline-danger" @click="removeInstrument(idx)">Quitar</button>
        </div>

        <div class="row g-2">
          <div class="col-md-4">
            <label class="form-label">Marca *</label>
            <input v-model="instrument.brand_other" class="form-control" :class="invalidClass(`instrument.${idx}.brand_other`)" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Modelo *</label>
            <input v-model="instrument.model" class="form-control" :class="invalidClass(`instrument.${idx}.model`)" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Número de serie *</label>
            <input v-model="instrument.serial_number" class="form-control" :class="invalidClass(`instrument.${idx}.serial_number`)" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Año *</label>
            <input v-model="instrument.year_manufactured" type="number" class="form-control" :class="invalidClass(`instrument.${idx}.year_manufactured`)" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Accesorios entregados *</label>
            <input v-model="instrument.accessories" class="form-control" :class="invalidClass(`instrument.${idx}.accessories`)" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Condición *</label>
            <input v-model="instrument.condition_notes" class="form-control" :class="invalidClass(`instrument.${idx}.condition_notes`)" />
          </div>
          <div class="col-12">
            <label class="form-label">Descripción *</label>
            <textarea v-model="instrument.description" class="form-control" rows="2" :class="invalidClass(`instrument.${idx}.description`)"></textarea>
          </div>
        </div>

        <div class="row g-2 mt-2">
          <div class="col-md-6">
            <label class="form-label">Problema reportado *</label>
            <textarea v-model="instrument.problem_reported" class="form-control" rows="2" :class="invalidClass(`instrument.${idx}.problem_reported`)"></textarea>
          </div>
          <div class="col-md-6">
            <label class="form-label">Diagnóstico *</label>
            <textarea v-model="instrument.diagnosis" class="form-control" rows="2" :class="invalidClass(`instrument.${idx}.diagnosis`)"></textarea>
          </div>
          <div class="col-md-6">
            <label class="form-label">Trabajo realizado *</label>
            <textarea v-model="instrument.work_performed" class="form-control" rows="2" :class="invalidClass(`instrument.${idx}.work_performed`)"></textarea>
          </div>
          <div class="col-md-3">
            <label class="form-label">Prioridad *</label>
            <select v-model.number="instrument.priority" class="form-select" :class="invalidClass(`instrument.${idx}.priority`)">
              <option :value="1">Alta</option>
              <option :value="2">Normal</option>
              <option :value="3">Baja</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Abono *</label>
            <input v-model.number="instrument.paid_amount" type="number" class="form-control" :class="invalidClass(`instrument.${idx}.paid_amount`)" />
          </div>
          <div class="col-md-3">
            <label class="form-label">Método pago *</label>
            <select v-model="instrument.payment_method" class="form-select" :class="invalidClass(`instrument.${idx}.payment_method`)">
              <option value="cash">Efectivo</option>
              <option value="transfer">Transferencia</option>
              <option value="web">Web</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Garantía (días) *</label>
            <input v-model.number="instrument.warranty_days" type="number" class="form-control" :class="invalidClass(`instrument.${idx}.warranty_days`)" />
          </div>
        </div>

        <div class="sheet-form-section mt-3">
          <h6>Planilla de operación y mantenimiento</h6>
          <div class="row g-2">
            <div class="col-md-4">
              <label class="form-label">Nombre del dispositivo *</label>
              <input v-model="instrument.equipment_name" class="form-control" :class="invalidClass(`instrument.${idx}.equipment_name`)" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Modelo del dispositivo *</label>
              <input v-model="instrument.equipment_model" class="form-control" :class="invalidClass(`instrument.${idx}.equipment_model`)" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Tipo de equipo *</label>
              <select v-model="instrument.equipment_type" class="form-select" :class="invalidClass(`instrument.${idx}.equipment_type`)">
                <option value="general">Equipo general</option>
                <option value="precision">Equipo de precisión</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label">Tipo de solicitud *</label>
              <select v-model="instrument.requested_service_type" class="form-select" :class="invalidClass(`instrument.${idx}.requested_service_type`)">
                <option value="emergency">Reparación de emergencia</option>
                <option value="maintenance">Mantenimiento general</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label">Falta de tiempo / disponibilidad *</label>
              <input v-model="instrument.downtime_description" class="form-control" :class="invalidClass(`instrument.${idx}.downtime_description`)" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Tiempo esperado de reparación *</label>
              <input v-model="instrument.estimated_repair_time" class="form-control" :class="invalidClass(`instrument.${idx}.estimated_repair_time`)" placeholder="Ej: 7 días hábiles" />
            </div>
            <div class="col-md-8">
              <label class="form-label">Causa del problema *</label>
              <textarea v-model="instrument.failure_cause" class="form-control" rows="2" :class="invalidClass(`instrument.${idx}.failure_cause`)"></textarea>
            </div>
            <div class="col-md-2">
              <label class="form-label">Tarifa reparación *</label>
              <input v-model.number="instrument.repair_tariff" type="number" class="form-control" :class="invalidClass(`instrument.${idx}.repair_tariff`)" />
            </div>
            <div class="col-md-2">
              <label class="form-label">Tarifa material *</label>
              <input v-model.number="instrument.material_tariff" type="number" class="form-control" :class="invalidClass(`instrument.${idx}.material_tariff`)" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Fecha estimada de finalización *</label>
              <input v-model="instrument.estimated_completion_date" type="date" class="form-control" :class="invalidClass(`instrument.${idx}.estimated_completion_date`)" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Depto. Tecnología (firma) *</label>
              <input v-model="instrument.operation_department_signed_by" class="form-control" :class="invalidClass(`instrument.${idx}.operation_department_signed_by`)" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Fecha Depto. Tecnología *</label>
              <input v-model="instrument.operation_department_signed_at" type="date" class="form-control" :class="invalidClass(`instrument.${idx}.operation_department_signed_at`)" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Depto. Finanzas (firma) *</label>
              <input v-model="instrument.finance_department_signed_by" class="form-control" :class="invalidClass(`instrument.${idx}.finance_department_signed_by`)" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Fecha Depto. Finanzas *</label>
              <input v-model="instrument.finance_department_signed_at" type="date" class="form-control" :class="invalidClass(`instrument.${idx}.finance_department_signed_at`)" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Director fábrica (firma) *</label>
              <input v-model="instrument.factory_director_signed_by" class="form-control" :class="invalidClass(`instrument.${idx}.factory_director_signed_by`)" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Fecha Director fábrica *</label>
              <input v-model="instrument.factory_director_signed_at" type="date" class="form-control" :class="invalidClass(`instrument.${idx}.factory_director_signed_at`)" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Gerente general (firma) *</label>
              <input v-model="instrument.general_manager_signed_by" class="form-control" :class="invalidClass(`instrument.${idx}.general_manager_signed_by`)" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Fecha Gerente general *</label>
              <input v-model="instrument.general_manager_signed_at" type="date" class="form-control" :class="invalidClass(`instrument.${idx}.general_manager_signed_at`)" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Tabulador *</label>
              <input v-model="instrument.tabulator_name" class="form-control" :class="invalidClass(`instrument.${idx}.tabulator_name`)" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Fecha formulario *</label>
              <input v-model="instrument.form_date" type="date" class="form-control" :class="invalidClass(`instrument.${idx}.form_date`)" />
            </div>
            <div class="col-12">
              <label class="form-label">Anotaciones operativas *</label>
              <textarea v-model="instrument.annotations" class="form-control" rows="2" :class="invalidClass(`instrument.${idx}.annotations`)"></textarea>
            </div>
          </div>
        </div>

        <div class="row g-2 mt-2">
          <div class="col-md-6">
            <label class="form-label">Foto inicial *</label>
            <input type="file" class="form-control" accept="image/*" @change="onFileSelected($event, idx)" />
          </div>
          <div class="col-md-6">
            <label class="form-label">Descripción foto *</label>
            <input v-model="instrument.photo_caption" class="form-control" :class="invalidClass(`instrument.${idx}.photo_caption`)" />
          </div>
        </div>

        <div class="materials-section">
          <div class="d-flex justify-content-between align-items-center">
            <h6>Materiales usados</h6>
            <button class="btn btn-sm btn-outline-secondary" @click="addMaterial(idx)">Agregar material</button>
          </div>
          <div v-for="(mat, mIdx) in instrument.materials" :key="mIdx" class="row g-2 align-items-end">
            <div class="col-md-4">
              <label class="form-label">SKU *</label>
              <input v-model="mat.sku" class="form-control" :class="invalidClass(`instrument.${idx}.materials.${mIdx}.sku`)" />
            </div>
            <div class="col-md-2">
              <label class="form-label">Cantidad *</label>
              <input v-model.number="mat.quantity" type="number" min="1" class="form-control" :class="invalidClass(`instrument.${idx}.materials.${mIdx}.quantity`)" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Notas *</label>
              <input v-model="mat.notes" class="form-control" :class="invalidClass(`instrument.${idx}.materials.${mIdx}.notes`)" />
            </div>
            <div class="col-md-2">
              <button class="btn btn-sm btn-outline-danger w-100" @click="removeMaterial(idx, mIdx)">Quitar</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="sheet-footer">
      <button class="btn btn-outline-secondary" @click="resetForm" :disabled="saving">Limpiar</button>
      <button class="btn btn-primary" @click="submit" :disabled="saving">
        {{ saving ? 'Guardando...' : 'Crear OT' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/services/api'

const emit = defineEmits(['completed'])

const saving = ref(false)
const errorMessage = ref('')
const invalidFields = ref(new Set())

const useExistingClient = ref(false)
const existingClientId = ref(null)
const clients = ref([])
const nextClientId = ref(1)
const otBaseIndex = ref(1)
const otPreviewCode = ref('')

const client = ref({
  name: '',
  email: '',
  phone: '',
  phone_alt: '',
  address: '',
  city: '',
  region: '',
  country: 'Chile',
  notes: '',
  internal_notes: '',
  tax_id: '',
  company_name: '',
  billing_address: '',
  customer_segment: 'regular',
  language_preference: 'es',
  service_preference: 'whatsapp'
})

const instruments = ref([createInstrument()])

function createInstrument() {
  return {
    key: (crypto?.randomUUID && crypto.randomUUID()) || String(Date.now() + Math.random()),
    brand_other: '',
    model: '',
    serial_number: '',
    year_manufactured: '',
    description: '',
    condition_notes: '',
    accessories: '',
    problem_reported: '',
    diagnosis: '',
    work_performed: '',
    priority: 2,
    paid_amount: 20000,
    payment_method: 'cash',
    warranty_days: 90,
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
    annotations: '',
    photo_file: null,
    photo_caption: '',
    materials: []
  }
}

const clientCode = computed(() => `CDS-${String(nextClientId.value).padStart(3, '0')}`)
const otBaseCode = computed(() => otPreviewCode.value || `${clientCode.value}-OT-${String(otBaseIndex.value).padStart(3, '0')}`)

const instrumentCode = (idx) => {
  if (idx === 0 && instruments.value.length === 1) {
    return otBaseCode.value
  }
  return `${otBaseCode.value}-${String(idx + 1).padStart(2, '0')}`
}

const invalidClass = (key) => invalidFields.value.has(key) ? 'is-invalid' : ''

const addInstrument = () => instruments.value.push(createInstrument())
const removeInstrument = (idx) => instruments.value.splice(idx, 1)

const addMaterial = (idx) => instruments.value[idx].materials.push({ sku: '', quantity: 1, notes: '' })
const removeMaterial = (idx, mIdx) => instruments.value[idx].materials.splice(mIdx, 1)

const onFileSelected = (e, idx) => {
  instruments.value[idx].photo_file = e.target.files?.[0] || null
}

const applyDefaults = () => {
  let applied = false

  const ensureText = (obj, key) => {
    if (!obj[key]) {
      obj[key] = 'SIN_DATO'
      applied = true
    }
  }
  const ensureNumber = (obj, key) => {
    if (obj[key] === '' || obj[key] === null || obj[key] === undefined) {
      obj[key] = 0
      applied = true
    }
  }

  const clientTextFields = [
    'name', 'email', 'phone', 'phone_alt', 'address', 'city', 'region', 'country',
    'notes', 'internal_notes', 'tax_id', 'company_name', 'billing_address',
    'customer_segment', 'language_preference', 'service_preference'
  ]
  clientTextFields.forEach((field) => ensureText(client.value, field))

  instruments.value.forEach((inst) => {
    const instTextFields = [
      'brand_other', 'model', 'serial_number', 'description', 'condition_notes',
      'accessories', 'problem_reported', 'diagnosis', 'work_performed',
      'payment_method', 'photo_caption',
      'equipment_name', 'equipment_model', 'equipment_type', 'requested_service_type',
      'downtime_description', 'failure_cause', 'estimated_repair_time',
      'estimated_completion_date', 'operation_department_signed_by', 'operation_department_signed_at',
      'finance_department_signed_by', 'finance_department_signed_at', 'factory_director_signed_by',
      'factory_director_signed_at', 'general_manager_signed_by', 'general_manager_signed_at',
      'tabulator_name', 'form_date', 'annotations'
    ]
    instTextFields.forEach((field) => ensureText(inst, field))
    const instNumberFields = [
      'year_manufactured', 'priority', 'paid_amount', 'warranty_days',
      'repair_tariff', 'material_tariff'
    ]
    instNumberFields.forEach((field) => ensureNumber(inst, field))
    inst.materials.forEach((mat) => {
      ensureText(mat, 'sku')
      ensureText(mat, 'notes')
      ensureNumber(mat, 'quantity')
    })
  })

  return applied
}

const reloadCodes = async () => {
  await fetchNextClientCode()
  if (existingClientId.value) {
    await fetchNextOtIndex(existingClientId.value)
  }
}

const fetchNextClientCode = async () => {
  try {
    const res = await api.get('/clients/code/next')
    const payload = res.data || res || {}
    nextClientId.value = payload.next_client_id || 1
  } catch (e) {
    try {
      const fallbackRes = await api.get('/clients/next-code')
      const fallbackPayload = fallbackRes.data || fallbackRes || {}
      nextClientId.value = fallbackPayload.next_client_id || 1
    } catch (fallbackError) {
      nextClientId.value = 1
    }
  }
}

const fetchClients = async () => {
  try {
    const res = await api.get('/clients')
    clients.value = res.data || res || []
  } catch (e) {
    clients.value = []
  }
}

const fetchNextOtIndex = async (clientId) => {
  try {
    const res = await api.get('/repairs/next-code', { params: { client_id: clientId } })
    const payload = res.data || res || {}
    otPreviewCode.value = payload.repair_code || payload.ot_base_code || ''
    if (payload.next_repair_id) {
      otBaseIndex.value = Number(payload.next_repair_id) || 1
      return
    }
    otBaseIndex.value = 1
  } catch (e) {
    otPreviewCode.value = ''
    try {
      const fallbackRes = await api.get(`/clients/${clientId}/repairs`)
      const count = (fallbackRes.data || fallbackRes || []).length
      otBaseIndex.value = count + 1
    } catch (fallbackError) {
      otBaseIndex.value = 1
    }
  }
}

const onClientSelected = async () => {
  const selected = clients.value.find(c => c.id === existingClientId.value)
  if (!selected) return
  client.value.name = selected.name || client.value.name
  client.value.email = selected.email || client.value.email
  client.value.phone = selected.phone || client.value.phone
  client.value.phone_alt = selected.phone_alt || client.value.phone_alt
  client.value.address = selected.address || client.value.address
  client.value.city = selected.city || client.value.city
  client.value.region = selected.region || client.value.region
  client.value.country = selected.country || client.value.country
  client.value.notes = selected.notes || client.value.notes
  client.value.internal_notes = selected.internal_notes || client.value.internal_notes
  client.value.tax_id = selected.tax_id || client.value.tax_id
  client.value.company_name = selected.company_name || client.value.company_name
  client.value.billing_address = selected.billing_address || client.value.billing_address
  client.value.customer_segment = selected.customer_segment || client.value.customer_segment
  client.value.language_preference = selected.language_preference || client.value.language_preference
  client.value.service_preference = selected.service_preference || client.value.service_preference
  nextClientId.value = selected.id
  await fetchNextOtIndex(selected.id)
}

const validate = () => {
  invalidFields.value = new Set()
  const requiredClientFields = [
    'name', 'email', 'phone', 'phone_alt', 'address', 'city', 'region', 'country',
    'notes', 'internal_notes', 'tax_id', 'company_name', 'billing_address',
    'customer_segment', 'language_preference', 'service_preference'
  ]
  requiredClientFields.forEach((field) => {
    if (!client.value[field]) invalidFields.value.add(`client.${field}`)
  })
  instruments.value.forEach((inst, idx) => {
    const requiredInstFields = [
      'brand_other', 'model', 'serial_number', 'year_manufactured',
      'description', 'condition_notes', 'accessories',
      'problem_reported', 'diagnosis', 'work_performed',
      'priority', 'paid_amount', 'payment_method', 'warranty_days',
      'photo_caption',
      'equipment_name', 'equipment_model', 'equipment_type', 'requested_service_type',
      'downtime_description', 'failure_cause', 'repair_tariff', 'material_tariff',
      'estimated_repair_time', 'estimated_completion_date',
      'operation_department_signed_by', 'operation_department_signed_at',
      'finance_department_signed_by', 'finance_department_signed_at',
      'factory_director_signed_by', 'factory_director_signed_at',
      'general_manager_signed_by', 'general_manager_signed_at',
      'tabulator_name', 'form_date', 'annotations'
    ]
    requiredInstFields.forEach((field) => {
      if (!inst[field]) invalidFields.value.add(`instrument.${idx}.${field}`)
    })
    if (!inst.photo_file) invalidFields.value.add(`instrument.${idx}.photo_file`)
    inst.materials.forEach((mat, mIdx) => {
      if (!mat.sku) invalidFields.value.add(`instrument.${idx}.materials.${mIdx}.sku`)
      if (!mat.quantity) invalidFields.value.add(`instrument.${idx}.materials.${mIdx}.quantity`)
      if (!mat.notes) invalidFields.value.add(`instrument.${idx}.materials.${mIdx}.notes`)
    })
  })
  if (useExistingClient.value && !existingClientId.value) {
    invalidFields.value.add('client.existing')
  }
  return invalidFields.value.size === 0
}

const submit = async () => {
  errorMessage.value = ''
  if (!validate()) {
    errorMessage.value = 'Completa todos los campos obligatorios.'
    return
  }
  const defaultsApplied = applyDefaults()

  saving.value = true
  try {
    let clientId = existingClientId.value
    if (!useExistingClient.value) {
      const clientRes = await api.post('/clients', {
        name: client.value.name,
        email: client.value.email,
        phone: client.value.phone,
        phone_alt: client.value.phone_alt,
        address: client.value.address,
        city: client.value.city,
        region: client.value.region,
        country: client.value.country,
        notes: client.value.notes,
        internal_notes: client.value.internal_notes,
        tax_id: client.value.tax_id,
        company_name: client.value.company_name,
        billing_address: client.value.billing_address,
        customer_segment: client.value.customer_segment,
        language_preference: client.value.language_preference,
        service_preference: client.value.service_preference,
        preferred_contact: client.value.service_preference
      })
      clientId = clientRes.data?.id || clientRes.id
      nextClientId.value = clientId
    }

    await fetchNextOtIndex(clientId)

    const createdRepairs = []
    let otParentRepairId = null

    for (let idx = 0; idx < instruments.value.length; idx += 1) {
      const inst = instruments.value[idx]
      const deviceRes = await api.post('/devices/', {
        client_id: clientId,
        model: inst.model,
        brand_other: inst.brand_other,
        serial_number: inst.serial_number,
        description: inst.description,
        condition_notes: inst.condition_notes,
        year_manufactured: inst.year_manufactured,
        accessories: inst.accessories
      })
      const deviceId = deviceRes.data?.id || deviceRes.id

      const repairPayload = {
        device_id: deviceId,
        problem_reported: inst.problem_reported,
        diagnosis: inst.diagnosis,
        work_performed: inst.work_performed,
        priority: inst.priority,
        paid_amount: inst.paid_amount,
        payment_method: inst.payment_method,
        payment_status: 'deposit',
        warranty_days: inst.warranty_days
      }

      // Nomenclatura OT backend-first:
      // - 1er instrumento: OT base
      // - siguientes: agrupados al OT base (el backend asigna sufijo correlativo)
      if (otParentRepairId && idx > 0) {
        repairPayload.ot_parent_id = otParentRepairId
      }

      const repairRes = await api.post('/repairs', repairPayload)
      const repairId = repairRes.data?.id || repairRes.id
      if (!repairId) {
        throw new Error('No se pudo crear OT')
      }
      if (!otParentRepairId) {
        otParentRepairId = repairId
      }
      createdRepairs.push({ idx, repairId, inst })

      if (inst.photo_file) {
        const formData = new FormData()
        formData.append('file', inst.photo_file)
        const uploadRes = await api.post('/uploads/images', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        const path = uploadRes.data?.path || uploadRes.path
        if (path) {
          await api.post(`/repairs/${repairId}/photos`, {
            photo_url: path,
            caption: inst.photo_caption,
            photo_type: 'before'
          })
        }
      }

      for (const mat of inst.materials) {
        const invRes = await api.get('/inventory/', { params: { search: mat.sku } })
        const items = invRes.data || invRes || []
        const match = items.find(i => i.sku === mat.sku) || items[0]
        if (!match) throw new Error(`SKU no encontrado: ${mat.sku}`)

        await api.post(`/repairs/${repairId}/components`, {
          component_table: 'products',
          component_id: match.id,
          quantity: mat.quantity,
          notes: mat.notes
        })
      }
    }

    // Guardar intake sheets al final para usar códigos OT definitivos
    // (el backend puede reasignar el OT base a -01 al agrupar).
    for (const created of createdRepairs) {
      const repairInfoRes = await api.get(`/repairs/${created.repairId}`)
      const repairInfo = repairInfoRes.data || repairInfoRes || {}
      const finalClientCode = repairInfo.client?.client_code || clientCode.value
      const finalOtCode = repairInfo.repair_code || repairInfo.repair_number || otBaseCode.value

      await api.post(`/repairs/${created.repairId}/intake-sheet`, {
        client_code: finalClientCode,
        ot_code: finalOtCode,
        instrument_code: finalOtCode,
        equipment_name: created.inst.equipment_name,
        equipment_model: created.inst.equipment_model,
        equipment_type: created.inst.equipment_type,
        requested_service_type: created.inst.requested_service_type,
        downtime_description: created.inst.downtime_description,
        failure_cause: created.inst.failure_cause,
        repair_tariff: created.inst.repair_tariff,
        material_tariff: created.inst.material_tariff,
        estimated_repair_time: created.inst.estimated_repair_time,
        estimated_completion_date: created.inst.estimated_completion_date,
        operation_department_signed_by: created.inst.operation_department_signed_by,
        operation_department_signed_at: created.inst.operation_department_signed_at,
        finance_department_signed_by: created.inst.finance_department_signed_by,
        finance_department_signed_at: created.inst.finance_department_signed_at,
        factory_director_signed_by: created.inst.factory_director_signed_by,
        factory_director_signed_at: created.inst.factory_director_signed_at,
        general_manager_signed_by: created.inst.general_manager_signed_by,
        general_manager_signed_at: created.inst.general_manager_signed_at,
        tabulator_name: created.inst.tabulator_name,
        form_date: created.inst.form_date,
        annotations: created.inst.annotations
      })
    }

    emit('completed', { client_id: clientId })
    resetForm()
    if (defaultsApplied) {
      alert('Se completaron campos vacíos con SIN_DATO / 0.')
    }
  } catch (e) {
    errorMessage.value = e?.response?.data?.detail || e?.message || 'Error en ingreso'
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  client.value = {
    name: '',
    email: '',
    phone: '',
    phone_alt: '',
    address: '',
    city: '',
    region: '',
    country: 'Chile',
    notes: '',
    internal_notes: '',
    tax_id: '',
    company_name: '',
    billing_address: '',
    customer_segment: 'regular',
    language_preference: 'es',
    service_preference: 'whatsapp'
  }
  instruments.value = [createInstrument()]
  invalidFields.value = new Set()
  existingClientId.value = null
  useExistingClient.value = false
  otPreviewCode.value = ''
  otBaseIndex.value = 1
  reloadCodes()
}

onMounted(async () => {
  await Promise.all([fetchNextClientCode(), fetchClients()])
})
</script>

<style scoped lang="scss">
@use '@/scss/core' as *;

.sheet-header {
  position: sticky;
  top: 0;
  z-index: 5;
  background: $color-sand-100-legacy;
  padding: 1rem 0;
  border-bottom: 1px solid rgba($color-dark, 0.2);
}

.sheet-context {
  display: flex;
  gap: 1.5rem;
  font-size: 0.95rem;
  color: $text-color-muted;
  margin-top: 0.35rem;
}

.intake-sheet {
  background: $color-white;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid $color-gray-200-legacy;
}
.sheet-header {
  display: flex;
  justify-content: space-between;
  gap: 1.5rem;
  align-items: center;
  margin-bottom: 1rem;
}
.sheet-title {
  font-size: 1.6rem;
  font-weight: 700;
  margin: 0;
}
.sheet-subtitle {
  color: $color-gray-500-legacy;
}
.code-block {
  background: $color-slate-25-legacy;
  border: 1px solid $color-border-light-legacy;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  text-align: right;
  min-width: 220px;
}
.code-label {
  font-size: 0.75rem;
  color: $color-gray-500-legacy;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.code-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: $color-orange-800-legacy;
}
.sheet-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.sheet-section {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid $color-gray-200-legacy;
}
.instrument-card {
  border: 1px solid $color-gray-200-legacy;
  border-radius: 10px;
  padding: 1rem;
  margin-top: 1rem;
  background: $color-white-ice-legacy;
}
.instrument-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.code-small {
  font-size: 0.85rem;
  color: $color-gray-500-legacy;
}
.materials-section {
  margin-top: 1rem;
  padding-top: 0.5rem;
  border-top: 1px dashed $color-gray-200-legacy;
}
.sheet-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}
</style>
