<template>
  <WizardShell
    :steps="steps"
    :current-index="stepIndex"
    :can-continue="canContinue"
    @next="onNext"
    @prev="onPrev"
  >
    <template #default>
      <div v-if="stepIndex === 0">
        <h4>Categoría</h4>
        <select v-model.number="form.category_id" class="form-select">
          <option :value="null">Selecciona categoría</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>

      <div v-else-if="stepIndex === 1">
        <h4>SKU</h4>
        <div class="row g-2">
          <div class="col-md-4">
            <label class="form-label">Prefijo</label>
            <input v-model="skuPrefix" class="form-control" />
          </div>
          <div class="col-md-8">
            <label class="form-label">Código (ej: 104, 1N4148, NE555)</label>
            <input v-model="skuCode" class="form-control" />
          </div>
        </div>
        <div class="mt-2 text-muted">
          SKU sugerido: <strong>{{ composedSku }}</strong>
        </div>
      </div>

      <div v-else-if="stepIndex === 2">
        <h4>Datos básicos</h4>
        <div class="row g-2">
          <div class="col-md-8">
            <label class="form-label">Nombre *</label>
            <input v-model="form.name" class="form-control" placeholder="Ej: Capacitor cerámico 104" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Stock inicial</label>
            <input v-model.number="form.quantity" type="number" min="0" class="form-control" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Precio (centavos)</label>
            <input v-model.number="form.price" type="number" min="0" class="form-control" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Stock mínimo</label>
            <input v-model.number="form.min_quantity" type="number" min="0" class="form-control" />
          </div>
          <div class="col-12">
            <label class="form-label">Descripción</label>
            <textarea v-model="form.description" class="form-control" rows="2"></textarea>
          </div>
        </div>
        <div class="mt-3 d-flex justify-content-end">
          <button class="btn btn-primary btn-sm" :disabled="saving" @click="submit">
            {{ saving ? 'Guardando...' : 'Guardar inventario' }}
          </button>
        </div>
      </div>
    </template>
  </WizardShell>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/services/api'
import WizardShell from '@/vue/components/admin/wizard/WizardShell.vue'

const emit = defineEmits(['completed'])

const steps = [
  { key: 'category', title: 'Categoría' },
  { key: 'sku', title: 'SKU' },
  { key: 'data', title: 'Datos' }
]

const stepIndex = ref(0)
const saving = ref(false)
const categories = ref([])
const form = ref({
  category_id: null,
  sku: '',
  name: '',
  description: '',
  price: 0,
  quantity: 0,
  min_quantity: 5
})
const skuPrefix = ref('CAP')
const skuCode = ref('')

const composedSku = computed(() => {
  if (!skuPrefix.value || !skuCode.value) return ''
  return `${skuPrefix.value}-${skuCode.value}`.toUpperCase()
})

const canContinue = computed(() => {
  if (stepIndex.value === 0) return !!form.value.category_id
  if (stepIndex.value === 1) return !!composedSku.value
  if (stepIndex.value === 2) return !!form.value.name
  return true
})

const onNext = () => {
  if (stepIndex.value === 1) {
    form.value.sku = composedSku.value
  }
  if (stepIndex.value < steps.length - 1) stepIndex.value += 1
}

const onPrev = () => {
  if (stepIndex.value > 0) stepIndex.value -= 1
}

const loadCategories = async () => {
  try {
    const res = await api.get('/categories')
    categories.value = res.data || res || []
  } catch (e) {
    categories.value = []
  }
}

const submit = async () => {
  if (!form.value.sku || !form.value.name || !form.value.category_id) {
    alert('Completa SKU, nombre y categoría')
    return
  }
  saving.value = true
  try {
    await api.post('/inventory', form.value)
    emit('completed')
    form.value = {
      category_id: null,
      sku: '',
      name: '',
      description: '',
      price: 0,
      quantity: 0,
      min_quantity: 5
    }
    skuPrefix.value = 'CAP'
    skuCode.value = ''
    stepIndex.value = 0
  } catch (e) {
    console.error(e)
    alert('Error guardando inventario')
  } finally {
    saving.value = false
  }
}

onMounted(loadCategories)
</script>
