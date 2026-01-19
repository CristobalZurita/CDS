<template>
  <section class="admin-section">
    <div class="admin-section-header">
      <h2 class="admin-section-title">Reparaciones</h2>
      <button class="admin-btn admin-btn-outline" @click="fetchRepairs">Actualizar</button>
    </div>
    <table class="admin-table">
      <thead>
        <tr>
          <th>Título</th>
          <th>Cliente</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="repair in repairs" :key="repair.id">
          <td>{{ repair.title }}</td>
          <td>{{ repair.client_id }}</td>
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
import { onMounted } from 'vue'
const { repairs, fetchRepairs, deleteRepair } = useRepairs()
const router = useRouter()

function editRepair(repair) {
  router.push(`/admin/repairs/${repair.id}`)
}

onMounted(() => {
  fetchRepairs()
})
</script>
