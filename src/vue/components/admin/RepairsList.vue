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
    <table class="admin-table admin-table--stack">
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
          <td data-label="OT">{{ repair.repair_code || repair.repair_number || repair.id }}</td>
          <td data-label="Cliente">
            <div class="cell-stack">
              <strong>{{ repair.client_name || 'Sin cliente' }}</strong>
              <small v-if="repair.client_code" class="text-muted">{{ repair.client_code }}</small>
            </div>
          </td>
          <td data-label="Instrumento">{{ repair.device_model || 'Sin modelo' }}</td>
          <td data-label="Estado">{{ repair.status }}</td>
          <td data-label="Acciones">
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
<style scoped lang="scss">
@import "/src/scss/_theming.scss";

.cell-stack {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

@include media-breakpoint-down(md) {
  .admin-table--stack,
  .admin-table--stack thead,
  .admin-table--stack tbody,
  .admin-table--stack tr,
  .admin-table--stack th,
  .admin-table--stack td {
    display: block;
    width: 100%;
  }

  .admin-table--stack thead {
    display: none;
  }

  .admin-table--stack tr {
    padding: 1rem;
    margin-bottom: 0.75rem;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 8px 16px rgba(62, 60, 56, 0.12);
  }

  .admin-table--stack td {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.35rem 0;
    font-size: 1rem;
  }

  .admin-table--stack td::before {
    content: attr(data-label);
    font-weight: 600;
    color: $text-muted;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    font-size: 0.8rem;
  }
}
</style>
