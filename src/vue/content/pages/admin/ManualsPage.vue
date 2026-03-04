<template>
  <AdminLayout title="Manuales" subtitle="Documentos técnicos por modelo">
    <section class="admin-page">
      <header class="admin-page__header">
        <h1 class="admin-page__title">Manuales y esquemas</h1>

        <div class="admin-page__actions">
          <button
            type="button"
            class="admin-page__button admin-page__button--success"
            data-testid="manuals-new"
            @click="showWizard = !showWizard"
          >
            {{ showWizard ? 'Cerrar' : 'Nuevo manual' }}
          </button>
          <button
            type="button"
            class="admin-page__button admin-page__button--secondary"
            data-testid="manuals-refresh"
            @click="loadManuals"
          >
            Actualizar
          </button>
        </div>
      </header>

      <section v-if="showWizard" class="admin-page__panel" data-testid="manuals-wizard">
        <WizardManualUpload @completed="onCompleted" />
      </section>

      <section class="admin-page__panel">
        <div class="admin-page__table-wrap">
          <table class="admin-page__table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Título</th>
                <th>Fuente</th>
                <th>Link</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="manual in manuals" :key="manual.id" data-testid="manual-row">
                <td>#{{ manual.id }}</td>
                <td>
                  <template v-if="editingId === manual.id">
                    <input v-model="draft.title" class="admin-page__input" data-testid="manual-title-input" />
                  </template>
                  <template v-else>
                    {{ manual.title }}
                  </template>
                </td>
                <td>
                  <template v-if="editingId === manual.id">
                    <select v-model="draft.source" class="admin-page__select" data-testid="manual-source-select">
                      <option value="internal">internal</option>
                      <option value="external">external</option>
                    </select>
                  </template>
                  <template v-else>
                    {{ manual.source }}
                  </template>
                </td>
                <td>
                  <template v-if="editingId === manual.id">
                    <input
                      v-model="draft.url"
                      class="admin-page__input"
                      data-testid="manual-url-input"
                      placeholder="https://..."
                    />
                  </template>
                  <template v-else>
                    <a v-if="manual.url" :href="manual.url" data-testid="manual-link" target="_blank" rel="noreferrer">URL</a>
                    <span v-else-if="manual.file_path">Archivo</span>
                    <span v-else>—</span>
                  </template>
                </td>
                <td>
                  <div class="admin-page__cell-actions">
                    <template v-if="editingId === manual.id">
                      <button
                        type="button"
                        class="admin-page__button admin-page__button--primary"
                        data-testid="manual-save"
                        @click="saveManual(manual)"
                      >
                        Guardar
                      </button>
                      <button
                        type="button"
                        class="admin-page__button admin-page__button--ghost"
                        data-testid="manual-cancel"
                        @click="cancelEdit"
                      >
                        Cancelar
                      </button>
                    </template>
                    <template v-else>
                      <button
                        type="button"
                        class="admin-page__button admin-page__button--primary"
                        data-testid="manual-edit"
                        @click="startEdit(manual)"
                      >
                        Editar
                      </button>
                      <button
                        type="button"
                        class="admin-page__button admin-page__button--danger"
                        data-testid="manual-delete"
                        @click="deleteManual(manual)"
                      >
                        Eliminar
                      </button>
                    </template>
                  </div>
                </td>
              </tr>
              <tr v-if="manuals.length === 0">
                <td colspan="5" class="admin-page__empty">Sin manuales registrados.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </section>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'
import WizardManualUpload from '@/vue/components/admin/wizard/WizardManualUpload.vue'

const manuals = ref([])
const showWizard = ref(false)
const editingId = ref(null)
const draft = ref({
  title: '',
  source: 'internal',
  url: ''
})

const loadManuals = async () => {
  const res = await api.get('/manuals/').catch(() => ({ data: [] }))
  manuals.value = res.data || res || []
}

const startEdit = (manual) => {
  editingId.value = manual.id
  draft.value = {
    title: manual.title || '',
    source: manual.source || 'internal',
    url: manual.url || ''
  }
}

const cancelEdit = () => {
  editingId.value = null
  draft.value = {
    title: '',
    source: 'internal',
    url: ''
  }
}

const saveManual = async (manual) => {
  await api.patch(`/manuals/${manual.id}`, {
    title: draft.value.title,
    source: draft.value.source,
    url: draft.value.url || null
  }).catch(() => null)
  cancelEdit()
  loadManuals()
}

const deleteManual = async (manual) => {
  if (!confirm(`¿Eliminar manual #${manual.id}?`)) return
  await api.delete(`/manuals/${manual.id}`).catch(() => null)
  loadManuals()
}

const onCompleted = () => {
  showWizard.value = false
  loadManuals()
}

onMounted(loadManuals)
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

.admin-page__actions,
.admin-page__cell-actions {
  display: flex;
  gap: var(--spacer-sm);
  flex-wrap: wrap;
}

.admin-page__panel {
  padding: var(--spacer-md);
  background: var(--color-white);
  border: 1px solid var(--color-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
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

.admin-page__input,
.admin-page__select {
  width: 100%;
  min-height: 40px;
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--color-light);
  border-radius: var(--radius-sm);
  background: var(--color-white);
  color: var(--color-dark);
  font-size: var(--text-sm);
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

.admin-page__button--success,
.admin-page__button--primary {
  background: var(--color-primary);
}

.admin-page__button--secondary {
  background: var(--color-dark);
}

.admin-page__button--danger {
  background: var(--color-danger);
}

.admin-page__button--ghost {
  background: var(--color-light);
  color: var(--color-dark);
}

@include media-breakpoint-down(md) {
  .admin-page__header,
  .admin-page__actions,
  .admin-page__cell-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .admin-page__button {
    width: 100%;
  }
}
</style>
