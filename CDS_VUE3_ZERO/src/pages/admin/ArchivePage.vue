<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Archivo</h1>
        <p>OT archivadas y opcion de reactivacion.</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" :disabled="loading" @click="loadArchive">
          {{ loading ? 'Actualizando...' : 'Actualizar' }}
        </button>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section class="panel-card">
      <label>
        <span>Buscar en archivo</span>
        <input v-model.trim="searchQuery" type="search" placeholder="OT, cliente, instrumento o estado" />
      </label>
    </section>

    <section class="panel-card">
      <h2>Archivadas ({{ items.length }})</h2>
      <p v-if="items.length === 0" class="empty-state">Sin OT archivadas.</p>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>OT</th>
              <th>Cliente</th>
              <th>Instrumento</th>
              <th>Estado</th>
              <th>Archivada</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td>{{ item.repair_code || item.repair_number }}</td>
              <td>{{ item.client_name || '—' }}</td>
              <td>{{ item.device_model || '—' }}</td>
              <td>{{ item.status || '—' }}</td>
              <td>{{ formatDate(item.archived_at) }}</td>
              <td>
                <div class="row-actions">
                  <button class="btn-secondary" :disabled="busyId === item.id" @click="goToRepair(item)">Ver</button>
                  <button class="btn-primary" :disabled="busyId === item.id" @click="reactivate(item)">
                    {{ busyId === item.id ? 'Reactivando...' : 'Reactivar' }}
                  </button>
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
import { useArchivePage } from '@/composables/useArchivePage'

const {
  items,
  loading,
  error,
  busyId,
  searchQuery,
  formatDate,
  loadArchive,
  goToRepair,
  reactivate
} = useArchivePage()
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped>
.panel-card label { display: grid; gap: .3rem; }
.panel-card span { color: var(--cds-text-muted); font-size: var(--cds-text-sm); }
.panel-card input { min-height: 44px; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); border-radius: .55rem; padding: .65rem .75rem; font-size: var(--cds-text-base); }
</style>
