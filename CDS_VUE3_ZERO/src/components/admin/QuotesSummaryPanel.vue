<template>
  <section class="summary-grid">
    <article class="summary-card"><span>En tablero</span><strong>{{ counts.total }}</strong></article>
    <article class="summary-card"><span>Abiertas</span><strong>{{ metrics.open_total }}</strong></article>
    <article class="summary-card"><span>Pendientes</span><strong>{{ metrics.pending }}</strong></article>
    <article class="summary-card"><span>Enviadas</span><strong>{{ metrics.sent }}</strong></article>
    <article class="summary-card"><span>Aprobadas</span><strong>{{ metrics.approved }}</strong></article>
    <article class="summary-card warning"><span>Vencen &lt; 3 dias</span><strong>{{ metrics.expiring_3d }}</strong></article>
    <article class="summary-card danger"><span>Vencidas</span><strong>{{ metrics.expired_open }}</strong></article>
  </section>
</template>

<script setup>
defineProps({
  counts: {
    type: Object,
    required: true
  },
  metrics: {
    type: Object,
    required: true
  }
})
</script>

<style scoped src="@/pages/admin/commonAdminPage.css"></style>
<style scoped src="@/pages/admin/quotesPageShared.css"></style>
