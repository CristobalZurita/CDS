<template>
  <section class="panel-card">
    <div class="panel-head">
      <h2>Auditoria OT ({{ audit.length }})</h2>
    </div>

    <p v-if="audit.length === 0" class="empty-state">Sin movimientos de auditoria registrados.</p>
    <div v-else class="audit-list">
      <article v-for="entry in audit" :key="entry.id" class="audit-card">
        <header>
          <strong>{{ resolveAuditTitle(entry) }}</strong>
          <small>{{ formatDate(entry.created_at) }}</small>
        </header>

        <p v-if="entry.message">{{ entry.message }}</p>

        <div v-if="entry.from_status || entry.to_status" class="audit-meta">
          <span><strong>Estado:</strong> {{ entry.from_status || '—' }} → {{ entry.to_status || '—' }}</span>
        </div>

        <div v-if="entry.fields.length" class="audit-meta">
          <span><strong>Campos:</strong> {{ entry.fields.join(', ') }}</span>
        </div>

        <div v-if="entry.status_notes" class="audit-meta">
          <span><strong>Notas:</strong> {{ entry.status_notes }}</span>
        </div>

        <div class="audit-meta">
          <span><strong>Evento:</strong> {{ entry.event_type || '—' }}</span>
          <span v-if="entry.user_id"><strong>Usuario:</strong> #{{ entry.user_id }}</span>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
defineProps({
  audit: {
    type: Array,
    default: () => []
  },
  formatDate: {
    type: Function,
    required: true
  }
})

function resolveAuditTitle(entry) {
  const eventType = String(entry?.event_type || '').trim().toLowerCase()
  if (eventType === 'repair.create') return 'Creacion de OT'
  if (eventType === 'repair.update') return 'Actualizacion de OT'
  if (eventType === 'repair.status.change') return 'Cambio de estado'
  if (eventType === 'repair.delete') return 'Eliminacion de OT'
  return eventType || 'Movimiento'
}
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/repairDetailAdminShared.css"></style>
