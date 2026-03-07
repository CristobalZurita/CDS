<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Clientes</h1>
        <p>Gestion de clientes, dispositivos y ordenes de trabajo.</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" :disabled="loading" @click="loadClients">
          {{ loading ? 'Actualizando...' : 'Actualizar' }}
        </button>
        <button class="btn-primary" :disabled="loading" @click="toggleCreateForm">
          {{ showCreateForm ? 'Cerrar ingreso' : 'Nuevo cliente' }}
        </button>
        <button class="btn-secondary" :disabled="!selectedClient" @click="toggleEditForm">
          {{ showEditForm ? 'Cerrar edicion' : 'Editar cliente' }}
        </button>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section v-if="showCreateForm" class="panel-card">
      <h2>Nuevo cliente</h2>
      <div class="form-grid two-cols">
        <label><span>Nombre *</span><input v-model.trim="createForm.name" type="text" /></label>
        <label><span>Email</span><input v-model.trim="createForm.email" type="email" /></label>
        <label><span>Telefono</span><input v-model.trim="createForm.phone" type="text" /></label>
        <label><span>Telefono alterno</span><input v-model.trim="createForm.phone_alt" type="text" /></label>
        <label><span>Ciudad</span><input v-model.trim="createForm.city" type="text" /></label>
        <label><span>Region</span><input v-model.trim="createForm.region" type="text" /></label>
        <label><span>Pais</span><input v-model.trim="createForm.country" type="text" /></label>
        <label class="full"><span>Direccion</span><input v-model.trim="createForm.address" type="text" /></label>
        <label class="full"><span>Notas</span><textarea v-model.trim="createForm.notes" rows="3"></textarea></label>
      </div>
      <div class="panel-actions">
        <button class="btn-primary" :disabled="loading" @click="createClient">
          {{ loading ? 'Guardando...' : 'Guardar cliente' }}
        </button>
      </div>
    </section>

    <section class="panel-card">
      <div class="toolbar">
        <label class="full">
          <span>Buscar cliente</span>
          <input v-model.trim="searchQuery" type="search" placeholder="Nombre, codigo, email o telefono" />
        </label>
      </div>

      <div class="split-grid">
        <aside class="list-panel">
          <h3>Listado</h3>
          <p v-if="filteredClients.length === 0" class="empty-state">Sin clientes para el filtro actual.</p>
          <ul v-else class="list-reset">
            <li
              v-for="client in filteredClients"
              :key="client.id"
              :class="['list-item', { active: selectedClientId === client.id }]"
              @click="selectClient(client)"
            >
              <div class="item-head">
                <strong>{{ client.name || `Cliente #${client.id}` }}</strong>
                <span class="chip">{{ client.client_code || `#${client.id}` }}</span>
              </div>
              <small>{{ client.email || 'Sin email' }}</small>
            </li>
          </ul>
        </aside>

        <article class="detail-panel">
          <template v-if="selectedClient">
            <div class="detail-head">
              <div>
                <h3>{{ selectedClient.name }}</h3>
                <p>{{ selectedClient.client_code }} · {{ selectedClient.email || 'Sin email' }}</p>
              </div>
              <div class="header-actions">
                <button class="btn-secondary" :disabled="contextLoading" @click="toggleDeviceForm">
                  {{ showDeviceForm ? 'Cerrar dispositivo' : 'Agregar dispositivo' }}
                </button>
                <button class="btn-secondary" :disabled="contextLoading" @click="toggleRepairForm">
                  {{ showRepairForm ? 'Cerrar OT' : 'Crear OT' }}
                </button>
                <button class="btn-danger" :disabled="loading" @click="deleteSelectedClient">Eliminar</button>
              </div>
            </div>

            <div class="summary-grid">
              <article class="summary-card">
                <span>Telefono</span>
                <strong>{{ selectedClient.phone || '—' }}</strong>
              </article>
              <article class="summary-card">
                <span>Reparaciones</span>
                <strong>{{ selectedClient.total_repairs }}</strong>
              </article>
              <article class="summary-card">
                <span>Total gastado</span>
                <strong>{{ new Intl.NumberFormat('es-CL').format(selectedClient.total_spent) }}</strong>
              </article>
            </div>

            <section v-if="showEditForm" class="panel-nested">
              <h4>Editar cliente</h4>
              <div class="form-grid two-cols">
                <label><span>Nombre *</span><input v-model.trim="editForm.name" type="text" /></label>
                <label><span>Email</span><input v-model.trim="editForm.email" type="email" /></label>
                <label><span>Telefono</span><input v-model.trim="editForm.phone" type="text" /></label>
                <label><span>Telefono alterno</span><input v-model.trim="editForm.phone_alt" type="text" /></label>
                <label><span>Ciudad</span><input v-model.trim="editForm.city" type="text" /></label>
                <label><span>Region</span><input v-model.trim="editForm.region" type="text" /></label>
                <label><span>Pais</span><input v-model.trim="editForm.country" type="text" /></label>
                <label class="full"><span>Direccion</span><input v-model.trim="editForm.address" type="text" /></label>
                <label class="full"><span>Notas</span><textarea v-model.trim="editForm.notes" rows="3"></textarea></label>
                <label class="full"><span>Notas internas</span><textarea v-model.trim="editForm.internal_notes" rows="3"></textarea></label>
              </div>
              <div class="panel-actions">
                <button class="btn-primary" :disabled="loading" @click="updateSelectedClient">Guardar cambios</button>
              </div>
            </section>

            <section v-if="showDeviceForm" class="panel-nested">
              <h4>Nuevo dispositivo</h4>
              <div class="form-grid two-cols">
                <label><span>Modelo *</span><input v-model.trim="deviceForm.model" type="text" /></label>
                <label><span>Marca</span><input v-model.trim="deviceForm.brand_other" type="text" /></label>
                <label><span>Serial</span><input v-model.trim="deviceForm.serial_number" type="text" /></label>
                <label class="full"><span>Descripcion</span><textarea v-model.trim="deviceForm.description" rows="2"></textarea></label>
                <label class="full"><span>Condicion</span><textarea v-model.trim="deviceForm.condition_notes" rows="2"></textarea></label>
              </div>
              <div class="panel-actions">
                <button class="btn-primary" :disabled="contextLoading" @click="createDeviceForSelectedClient">
                  {{ contextLoading ? 'Guardando...' : 'Guardar dispositivo' }}
                </button>
              </div>
            </section>

            <section v-if="showRepairForm" class="panel-nested">
              <h4>Nueva orden de trabajo</h4>
              <div class="form-grid two-cols">
                <label>
                  <span>Dispositivo</span>
                  <select v-model="repairForm.device_id">
                    <option value="">Sin seleccionar</option>
                    <option v-for="device in devices" :key="device.id" :value="device.id">
                      {{ device.model || `Dispositivo #${device.id}` }}
                    </option>
                  </select>
                </label>
                <label><span>Prioridad</span><select v-model.number="repairForm.priority"><option :value="1">Alta</option><option :value="2">Normal</option><option :value="3">Baja</option></select></label>
                <label class="full"><span>Problema reportado *</span><textarea v-model.trim="repairForm.problem_reported" rows="3"></textarea></label>
                <label><span>Abono (CLP)</span><input v-model.number="repairForm.paid_amount" type="number" min="0" /></label>
                <label>
                  <span>Medio de pago</span>
                  <select v-model="repairForm.payment_method">
                    <option value="cash">Efectivo</option>
                    <option value="web">Web</option>
                    <option value="transfer">Transferencia</option>
                  </select>
                </label>
                <label class="checkbox-row full"><input v-model="repairForm.group_with_ot" type="checkbox" /><span>Agrupar con OT existente</span></label>
                <label v-if="repairForm.group_with_ot" class="full">
                  <span>OT base</span>
                  <select v-model="repairForm.ot_parent_id">
                    <option value="">Seleccionar OT base</option>
                    <option v-for="item in repairs" :key="item.id" :value="item.id">
                      {{ item.repair_code || `OT #${item.id}` }}
                    </option>
                  </select>
                </label>
              </div>
              <div class="panel-actions">
                <button class="btn-primary" :disabled="contextLoading" @click="createRepairForSelectedClient">
                  {{ contextLoading ? 'Creando...' : 'Crear OT' }}
                </button>
              </div>
            </section>

            <section class="panel-nested">
              <h4>Dispositivos ({{ devices.length }})</h4>
              <p v-if="devices.length === 0" class="empty-state">No hay dispositivos registrados.</p>
              <div v-else class="table-wrap">
                <table>
                  <thead><tr><th>ID</th><th>Modelo</th><th>Marca</th><th>Serial</th></tr></thead>
                  <tbody>
                    <tr v-for="device in devices" :key="device.id">
                      <td>{{ device.id }}</td>
                      <td>{{ device.model || '—' }}</td>
                      <td>{{ device.brand_other || '—' }}</td>
                      <td>{{ device.serial_number || '—' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <section class="panel-nested">
              <h4>OT activas ({{ repairs.length }})</h4>
              <p v-if="repairs.length === 0" class="empty-state">No hay OT activas para este cliente.</p>
              <div v-else class="table-wrap">
                <table>
                  <thead><tr><th>OT</th><th>Estado</th><th>Problema</th><th>Creada</th></tr></thead>
                  <tbody>
                    <tr v-for="item in repairs" :key="item.id">
                      <td>{{ item.repair_code || item.repair_number }}</td>
                      <td>{{ item.status_id || '—' }}</td>
                      <td>{{ item.problem_reported || '—' }}</td>
                      <td>{{ item.created_at ? new Date(item.created_at).toLocaleDateString('es-CL') : '—' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>
          </template>

          <div v-else class="empty-state">Selecciona un cliente para ver detalle.</div>
        </article>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useClientsPage } from '@new/composables/useClientsPage'

const {
  clients,
  devices,
  repairs,
  loading,
  contextLoading,
  error,
  searchQuery,
  selectedClientId,
  selectedClient,
  filteredClients,
  showCreateForm,
  showEditForm,
  showDeviceForm,
  showRepairForm,
  createForm,
  editForm,
  deviceForm,
  repairForm,
  selectClient,
  toggleCreateForm,
  toggleEditForm,
  toggleDeviceForm,
  toggleRepairForm,
  loadClients,
  createClient,
  updateSelectedClient,
  deleteSelectedClient,
  createDeviceForSelectedClient,
  createRepairForSelectedClient
} = useClientsPage()
</script>

<style scoped>
.admin-page { padding: 1rem; display: grid; gap: 1rem; }
.admin-header, .panel-card, .summary-card, .panel-nested { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); }
.admin-header { padding: .9rem; display: flex; gap: .75rem; justify-content: space-between; align-items: center; flex-wrap: wrap; }
.admin-header h1 { margin: 0; font-size: var(--cds-text-3xl); }
.admin-header p { margin: .3rem 0 0; color: var(--cds-text-muted); }
.header-actions { display: flex; gap: .45rem; flex-wrap: wrap; }
.btn-primary, .btn-secondary, .btn-danger { min-height: 44px; border-radius: .55rem; padding: .65rem .9rem; border: 1px solid transparent; font-size: var(--cds-text-base); }
.btn-primary { background: var(--cds-primary); color: var(--cds-white); border-color: var(--cds-primary); }
.btn-secondary { background: var(--cds-white); color: var(--cds-text-normal); border-color: color-mix(in srgb, var(--cds-light) 65%, white); }
.btn-danger { background: #dc2626; color: #fff; border-color: #dc2626; }
.admin-error { margin: 0; border: 1px solid #fecaca; background: #fef2f2; color: #991b1b; border-radius: .65rem; padding: .75rem; }
.panel-card { padding: .9rem; display: grid; gap: .8rem; }
.toolbar { display: grid; gap: .45rem; }
.split-grid { display: grid; gap: .8rem; grid-template-columns: 1fr; }
.list-panel, .detail-panel { display: grid; gap: .65rem; }
.list-panel h3, .detail-panel h3, .panel-card h2, .panel-nested h4 { margin: 0; }
.list-reset { list-style: none; margin: 0; padding: 0; display: grid; gap: .5rem; }
.list-item { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .65rem; padding: .65rem; cursor: pointer; display: grid; gap: .25rem; }
.list-item.active { border-color: color-mix(in srgb, var(--cds-primary) 40%, white); background: color-mix(in srgb, var(--cds-primary) 8%, white); }
.item-head { display: flex; justify-content: space-between; gap: .45rem; align-items: center; }
.chip { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: 999px; padding: .2rem .55rem; font-size: var(--cds-text-sm); }
.detail-head { display: flex; justify-content: space-between; gap: .65rem; flex-wrap: wrap; align-items: start; }
.detail-head p { margin: .2rem 0 0; color: var(--cds-text-muted); }
.summary-grid { display: grid; gap: .65rem; grid-template-columns: repeat(1, minmax(0, 1fr)); }
.summary-card { padding: .65rem; display: grid; gap: .2rem; }
.summary-card span { color: var(--cds-text-muted); font-size: var(--cds-text-sm); }
.summary-card strong { font-size: var(--cds-text-lg); }
.panel-nested { padding: .8rem; display: grid; gap: .6rem; }
.form-grid { display: grid; gap: .6rem; grid-template-columns: 1fr; }
.form-grid.two-cols { grid-template-columns: 1fr; }
.form-grid label { display: grid; gap: .3rem; }
.form-grid span { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.form-grid .full { grid-column: 1 / -1; }
.form-grid input, .form-grid textarea, .form-grid select, .toolbar input { min-height: 44px; border-radius: .55rem; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); padding: .65rem .75rem; font-size: var(--cds-text-base); }
.form-grid textarea { min-height: 92px; resize: vertical; }
.checkbox-row { display: flex !important; align-items: center; gap: .5rem !important; }
.panel-actions { display: flex; justify-content: flex-end; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: .55rem; border-bottom: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); vertical-align: top; }
th { color: var(--cds-text-muted); font-size: var(--cds-text-sm); }
.empty-state { margin: 0; border: 1px dashed color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .65rem; padding: .8rem; color: var(--cds-text-muted); }
@media (min-width: 1024px) {
  .split-grid { grid-template-columns: minmax(280px, .95fr) minmax(0, 1.6fr); }
  .summary-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .form-grid.two-cols { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
