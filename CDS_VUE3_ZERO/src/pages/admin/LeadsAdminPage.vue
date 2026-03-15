<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Prospectos del Cotizador</h1>
        <p>Leads capturados desde el wizard de cotización público.</p>
      </div>
      <div class="header-actions">
        <input
          v-model.trim="search"
          type="text"
          placeholder="Buscar nombre, email, equipo"
        />
        <button
          class="btn-secondary"
          :disabled="isLoading"
          @click="loadLeads"
        >
          {{ isLoading ? 'Actualizando...' : 'Actualizar' }}
        </button>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section class="panel-card">
      <div v-if="isLoading" class="empty-state">Cargando prospectos...</div>
      <div v-else-if="filteredLeads.length === 0" class="empty-state">
        No hay prospectos registrados aún.
      </div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Email</th>
              <th>Teléfono</th>
              <th>Equipo</th>
              <th>Estimación</th>
              <th>Estado</th>
              <th>Fecha</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="lead in filteredLeads" :key="lead.id">
              <td class="td-id">{{ lead.id }}</td>
              <td>{{ lead.nombre }}</td>
              <td>
                <a :href="`mailto:${lead.email}`">{{ lead.email }}</a>
              </td>
              <td>{{ lead.telefono || '—' }}</td>
              <td>
                <span v-if="lead.equipment_brand || lead.equipment_model">
                  {{ lead.equipment_brand }} {{ lead.equipment_model }}
                </span>
                <span v-else class="muted">—</span>
              </td>
              <td>{{ formatFinalCost(lead.quote_result) }}</td>
              <td>
                <span class="status-badge" :class="`status-${lead.status}`">
                  {{ statusLabel(lead.status) }}
                </span>
              </td>
              <td>{{ formatDate(lead.created_at) }}</td>
              <td>
                <button
                  v-if="nextStatus(lead.status)"
                  class="btn-advance"
                  :disabled="isBusy(lead.id)"
                  @click="advanceStatus(lead)"
                >
                  <span v-if="isBusy(lead.id)">…</span>
                  <span v-else>→ {{ statusLabel(nextStatus(lead.status)) }}</span>
                </button>
                <span v-else class="muted">Finalizado</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useLeadsAdminPage } from '@/composables/useLeadsAdminPage'

const {
  isLoading,
  error,
  search,
  filteredLeads,
  isBusy,
  statusLabel,
  nextStatus,
  loadLeads,
  advanceStatus,
  formatDate,
  formatFinalCost
} = useLeadsAdminPage()
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped>
.header-actions input {
  min-height: 44px;
  min-width: 260px;
  padding: .65rem .75rem;
  border-radius: .55rem;
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  font-size: var(--cds-text-base);
}

.td-id {
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
}

.muted {
  color: var(--cds-text-muted);
}

.status-badge {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 0.4rem;
  font-size: var(--cds-text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.status-new {
  background: color-mix(in srgb, var(--cds-primary) 12%, white);
  color: var(--cds-primary);
}

.status-contacted {
  background: color-mix(in srgb, #2563eb 10%, white);
  color: #1d4ed8;
}

.status-converted {
  background: color-mix(in srgb, #16a34a 10%, white);
  color: #15803d;
}

.btn-advance {
  min-height: 32px;
  padding: 0.3rem 0.65rem;
  border-radius: 0.4rem;
  border: 1px solid color-mix(in srgb, var(--cds-primary) 40%, white);
  background: color-mix(in srgb, var(--cds-primary) 8%, white);
  color: var(--cds-primary);
  font-size: var(--cds-text-xs);
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.btn-advance:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-advance:not(:disabled):hover {
  background: color-mix(in srgb, var(--cds-primary) 15%, white);
}
</style>
