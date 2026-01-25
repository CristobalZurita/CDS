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

const client = ref({
  name: '',
  email: '',
  phone: '',
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
  language_preference: 'es'
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
    photo_file: null,
    photo_caption: '',
    materials: []
  }
}

const clientCode = computed(() => `CDS-${String(nextClientId.value).padStart(3, '0')}`)
const otBaseCode = computed(() => `${clientCode.value}-OT-${String(otBaseIndex.value).padStart(3, '0')}`)

const instrumentCode = (idx) => `${otBaseCode.value}-${String(idx + 1).padStart(2, '0')}`

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
    'name', 'email', 'phone', 'address', 'city', 'region', 'country',
    'notes', 'internal_notes', 'tax_id', 'company_name', 'billing_address',
    'customer_segment', 'language_preference'
  ]
  clientTextFields.forEach((field) => ensureText(client.value, field))

  instruments.value.forEach((inst) => {
    const instTextFields = [
      'brand_other', 'model', 'serial_number', 'description', 'condition_notes',
      'accessories', 'problem_reported', 'diagnosis', 'work_performed',
      'payment_method', 'photo_caption'
    ]
    instTextFields.forEach((field) => ensureText(inst, field))
    const instNumberFields = ['year_manufactured', 'priority', 'paid_amount', 'warranty_days']
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
    const res = await api.get('/clients/next-code')
    nextClientId.value = res.data?.next_client_id || res.next_client_id || 1
  } catch (e) {
    nextClientId.value = 1
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
    const res = await api.get(`/clients/${clientId}/repairs`)
    const count = (res.data || res || []).length
    otBaseIndex.value = count + 1
  } catch (e) {
    otBaseIndex.value = 1
  }
}

const onClientSelected = async () => {
  const selected = clients.value.find(c => c.id === existingClientId.value)
  if (!selected) return
  client.value.name = selected.name || client.value.name
  client.value.email = selected.email || client.value.email
  client.value.phone = selected.phone || client.value.phone
  client.value.address = selected.address || client.value.address
  nextClientId.value = selected.id
  await fetchNextOtIndex(selected.id)
}

const validate = () => {
  invalidFields.value = new Set()
  const requiredClientFields = [
    'name', 'email', 'phone', 'address', 'city', 'region', 'country',
    'notes', 'internal_notes', 'tax_id', 'company_name', 'billing_address',
    'customer_segment', 'language_preference'
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
      'photo_caption'
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
  const defaultsApplied = applyDefaults()
  if (!validate()) {
    errorMessage.value = 'Completa todos los campos obligatorios.'
    return
  }

  saving.value = true
  try {
    let clientId = existingClientId.value
    if (!useExistingClient.value) {
      const clientRes = await api.post('/clients', {
        name: client.value.name,
        email: client.value.email,
        phone: client.value.phone,
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
        language_preference: client.value.language_preference
      })
      clientId = clientRes.data?.id || clientRes.id
      nextClientId.value = clientId
    }

    await fetchNextOtIndex(clientId)

    for (let idx = 0; idx < instruments.value.length; idx += 1) {
      const inst = instruments.value[idx]
      const deviceRes = await api.post('/devices/', {
        client_id: clientId,
        model: inst.model,
        brand_other: inst.brand_other,
        serial_number: inst.serial_number,
        description: inst.description,
        condition_notes: inst.condition_notes,
        year_manufactured: inst.year_manufactured
      })
      const deviceId = deviceRes.data?.id || deviceRes.id

      const repairCode = instruments.value.length > 1 ? instrumentCode(idx) : otBaseCode.value

      const repairRes = await api.post('/repairs', {
        device_id: deviceId,
        repair_number: repairCode,
        problem_reported: inst.problem_reported,
        diagnosis: inst.diagnosis,
        work_performed: inst.work_performed,
        priority: inst.priority,
        paid_amount: inst.paid_amount,
        payment_method: inst.payment_method,
        payment_status: 'deposit',
        warranty_days: inst.warranty_days
      })
      const repairId = repairRes.data?.id || repairRes.id

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
    language_preference: 'es'
  }
  instruments.value = [createInstrument()]
  invalidFields.value = new Set()
  existingClientId.value = null
  useExistingClient.value = false
  reloadCodes()
}

onMounted(async () => {
  await Promise.all([fetchNextClientCode(), fetchClients()])
})
</script>

<style scoped>
.sheet-header {
  position: sticky;
  top: 0;
  z-index: 5;
  background: #f6f2ea;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(62, 60, 56, 0.2);
}

.sheet-context {
  display: flex;
  gap: 1.5rem;
  font-size: 0.95rem;
  color: #5a5652;
  margin-top: 0.35rem;
}
</style>

<style scoped>
.intake-sheet {
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
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
  color: #6b7280;
}
.code-block {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  text-align: right;
  min-width: 220px;
}
.code-label {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.code-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #c2410c;
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
  border-top: 1px solid #e5e7eb;
}
.instrument-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 1rem;
  margin-top: 1rem;
  background: #fcfcfc;
}
.instrument-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.code-small {
  font-size: 0.85rem;
  color: #6b7280;
}
.materials-section {
  margin-top: 1rem;
  padding-top: 0.5rem;
  border-top: 1px dashed #e5e7eb;
}
.sheet-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}
</style>
