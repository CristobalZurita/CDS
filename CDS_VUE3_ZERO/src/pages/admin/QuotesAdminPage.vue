<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Cotizaciones</h1>
        <p>Tablero de estados para pendientes, enviadas y cerradas.</p>
      </div>
      <div class="header-actions">
        <button class="btn-primary" @click="showNewQuoteModal = true">
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
      :open="showNewQuoteModal"
      :quote="newQuote"
      :is-creating="isCreating"
      @close="closeModal"
      @submit="handleCreateQuote"
      @update-field="updateNewQuoteField"
    />
  </main>
</template>

<script setup>
import { ref, reactive } from 'vue'
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
  createQuote
} = useQuotesAdminPage()

// Modal state
const showNewQuoteModal = ref(false)
const isCreating = ref(false)

// Default valid until (30 days)
const defaultValidUntil = () => {
  const date = new Date()
  date.setDate(date.getDate() + 30)
  return date.toISOString().split('T')[0]
}

const newQuote = reactive({
  client_name: '',
  client_email: '',
  client_phone: '',
  problem_description: '',
  diagnosis: '',
  estimated_parts_cost: 0,
  estimated_labor_cost: 0,
  estimated_total: 0,
  valid_until: defaultValidUntil()
})

function closeModal() {
  showNewQuoteModal.value = false
  resetForm()
}

function resetForm() {
  newQuote.client_name = ''
  newQuote.client_email = ''
  newQuote.client_phone = ''
  newQuote.problem_description = ''
  newQuote.diagnosis = ''
  newQuote.estimated_parts_cost = 0
  newQuote.estimated_labor_cost = 0
  newQuote.estimated_total = 0
  newQuote.valid_until = defaultValidUntil()
}

function updateNewQuoteField({ field, value }) {
  if (!field) return
  newQuote[field] = value
}

async function handleCreateQuote() {
  isCreating.value = true
  
  const result = await createQuote(newQuote)
  
  if (result.success) {
    closeModal()
  }
  
  isCreating.value = false
}
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped src="./quotesPageShared.css"></style>
