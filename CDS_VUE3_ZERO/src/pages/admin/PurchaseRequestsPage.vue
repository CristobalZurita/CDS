<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Solicitudes de compra</h1>
        <p>Carrito interno por cliente/OT y control de pagos.</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" :disabled="loading" @click="loadRequests">
          {{ loading ? 'Actualizando...' : 'Actualizar' }}
        </button>
        <button class="btn-primary" :disabled="loading" @click="toggleForm">
          {{ showForm ? 'Cancelar' : 'Nueva solicitud' }}
        </button>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section v-if="activeRepairFilter" class="panel-card notice-card">
      <p>Filtro activo por OT ID: <strong>#{{ activeRepairFilter }}</strong></p>
      <div class="panel-actions"><button class="btn-secondary" @click="clearRepairFilter">Quitar filtro</button></div>
    </section>

    <section v-if="showForm" class="panel-card">
      <h2>Nueva solicitud</h2>
      <div class="form-grid two-cols">
        <label>
          <span>Cliente</span>
          <select v-model="createForm.client_id">
            <option value="">Sin cliente</option>
            <option v-for="client in clients" :key="client.id" :value="client.id">
              {{ client.client_code || `#${client.id}` }} - {{ client.name }}
            </option>
          </select>
        </label>
        <label>
          <span>OT</span>
          <select v-model="createForm.repair_id">
            <option value="">Sin OT</option>
            <option v-for="repair in repairs" :key="repair.id" :value="repair.id">
              {{ repair.repair_code || `OT #${repair.id}` }}
            </option>
          </select>
        </label>
        <label class="full"><span>Notas</span><textarea v-model.trim="createForm.notes" rows="2"></textarea></label>
        <label><span>Item *</span><input v-model.trim="createForm.item_name" type="text" /></label>
        <label><span>SKU</span><input v-model.trim="createForm.item_sku" type="text" /></label>
        <label><span>Cantidad</span><input v-model.number="createForm.item_qty" type="number" min="1" /></label>
        <label><span>Precio unitario (CLP)</span><input v-model.number="createForm.item_price" type="number" min="0" /></label>
        <label class="full"><span>URL externa</span><input v-model.trim="createForm.item_url" type="text" placeholder="https://..." /></label>
      </div>
      <div class="panel-actions">
        <button class="btn-primary" :disabled="loading" @click="createRequest">
          {{ loading ? 'Guardando...' : 'Crear solicitud' }}
        </button>
      </div>
    </section>

    <section class="panel-card">
      <h2>Tablero ({{ requests.length }})</h2>
      <p v-if="requests.length === 0" class="empty-state">Sin solicitudes registradas.</p>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Cliente / OT</th>
              <th>Estado</th>
              <th>Items</th>
              <th>Total</th>
              <th>Cobro cliente</th>
              <th>Ultimo pago</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="req in requests" :key="req.id">
              <td>#{{ req.id }}</td>
              <td>
                <div class="cell-stack">
                  <strong>{{ req.client_name || 'SIN_CLIENTE' }}</strong>
                  <small>{{ req.repair_code || req.repair_number || 'SIN_OT' }}</small>
                </div>
              </td>
              <td><span class="chip">{{ req.status }}</span></td>
              <td>{{ req.items_count || req.items?.length || 0 }}</td>
              <td>{{ formatCurrency(req.total_items_amount || req.requested_amount || 0) }}</td>
              <td>
                <div class="payment-box">
                  <input v-model.number="paymentDraft[req.id].amount" type="number" min="1" placeholder="Monto" />
                  <input v-model.number="paymentDraft[req.id].dueDays" type="number" min="1" max="30" placeholder="Dias" />
                  <input v-model="paymentDraft[req.id].instruction" type="text" placeholder="Instruccion" />
                  <button class="btn-primary" :disabled="isBusy(req.id)" @click="requestPayment(req)">
                    {{ isBusy(req.id) ? 'Enviando...' : 'Solicitar pago' }}
                  </button>
                </div>
              </td>
              <td>
                <div v-if="req.latest_payment" class="cell-stack">
                  <strong>{{ req.latest_payment.status }}</strong>
                  <small>{{ formatCurrency(req.latest_payment.amount || req.requested_amount || 0) }}</small>
                  <small v-if="req.latest_payment.deposit_reference">Ref: {{ req.latest_payment.deposit_reference }}</small>
                  <a v-if="req.latest_payment.proof_path" :href="toApiPath(req.latest_payment.proof_path)" target="_blank" rel="noopener">Ver comprobante</a>
                </div>
                <span v-else>Sin pago</span>
              </td>
              <td>
                <div class="row-actions">
                  <button class="btn-secondary" :disabled="isBusy(req.id)" @click="confirmPayment(req)">Confirmar pago</button>
                  <select :value="req.status" :disabled="isBusy(req.id)" @change="setStatus(req, $event.target.value)">
                    <option v-for="status in statusOptions" :key="status" :value="status">{{ status }}</option>
                  </select>
                  <button class="btn-danger" :disabled="isBusy(req.id)" @click="deleteRequest(req)">Eliminar</button>
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
import { usePurchaseRequestsPage } from '@/composables/usePurchaseRequestsPage'

const {
  requests,
  clients,
  repairs,
  loading,
  error,
  showForm,
  createForm,
  paymentDraft,
  activeRepairFilter,
  statusOptions,
  toggleForm,
  isBusy,
  formatCurrency,
  toApiPath,
  loadRequests,
  createRequest,
  requestPayment,
  confirmPayment,
  setStatus,
  deleteRequest,
  clearRepairFilter
} = usePurchaseRequestsPage()
</script>

<style scoped>
.admin-page { padding: 1rem; display: grid; gap: 1rem; }
.admin-header, .panel-card { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); }
.admin-header { padding: .9rem; display: flex; justify-content: space-between; align-items: center; gap: .75rem; flex-wrap: wrap; }
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
.notice-card { background: color-mix(in srgb, #0284c7 10%, white); }
.notice-card p { margin: 0; }
.form-grid { display: grid; gap: .6rem; grid-template-columns: 1fr; }
.form-grid.two-cols { grid-template-columns: 1fr; }
.form-grid label { display: grid; gap: .3rem; }
.form-grid span { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.form-grid input, .form-grid textarea, .form-grid select, .payment-box input, .row-actions select { min-height: 44px; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); border-radius: .55rem; padding: .65rem .75rem; font-size: var(--cds-text-base); }
.form-grid textarea { min-height: 88px; resize: vertical; }
.form-grid .full { grid-column: 1 / -1; }
.panel-actions { display: flex; justify-content: flex-end; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: .55rem; border-bottom: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); vertical-align: top; }
th { color: var(--cds-text-muted); font-size: var(--cds-text-sm); }
.cell-stack { display: grid; gap: .2rem; }
.chip { border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); border-radius: 999px; padding: .15rem .55rem; font-size: var(--cds-text-sm); text-transform: uppercase; }
.payment-box { display: grid; gap: .35rem; min-width: 220px; }
.row-actions { display: grid; gap: .35rem; min-width: 180px; }
.empty-state { margin: 0; border: 1px dashed color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .65rem; padding: .8rem; color: var(--cds-text-muted); }
@media (min-width: 900px) {
  .form-grid.two-cols { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
