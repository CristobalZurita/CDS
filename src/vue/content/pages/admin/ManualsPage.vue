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
