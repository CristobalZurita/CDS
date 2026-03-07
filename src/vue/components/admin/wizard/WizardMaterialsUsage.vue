<template>
  <div>
    <div class="mb-3">
      <label class="form-label">Selecciona OT</label>
      <select v-model.number="selectedRepairId" class="form-select">
        <option :value="null">Selecciona OT</option>
        <option v-for="r in repairs" :key="r.id" :value="r.id">
          {{ r.repair_code || r.repair_number || ('OT #' + r.id) }} - {{ r.client_name || 'Sin cliente' }}
        </option>
      </select>
    </div>
    <div v-if="selectedRepairId">
      <RepairComponentsManager :repair-id="selectedRepairId" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import RepairComponentsManager from '@/vue/components/admin/repair/RepairComponentsManager.vue'

const repairs = ref([])
const selectedRepairId = ref(null)

const loadRepairs = async () => {
  try {
    const res = await api.get('/repairs/')
    repairs.value = res.data || res || []
  } catch {
    repairs.value = []
  }
}

onMounted(loadRepairs)
</script>
