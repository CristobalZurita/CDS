<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Newsletter</h1>
        <p>Suscripciones activas e historico.</p>
      </div>
      <div class="header-actions">
        <input v-model.trim="search" type="text" placeholder="Buscar email u origen" />
        <button class="btn-secondary" data-testid="newsletter-refresh" :disabled="isLoading" @click="loadSubscriptions">
          {{ isLoading ? 'Actualizando...' : 'Actualizar' }}
        </button>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section class="panel-card">
      <div v-if="isLoading" class="empty-state">Cargando suscripciones...</div>
      <div v-else-if="filteredSubscriptions.length === 0" class="empty-state">No hay suscripciones registradas.</div>
      <div v-else class="table-wrap">
        <table data-testid="newsletter-table">
          <thead>
            <tr>
              <th>Email</th>
              <th>Estado</th>
              <th>Origen</th>
              <th>Fecha</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="subscription in filteredSubscriptions" :key="subscription.id">
              <td>{{ subscription.email }}</td>
              <td>{{ subscription.is_active ? 'Activa' : 'Inactiva' }}</td>
              <td>{{ subscription.source_url || '—' }}</td>
              <td>{{ formatDate(subscription.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useNewsletterSubscriptionsPage } from '@/composables/useNewsletterSubscriptionsPage'

const {
  isLoading,
  error,
  search,
  filteredSubscriptions,
  formatDate,
  loadSubscriptions
} = useNewsletterSubscriptionsPage()
</script>

<style scoped>
.admin-page { padding: 1rem; display: grid; gap: 1rem; }
.admin-header, .panel-card { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); }
.admin-header { padding: .9rem; display: flex; flex-wrap: wrap; justify-content: space-between; gap: .75rem; align-items: center; }
.admin-header h1 { margin: 0; font-size: var(--cds-text-3xl); }
.admin-header p { margin: .3rem 0 0; color: var(--cds-text-muted); }
.header-actions { display: flex; flex-wrap: wrap; gap: .5rem; }
.header-actions input { min-height: 44px; min-width: 250px; padding: .65rem .75rem; border-radius: .55rem; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); font-size: var(--cds-text-base); }
.btn-secondary { min-height: 44px; padding: .65rem .9rem; border-radius: .55rem; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); background: var(--cds-white); color: var(--cds-text-normal); font-size: var(--cds-text-base); }
.admin-error { margin: 0; border: 1px solid #f4c7c3; background: #fef3f2; color: #b42318; border-radius: .6rem; padding: .75rem; }
.panel-card { padding: .9rem; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: .6rem; border-bottom: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); }
th { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.empty-state { border: 1px dashed color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .7rem; padding: .9rem; }
</style>
