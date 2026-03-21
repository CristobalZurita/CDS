<template>
  <section class="panel-card">
    <h2>Informacion general</h2>
    <div class="detail-grid">
      <article>
        <p><strong>Cliente:</strong> {{ repair?.client?.name || '—' }}</p>
        <p><strong>Codigo cliente:</strong> {{ repair?.client?.client_code || '—' }}</p>
        <p><strong>Instrumento:</strong> {{ repair?.device?.model || '—' }}</p>
        <p><strong>Serial:</strong> {{ repair?.device?.serial_number || '—' }}</p>
        <p><strong>OT padre:</strong> {{ formatParentOt(repair?.ot_parent_id, repair?.ot_sequence) }}</p>
        <p><strong>Garantia hasta:</strong> {{ formatDate(repair?.warranty_until) }}</p>
      </article>
      <article>
        <p><strong>Problema:</strong> {{ repair?.problem_reported || '—' }}</p>
        <p><strong>Diagnostico:</strong> {{ repair?.diagnosis || '—' }}</p>
        <p><strong>Trabajo:</strong> {{ repair?.work_performed || '—' }}</p>
        <p><strong>Ingreso:</strong> {{ formatDate(repair?.intake_date) }}</p>
        <p><strong>Diagnostico fecha:</strong> {{ formatDate(repair?.diagnosis_date) }}</p>
        <p><strong>Aprobacion:</strong> {{ formatDate(repair?.approval_date) }}</p>
        <p><strong>Inicio:</strong> {{ formatDate(repair?.start_date) }}</p>
        <p><strong>Completada:</strong> {{ formatDate(repair?.completion_date) }}</p>
        <p><strong>Entrega:</strong> {{ formatDate(repair?.delivery_date) }}</p>
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
  },
  formatDate: {
    type: Function,
    required: true
  }
})

function formatParentOt(otParentId, otSequence) {
  const parentId = Number(otParentId || 0)
  const sequence = Number(otSequence || 0)

  if (!parentId) return 'Base'
  if (!sequence) return `OT #${parentId}`
  return `OT #${parentId} · tramo ${sequence}`
}
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/repairDetailAdminShared.css"></style>
