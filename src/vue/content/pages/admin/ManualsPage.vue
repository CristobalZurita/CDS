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
          </tr>
        </thead>
        <tbody>
          <tr v-for="manual in manuals" :key="manual.id">
            <td>#{{ manual.id }}</td>
            <td>{{ manual.title }}</td>
            <td>{{ manual.source }}</td>
            <td>
              <a v-if="manual.url" :href="manual.url" target="_blank" rel="noreferrer">URL</a>
              <span v-else-if="manual.file_path">Archivo</span>
              <span v-else>—</span>
            </td>
          </tr>
          <tr v-if="manuals.length === 0">
            <td colspan="4" class="text-muted">Sin manuales registrados.</td>
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

const loadManuals = async () => {
  const res = await api.get('/manuals/').catch(() => ({ data: [] }))
  manuals.value = res.data || res || []
}

const onCompleted = () => {
  showWizard.value = false
  loadManuals()
}

onMounted(loadManuals)
</script>
