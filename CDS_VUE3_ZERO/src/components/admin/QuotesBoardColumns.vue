<template>
  <section class="columns-grid">
    <article v-for="column in columnDefs" :key="column.key" class="column-card">
      <header class="column-head">
        <h2>{{ column.label }}</h2>
        <span class="chip">{{ getColumnCount(column.key) }}</span>
      </header>

      <div class="column-body">
        <article
          v-for="quote in getColumnItems(column.key)"
          :key="quote.id"
          class="quote-card"
          :class="{ highlighted: highlightedQuoteId === quote.id }"
        >
          <div class="quote-head">
            <strong>{{ quote.quote_number || `COT-${quote.id}` }}</strong>
            <span class="status-chip">{{ quote.status || 'pending' }}</span>
          </div>

          <div class="quote-meta">
            <div><span>Cliente:</span> {{ quote.client?.name || quote.client_name || 'SIN_DATO' }}</div>
            <div><span>Total:</span> {{ formatCurrency(quote.estimated_total) }}</div>
            <div><span>Validez:</span> {{ formatDate(quote.valid_until) }}</div>
            <div v-if="quote.linked_repair_id"><span>OT:</span> {{ quote.linked_repair_number || `OT-${quote.linked_repair_id}` }}</div>
          </div>

          <p class="quote-problem">{{ quote.problem_description || 'Sin descripcion' }}</p>

          <div class="row-actions">
            <button
              v-if="quote.status === 'pending'"
              class="btn-primary"
              :disabled="isBusy(quote.id)"
              @click="emit('send-quote', quote)"
            >
              {{ isBusy(quote.id) ? 'Enviando...' : 'Enviar' }}
            </button>

            <button
              v-if="quote.status === 'sent'"
              class="btn-success"
              :disabled="isBusy(quote.id)"
              @click="emit('change-status', quote, 'approved')"
            >
              Aprobar
            </button>

            <button
              v-if="quote.status === 'sent'"
              class="btn-danger"
              :disabled="isBusy(quote.id)"
              @click="emit('change-status', quote, 'denied')"
            >
              Rechazar
            </button>

            <button
              v-if="quote.status === 'approved' && !quote.linked_repair_id"
              class="btn-secondary"
              :disabled="isBusy(quote.id)"
              @click="emit('create-repair', quote)"
            >
              {{ isBusy(quote.id) ? 'Creando OT...' : 'Crear OT' }}
            </button>

            <button
              v-if="quote.linked_repair_id"
              class="btn-secondary"
              @click="emit('open-repair', quote.linked_repair_id)"
            >
              Ver OT
            </button>

            <button
              v-if="!quote.linked_repair_id"
              class="btn-danger"
              :disabled="isBusy(quote.id)"
              @click="emit('delete-quote', quote)"
            >
              Eliminar
            </button>
          </div>
        </article>

        <p v-if="getColumnItems(column.key).length === 0" class="empty-state">Sin cotizaciones en esta columna.</p>
      </div>
    </article>
  </section>
</template>

<script setup>
defineProps({
  columnDefs: {
    type: Array,
    default: () => []
  },
  highlightedQuoteId: {
    type: Number,
    default: null
  },
  isBusy: {
    type: Function,
    required: true
  },
  getColumnItems: {
    type: Function,
    required: true
  },
  getColumnCount: {
    type: Function,
    required: true
  },
  formatCurrency: {
    type: Function,
    required: true
  },
  formatDate: {
    type: Function,
    required: true
  }
})

const emit = defineEmits([
  'send-quote',
  'change-status',
  'create-repair',
  'open-repair',
  'delete-quote'
])
</script>

<style scoped src="@/pages/admin/commonAdminPage.css"></style>
<style scoped src="@/pages/admin/quotesPageShared.css"></style>
