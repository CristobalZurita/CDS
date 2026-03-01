<template>
  <AdminLayout title="Manuales" subtitle="Documentos técnicos por modelo">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1 class="h4">Manuales y esquemas</h1>
      <div>
        <button class="btn btn-sm btn-success me-2" data-testid="manuals-new" @click="showWizard = !showWizard">
          {{ showWizard ? 'Cerrar' : 'Nuevo manual' }}
        </button>
        <button class="btn btn-sm btn-outline-secondary" data-testid="manuals-refresh" @click="loadManuals">Actualizar</button>
      </div>
    </div>

    <div v-if="showWizard" class="card p-3 mb-3" data-testid="manuals-wizard">
      <WizardManualUpload @completed="onCompleted" />
    </div>

    <div class="card p-3">
      <table class="table table-sm">
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
                <input v-model="draft.title" class="form-control form-control-sm" data-testid="manual-title-input" />
              </template>
              <template v-else>
                {{ manual.title }}
              </template>
            </td>
            <td>
              <template v-if="editingId === manual.id">
                <select v-model="draft.source" class="form-select form-select-sm" data-testid="manual-source-select">
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
                <input v-model="draft.url" class="form-control form-control-sm" data-testid="manual-url-input" placeholder="https://..." />
              </template>
              <template v-else>
                <a v-if="manual.url" :href="manual.url" data-testid="manual-link" target="_blank" rel="noreferrer">URL</a>
                <span v-else-if="manual.file_path">Archivo</span>
                <span v-else>—</span>
              </template>
            </td>
            <td>
              <div class="d-flex gap-2">
                <template v-if="editingId === manual.id">
                  <button class="btn btn-sm btn-primary" data-testid="manual-save" @click="saveManual(manual)">Guardar</button>
                  <button class="btn btn-sm btn-outline-secondary" data-testid="manual-cancel" @click="cancelEdit">Cancelar</button>
                </template>
                <template v-else>
                  <button class="btn btn-sm btn-outline-primary" data-testid="manual-edit" @click="startEdit(manual)">Editar</button>
                  <button class="btn btn-sm btn-outline-danger" data-testid="manual-delete" @click="deleteManual(manual)">Eliminar</button>
                </template>
              </div>
            </td>
          </tr>
          <tr v-if="manuals.length === 0">
            <td colspan="5" class="text-muted">Sin manuales registrados.</td>
          </tr>
        </tbody>
      </table>
    </div>
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
