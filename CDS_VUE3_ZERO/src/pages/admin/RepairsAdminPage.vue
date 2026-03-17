<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Reparaciones</h1>
        <p>Flujo de OT activas, filtros y acceso al detalle tecnico.</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" :disabled="loading" @click="loadRepairs">
          {{ loading ? 'Actualizando...' : 'Actualizar' }}
        </button>
        <button class="btn-primary" :disabled="loading" @click="toggleForm">
          {{ showForm ? 'Cancelar' : 'Nueva reparacion' }}
        </button>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section class="panel-card filters-panel">
      <label>
        <span>Buscar</span>
        <input v-model.trim="searchQuery" type="search" placeholder="OT, cliente, instrumento o estado" />
      </label>
      <label>
        <span>Estado</span>
        <select v-model="statusFilter">
          <option value="">Todos</option>
          <option v-for="status in statusOptions" :key="status" :value="status">{{ status }}</option>
        </select>
      </label>
    </section>

    <section v-if="showForm" class="panel-card">
      <h2>Crear reparacion</h2>
      <div class="form-grid two-cols">
        <label>
          <span>Cliente *</span>
          <select v-model="form.client_id">
            <option value="">Seleccionar</option>
            <option v-for="client in clients" :key="client.id" :value="client.id">
              {{ client.client_code || `#${client.id}` }} - {{ client.name }}
            </option>
          </select>
        </label>
        <label><span>Modelo *</span><input v-model.trim="form.model" type="text" placeholder="Ej: Korg MS-20" /></label>
        <label class="full"><span>Problema reportado *</span><textarea v-model.trim="form.problem_reported" rows="3"></textarea></label>
        <label><span>Prioridad</span><select v-model.number="form.priority"><option :value="1">Alta</option><option :value="2">Normal</option><option :value="3">Baja</option></select></label>
        <label><span>Abono (CLP)</span><input v-model.number="form.paid_amount" type="number" min="0" /></label>
        <label>
          <span>Medio de pago</span>
          <select v-model="form.payment_method">
            <option v-for="method in paymentMethods" :key="method.value" :value="method.value">{{ method.label }}</option>
          </select>
        </label>
      </div>
      <div class="panel-actions">
        <button class="btn-primary" :disabled="loading" @click="createRepair">
          {{ loading ? 'Guardando...' : 'Crear OT' }}
        </button>
      </div>
    </section>

    <section class="panel-card">
      <h2>Listado ({{ repairs.length }})</h2>
      <p v-if="repairs.length === 0" class="empty-state">No hay reparaciones para el filtro actual.</p>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>OT</th>
              <th>Cliente</th>
              <th>Instrumento</th>
              <th>Estado</th>
              <th>Creada</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="repair in repairs" :key="repair.id">
              <td>{{ repair.repair_code || repair.repair_number || `#${repair.id}` }}</td>
              <td>
                <div class="cell-stack">
                  <strong>{{ repair.client_name || 'Sin cliente' }}</strong>
                  <small>{{ repair.client_code || '—' }}</small>
                </div>
              </td>
              <td>{{ repair.device_model || '—' }}</td>
              <td>{{ repair.status || '—' }}</td>
              <td>{{ formatDate(repair.created_at) }}</td>
              <td>
                <div class="row-actions">
                  <button class="btn-secondary" :disabled="loading" @click="goToRepair(repair)">Abrir</button>
                  <button class="btn-danger" :disabled="loading" @click="deleteRepair(repair)">Eliminar</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useRepairsAdminPage } from '@/composables/useRepairsAdminPage'

const {
  repairs,
  clients,
  loading,
  error,
  searchQuery,
  statusFilter,
  statusOptions,
  showForm,
  form,
  paymentMethods,
  formatDate,
  loadRepairs,
  toggleForm,
  goToRepair,
  createRepair,
  deleteRepair
} = useRepairsAdminPage()
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped>
.filters-panel { grid-template-columns: repeat(1, minmax(0, 1fr)); }
@media (min-width: 900px) { .filters-panel { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
