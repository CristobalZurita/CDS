<template>
  <AdminLayout title="Archivo" subtitle="OT archivadas y cerradas">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1 class="h4">Archivo</h1>
      <button class="btn btn-sm btn-outline-secondary" @click="load">Actualizar</button>
    </div>

    <div class="mb-3">
      <input v-model="searchQuery" class="form-control" placeholder="Buscar por cliente, OT, instrumento..." />
    </div>

    <div class="card p-3">
      <table class="table table-sm">
        <thead>
          <tr>
            <th>OT</th>
            <th>Cliente</th>
            <th>Instrumento</th>
            <th>Estado</th>
            <th>Archivado</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filtered" :key="item.id">
            <td>{{ item.repair_code || item.repair_number }}</td>
            <td>{{ item.client_name || '—' }}</td>
            <td>{{ item.device_model || '—' }}</td>
            <td>{{ item.status || '—' }}</td>
            <td>{{ formatDate(item.archived_at) }}</td>
            <td class="text-end">
              <button class="btn btn-sm btn-outline-primary" @click="goToRepair(item)">Ver</button>
            </td>
          </tr>
          <tr v-if="filtered.length === 0">
            <td colspan="6" class="text-muted">Sin OT archivadas.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'

const router = useRouter()
const items = ref([])
const searchQuery = ref('')

const load = async () => {
  const res = await api.get('/repairs/archived').catch(() => ({ data: [] }))
  items.value = res.data || res || []
}

const filtered = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return items.value
  return items.value.filter((item) => {
    const hay = [
      item.repair_code,
      item.repair_number,
      item.client_name,
      item.device_model
    ].filter(Boolean).join(' ').toLowerCase()
    return hay.includes(q)
  })
})

const goToRepair = (item) => {
  router.push(`/admin/repairs/${item.id}`)
}

const formatDate = (val) => {
  if (!val) return '—'
  const d = new Date(val)
  return isNaN(d.getTime()) ? val : d.toLocaleDateString('es-CL')
}

onMounted(load)
</script>
