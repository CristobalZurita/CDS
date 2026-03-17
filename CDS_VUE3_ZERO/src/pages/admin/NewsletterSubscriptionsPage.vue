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

<style scoped src="./commonAdminPage.css"></style>
