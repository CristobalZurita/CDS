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
                <StatusBadge
                  :label="statusLabel(lead.status)"
                  :variant="statusVariant(lead.status)"
                  size="sm"
                  rounded
                />
              </td>
              <td>{{ formatDate(lead.created_at) }}</td>
              <td>
                <BaseButton
                  v-if="nextStatus(lead.status)"
                  type="button"
                  variant="ghost"
                  size="sm"
                  class="lead-advance-button"
                  :disabled="isBusy(lead.id)"
                  @click="advanceStatus(lead)"
                >
                  <span v-if="isBusy(lead.id)">…</span>
                  <span v-else>→ {{ statusLabel(nextStatus(lead.status)) }}</span>
                </BaseButton>
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
import { BaseButton } from '@/components/base'
import { StatusBadge } from '@/components/composite'
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

function statusVariant(status) {
  if (status === 'contacted') return 'info'
  if (status === 'converted') return 'success'
  return 'primary'
}
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped src="./leadsAdminPageShared.css"></style>
