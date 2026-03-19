<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Cotizaciones</h1>
        <p>Tablero de estados para pendientes, enviadas y cerradas.</p>
      </div>
      <div class="header-actions">
        <button class="btn-primary" @click="openCreateModal">
          + Nueva Cotización
        </button>
        <button class="btn-secondary" :disabled="loading" @click="loadBoard">
          {{ loading ? 'Actualizando...' : 'Actualizar' }}
        </button>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <QuotesToolbarPanel
      v-model:search-query="searchQuery"
      v-model:status-filter="statusFilter"
      v-model:custom-message="customMessage"
      v-model:send-whatsapp="sendWhatsapp"
      :status-options="statusOptions"
      @refresh="loadBoard"
    />

    <QuotesSummaryPanel :counts="counts" :metrics="metrics" />

    <QuotesBoardColumns
      :column-defs="columnDefs"
      :highlighted-quote-id="highlightedQuoteId"
      :is-busy="isBusy"
      :get-column-items="getColumnItems"
      :get-column-count="getColumnCount"
      :format-currency="formatCurrency"
      :format-date="formatDate"
      @send-quote="sendQuote"
      @change-status="changeStatus"
      @create-repair="createRepairFromQuote"
      @open-repair="openRepair"
      @delete-quote="deleteQuote"
    />

    <QuotesCreateModal
      :open="showCreateModal"
      :quote="newQuote"
      :is-creating="isCreating"
      @close="closeCreateModal"
      @submit="submitNewQuote"
      @update-field="updateNewQuoteField"
    />
  </main>
</template>

<script setup>
import QuotesBoardColumns from '@/components/admin/QuotesBoardColumns.vue'
import QuotesCreateModal from '@/components/admin/QuotesCreateModal.vue'
import QuotesSummaryPanel from '@/components/admin/QuotesSummaryPanel.vue'
import QuotesToolbarPanel from '@/components/admin/QuotesToolbarPanel.vue'
import { useQuotesAdminPage } from '@/composables/useQuotesAdminPage'

const {
  loading,
  error,
  searchQuery,
  statusFilter,
  customMessage,
  sendWhatsapp,
  statusOptions,
  columnDefs,
  counts,
  metrics,
  highlightedQuoteId,
  showCreateModal,
  isCreating,
  newQuote,
  isBusy,
  getColumnItems,
  getColumnCount,
  formatCurrency,
  formatDate,
  loadBoard,
  sendQuote,
  changeStatus,
  createRepairFromQuote,
  openRepair,
  deleteQuote,
  openCreateModal,
  closeCreateModal,
  updateNewQuoteField,
  submitNewQuote
} = useQuotesAdminPage()
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped src="./quotesPageShared.css"></style>
