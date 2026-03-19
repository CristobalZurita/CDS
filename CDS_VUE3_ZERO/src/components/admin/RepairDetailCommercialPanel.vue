<template>
  <section class="panel-card">
    <h2>Garantia y comprobante</h2>

    <div class="detail-grid commercial-grid">
      <article class="panel-nested commercial-card">
        <div class="panel-head">
          <h3>Garantia</h3>
          <button
            v-if="canCreateWarranty"
            class="btn-secondary"
            :disabled="performingAction"
            @click="emit('create-warranty')"
          >
            Crear garantia
          </button>
        </div>

        <template v-if="warranty">
          <p><strong>Tipo:</strong> {{ formatWarrantyType(warranty.warranty_type) }}</p>
          <p><strong>Estado:</strong> <span :class="resolveWarrantyStatusClass(warranty.status)">{{ formatWarrantyStatus(warranty.status) }}</span></p>
          <p><strong>Inicio:</strong> {{ formatDate(warranty.start_date) }}</p>
          <p><strong>Fin:</strong> {{ formatDate(warranty.end_date) }}</p>
          <p><strong>Reclamos:</strong> {{ warranty.claims_used }} / {{ warranty.max_claims }}</p>
        </template>
        <p v-else class="empty-state">No hay garantia registrada para esta OT.</p>
      </article>

      <article class="panel-nested commercial-card">
        <div class="panel-head">
          <h3>Comprobante</h3>
          <button
            v-if="canCreateInvoice"
            class="btn-secondary"
            :disabled="performingAction"
            @click="emit('create-invoice')"
          >
            Generar comprobante
          </button>
        </div>

        <template v-if="invoice">
          <p><strong>Numero:</strong> {{ invoice.invoice_number || `Factura #${invoice.id}` }}</p>
          <p><strong>Estado:</strong> <span :class="resolveInvoiceStatusClass(invoice.status)">{{ formatInvoiceStatus(invoice.status) }}</span></p>
          <p><strong>Emision:</strong> {{ formatDate(invoice.issue_date) }}</p>
          <p><strong>Vencimiento:</strong> {{ formatDate(invoice.due_date) }}</p>
          <p><strong>Total:</strong> {{ formatCurrency(invoice.total) }}</p>
          <p><strong>Pendiente:</strong> {{ formatCurrency(invoice.amount_due) }}</p>
        </template>
        <p v-else class="empty-state">No hay comprobante generado para esta OT.</p>
      </article>
    </div>
  </section>
</template>

<script setup>
defineProps({
  warranty: {
    type: Object,
    default: null
  },
  invoice: {
    type: Object,
    default: null
  },
  performingAction: {
    type: Boolean,
    default: false
  },
  canCreateWarranty: {
    type: Boolean,
    default: false
  },
  canCreateInvoice: {
    type: Boolean,
    default: false
  },
  formatDate: {
    type: Function,
    required: true
  },
  formatCurrency: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['create-warranty', 'create-invoice'])

function formatWarrantyType(value) {
  const map = {
    labor: 'Mano de obra',
    parts: 'Repuestos',
    full: 'Completa',
    limited: 'Limitada',
    extended: 'Extendida'
  }
  return map[String(value || '').toLowerCase()] || 'Sin tipo'
}

function formatWarrantyStatus(value) {
  const map = {
    active: 'Activa',
    expired: 'Vencida',
    voided: 'Anulada',
    claimed: 'Con reclamo',
    used: 'Usada'
  }
  return map[String(value || '').toLowerCase()] || 'Sin estado'
}

function formatInvoiceStatus(value) {
  const map = {
    draft: 'Borrador',
    sent: 'Enviada',
    viewed: 'Vista',
    paid: 'Pagada',
    partial: 'Pago parcial',
    overdue: 'Vencida',
    void: 'Anulada',
    refunded: 'Reembolsada'
  }
  return map[String(value || '').toLowerCase()] || 'Sin estado'
}

function resolveWarrantyStatusClass(status) {
  const key = String(status || '').toLowerCase()
  if (key === 'active') return 'status-success'
  if (['claimed', 'used'].includes(key)) return 'status-progress'
  if (['expired', 'voided'].includes(key)) return 'status-archived'
  return 'status-neutral'
}

function resolveInvoiceStatusClass(status) {
  const key = String(status || '').toLowerCase()
  if (key === 'paid') return 'status-success'
  if (['sent', 'viewed', 'partial'].includes(key)) return 'status-progress'
  if (['overdue', 'void', 'refunded'].includes(key)) return 'status-archived'
  return 'status-neutral'
}
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/repairDetailAdminShared.css"></style>
