<template>
  <section class="panel-card">
    <h2>Informacion general</h2>
    <div class="detail-grid">
      <article>
        <p><strong>Cliente:</strong> {{ repair?.client?.name || '—' }}</p>
        <p><strong>Codigo cliente:</strong> {{ repair?.client?.client_code || '—' }}</p>
        <p><strong>Instrumento:</strong> {{ repair?.device?.model || '—' }}</p>
        <p><strong>Serial:</strong> {{ repair?.device?.serial_number || '—' }}</p>
      </article>
      <article>
        <p><strong>Problema:</strong> {{ repair?.problem_reported || '—' }}</p>
        <p><strong>Diagnostico:</strong> {{ repair?.diagnosis || '—' }}</p>
        <p><strong>Trabajo:</strong> {{ repair?.work_performed || '—' }}</p>
        <p><strong>Archivada:</strong> {{ isArchived ? 'Si' : 'No' }}</p>
      </article>
    </div>
  </section>
</template>

<script setup>
defineProps({
  repair: {
    type: Object,
    default: null
  },
  isArchived: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/repairDetailAdminShared.css"></style>
