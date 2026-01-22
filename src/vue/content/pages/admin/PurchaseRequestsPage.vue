<template>
  <AdminLayout title="Compras sugeridas" subtitle="Carrito interno por cliente/OT">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1 class="h4">Solicitudes de compra</h1>
      <div>
        <button class="btn btn-sm btn-success me-2" @click="showWizard = !showWizard">
          {{ showWizard ? 'Cerrar' : 'Nueva solicitud' }}
        </button>
        <button class="btn btn-sm btn-outline-secondary" @click="loadRequests">Actualizar</button>
      </div>
    </div>

    <div v-if="showWizard" class="card p-3 mb-3">
      <WizardPurchaseRequest @completed="onCompleted" />
    </div>

    <div class="card p-3">
      <table class="table table-sm">
        <thead>
          <tr>
            <th>ID</th>
            <th>Estado</th>
            <th>Items</th>
            <th>Notas</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="req in requests" :key="req.id">
            <td>#{{ req.id }}</td>
            <td>{{ req.status }}</td>
            <td>{{ req.items?.length || 0 }}</td>
            <td>{{ req.notes || '—' }}</td>
          </tr>
          <tr v-if="requests.length === 0">
            <td colspan="4" class="text-muted">Sin solicitudes registradas.</td>
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
import WizardPurchaseRequest from '@/vue/components/admin/wizard/WizardPurchaseRequest.vue'

const requests = ref([])
const showWizard = ref(false)

const loadRequests = async () => {
  const res = await api.get('/purchase-requests/').catch(() => ({ data: [] }))
  requests.value = res.data || res || []
}

const onCompleted = () => {
  showWizard.value = false
  loadRequests()
}

onMounted(loadRequests)
</script>
