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
                  <div class="admin-page__actions">
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

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.admin-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-md);
}

.admin-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacer-md);
  flex-wrap: wrap;
}

.admin-page__title {
  margin: 0;
  color: var(--color-dark);
  font-size: var(--text-xl);
  font-weight: 700;
}

.admin-page__search-panel,
.admin-page__panel {
  padding: var(--spacer-md);
  background: var(--color-white);
  border: 1px solid var(--color-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.admin-page__input {
  width: 100%;
  min-height: 44px;
  padding: 0.75rem 0.875rem;
  border: 1px solid var(--color-light);
  border-radius: var(--radius-md);
  background: var(--color-white);
  color: var(--color-dark);
  font-size: var(--text-base);
}

.admin-page__table-wrap {
  width: 100%;
  overflow-x: auto;
}

.admin-page__table {
  width: 100%;
  border-collapse: collapse;
}

.admin-page__table th,
.admin-page__table td {
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-light);
  text-align: left;
  vertical-align: middle;
  color: var(--color-dark);
  font-size: var(--text-sm);
}

.admin-page__table th {
  font-weight: 700;
}

.admin-page__empty {
  color: var(--color-dark);
  opacity: 0.7;
}

.admin-page__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacer-sm);
  flex-wrap: wrap;
}

.admin-page__button {
  min-height: 40px;
  padding: 0.65rem 0.9rem;
  border: 0;
  border-radius: var(--radius-sm);
  color: var(--color-white);
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-base);
}

.admin-page__button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.admin-page__button--secondary {
  background: var(--color-dark);
}

.admin-page__button--primary {
  background: var(--color-primary);
}

.admin-page__button--ghost {
  background: var(--color-light);
  color: var(--color-dark);
}

@include media-breakpoint-down(md) {
  .admin-page__header,
  .admin-page__actions {
    flex-direction: column;
    align-items: stretch;
  }

  .admin-page__button {
    width: 100%;
  }
}
</style>
