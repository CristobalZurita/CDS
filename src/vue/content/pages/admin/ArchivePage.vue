<template>
  <AdminLayout title="Archivo" subtitle="OT archivadas y cerradas">
    <section class="admin-page">
      <header class="admin-page__header">
        <h1 class="admin-page__title">Archivo</h1>
        <button
          type="button"
          class="admin-page__button admin-page__button--secondary"
          data-testid="archive-refresh"
          @click="load"
        >
          Actualizar
        </button>
      </header>

      <section class="admin-page__search-panel">
        <input
          v-model="searchQuery"
          class="admin-page__input"
          data-testid="archive-search"
          placeholder="Buscar por cliente, OT, instrumento..."
        />
      </section>

      <section class="admin-page__panel" data-testid="archive-table">
        <div class="admin-page__table-wrap">
          <table class="admin-page__table">
            <thead>
              <tr>
                <th>OT</th>
                <th>Cliente</th>
                <th>Instrumento</th>
                <th>Estado</th>
                <th>Archivado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in filtered" :key="item.id">
                <td>{{ item.repair_code || item.repair_number }}</td>
                <td>{{ item.client_name || '—' }}</td>
                <td>{{ item.device_model || '—' }}</td>
                <td>{{ item.status || '—' }}</td>
                <td>{{ formatDate(item.archived_at) }}</td>
                <td>
                  <div class="admin-page__cell-actions">
                    <button
                      type="button"
                      class="admin-page__button admin-page__button--ghost"
                      @click="reactivate(item)"
                    >
                      Reactivar
                    </button>
                    <button
                      type="button"
                      class="admin-page__button admin-page__button--primary"
                      @click="goToRepair(item)"
                    >
                      Ver
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="filtered.length === 0">
                <td colspan="6" class="admin-page__empty">Sin OT archivadas.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </section>
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

const reactivate = async (item) => {
  const ok = window.confirm('¿Reactivar esta OT? Volverá a Ingreso.')
  if (!ok) return
  await api.post(`/repairs/${item.id}/reactivate`).catch(() => null)
  load()
}

const formatDate = (val) => {
  if (!val) return '—'
  const d = new Date(val)
  return isNaN(d.getTime()) ? val : d.toLocaleDateString('es-CL')
}

onMounted(load)
</script>

<style scoped>
.admin-page__input {
  min-height: 44px;
  padding: 0.75rem 0.875rem;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
}
</style>
