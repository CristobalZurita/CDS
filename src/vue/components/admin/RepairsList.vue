<template>
  <section class="admin-section">
    <div class="admin-section-header">
      <h2 class="admin-section-title">Reparaciones</h2>
      <div class="d-flex gap-2 align-items-center">
        <input
          v-model="searchQuery"
          type="search"
          class="form-control form-control-sm"
          placeholder="Buscar OT, cliente o instrumento..."
        />
        <button class="admin-btn admin-btn-outline" @click="fetchRepairs">Actualizar</button>
      </div>
    </div>
    <table class="admin-table">
      <thead>
        <tr>
          <th>OT</th>
          <th>Cliente</th>
          <th>Instrumento</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="repair in filteredRepairs" :key="repair.id">
          <td>{{ repair.repair_code || repair.repair_number || repair.id }}</td>
          <td>
            <div class="cell-stack">
              <strong>{{ repair.client_name || 'Sin cliente' }}</strong>
              <small v-if="repair.client_code" class="text-muted">{{ repair.client_code }}</small>
            </div>
          </td>
          <td>{{ repair.device_model || 'Sin modelo' }}</td>
          <td>{{ repair.status }}</td>
          <td>
            <button class="admin-btn admin-btn-outline" @click="editRepair(repair)">Editar</button>
            <button class="admin-btn admin-btn-primary" @click="deleteRepair(repair.id)">Borrar</button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
<script setup>
import { useRepairs } from '@/composables/useRepairs'
import { useRouter } from 'vue-router'
import { onMounted, ref, computed } from 'vue'
const { repairs, fetchRepairs, deleteRepair } = useRepairs()
const router = useRouter()
const searchQuery = ref('')

const filteredRepairs = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return repairs
  return (repairs || []).filter((repair) => {
    const haystack = [
      repair.repair_code,
      repair.repair_number,
      repair.client_name,
      repair.client_code,
      repair.device_model
    ].filter(Boolean).join(' ').toLowerCase()
    return haystack.includes(q)
  })
})

function editRepair(repair) {
  router.push(`/admin/repairs/${repair.id}`)
}

onMounted(() => {
  fetchRepairs()
})
</script>
<style scoped>
.cell-stack {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
</style>
