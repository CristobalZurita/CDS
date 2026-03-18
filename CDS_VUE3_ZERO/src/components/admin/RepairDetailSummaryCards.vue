<template>
  <section class="summary-grid">
    <article class="summary-card">
      <span>Estado</span>
      <strong :class="statusClass">{{ statusLabel }}</strong>
    </article>
    <article class="summary-card">
      <span>Prioridad</span>
      <strong :class="priorityClass">{{ priorityLabel }}</strong>
    </article>
    <article class="summary-card">
      <span>Total OT</span>
      <strong>{{ formatCurrency(repair?.total_cost) }}</strong>
    </article>
    <article class="summary-card">
      <span>Abonado</span>
      <strong>{{ formatCurrency(repair?.paid_amount) }}</strong>
    </article>
  </section>
</template>

<script setup>
defineProps({
  repair: {
    type: Object,
    default: null
  },
  statusLabel: {
    type: String,
    required: true
  },
  statusClass: {
    type: String,
    required: true
  },
  priorityLabel: {
    type: String,
    required: true
  },
  priorityClass: {
    type: String,
    required: true
  },
  formatCurrency: {
    type: Function,
    required: true
  }
})
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/repairDetailAdminShared.css"></style>
