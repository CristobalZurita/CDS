<template>
  <section class="panel-card">
    <h2>Acciones</h2>
    <div class="action-grid">
      <button class="btn-secondary" :disabled="performingAction" @click="emit('notify-client')">Enviar resumen al cliente</button>
      <button class="btn-secondary" :disabled="downloadingClosurePdf" @click="emit('download-closure-pdf')">
        {{ downloadingClosurePdf ? 'Generando PDF...' : 'Descargar cierre OT' }}
      </button>
      <button v-if="!isArchived" class="btn-danger" :disabled="performingAction" @click="emit('archive-repair')">Archivar OT</button>
      <button v-else class="btn-primary" :disabled="performingAction" @click="emit('reactivate-repair')">Reactivar OT</button>
    </div>
  </section>
</template>

<script setup>
defineProps({
  performingAction: {
    type: Boolean,
    default: false
  },
  downloadingClosurePdf: {
    type: Boolean,
    default: false
  },
  isArchived: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['notify-client', 'download-closure-pdf', 'archive-repair', 'reactivate-repair'])
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/repairDetailAdminShared.css"></style>
