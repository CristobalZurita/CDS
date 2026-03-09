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

<style scoped>
.admin-page { padding: 1rem; display: grid; gap: 1rem; }
.admin-header, .panel-card { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); }
.admin-header { padding: .9rem; display: flex; gap: .75rem; justify-content: space-between; align-items: center; flex-wrap: wrap; }
.admin-header h1 { margin: 0; font-size: var(--cds-text-3xl); }
.admin-header p { margin: .3rem 0 0; color: var(--cds-text-muted); }
.header-actions { display: flex; gap: .45rem; flex-wrap: wrap; }
.btn-primary, .btn-secondary, .btn-danger { min-height: 44px; padding: .65rem .9rem; border-radius: .55rem; border: 1px solid transparent; font-size: var(--cds-text-base); }
.btn-primary { border-color: var(--cds-primary); background: var(--cds-primary); color: var(--cds-white); }
.btn-secondary { border-color: color-mix(in srgb, var(--cds-light) 65%, white); background: var(--cds-white); color: var(--cds-text-normal); }
.btn-danger { border-color: #dc2626; background: #dc2626; color: #fff; }
.admin-error { margin: 0; border: 1px solid #fecaca; background: #fef2f2; color: #991b1b; border-radius: .65rem; padding: .75rem; }
.panel-card { padding: .9rem; display: grid; gap: .7rem; }
.panel-card h2 { margin: 0; font-size: var(--cds-text-xl); }
.filters-panel { grid-template-columns: repeat(1, minmax(0, 1fr)); }
.filters-panel label { display: grid; gap: .3rem; }
.filters-panel span, .form-grid span { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.filters-panel input, .filters-panel select, .form-grid input, .form-grid textarea, .form-grid select { min-height: 44px; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); border-radius: .55rem; padding: .65rem .75rem; font-size: var(--cds-text-base); }
.form-grid { display: grid; gap: .6rem; grid-template-columns: 1fr; }
.form-grid.two-cols { grid-template-columns: 1fr; }
.form-grid label { display: grid; gap: .3rem; }
.form-grid textarea { min-height: 92px; resize: vertical; }
.form-grid .full { grid-column: 1 / -1; }
.panel-actions { display: flex; justify-content: flex-end; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: .55rem; border-bottom: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); vertical-align: top; }
th { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.cell-stack { display: grid; gap: .15rem; }
.cell-stack small { color: var(--cds-text-muted); }
.row-actions { display: flex; gap: .45rem; flex-wrap: wrap; }
.empty-state { margin: 0; border: 1px dashed color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .65rem; padding: .8rem; color: var(--cds-text-muted); }
@media (min-width: 900px) {
  .filters-panel { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .form-grid.two-cols { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
