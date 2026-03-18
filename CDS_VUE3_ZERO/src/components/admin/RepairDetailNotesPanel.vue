<template>
  <section class="panel-card">
    <div class="panel-head">
      <h2>Notas ({{ notes.length }})</h2>
      <button class="btn-secondary" @click="emit('toggle-note-form')">
        {{ showNoteForm ? 'Cerrar nota' : 'Agregar nota' }}
      </button>
    </div>

    <div v-if="showNoteForm" class="form-grid panel-nested">
      <label>
        <span>Tipo</span>
        <select :value="newNoteType" @change="emit('update-note-field', { field: 'newNoteType', value: $event.target.value })">
          <option value="internal">internal</option>
          <option value="public">public</option>
          <option value="technical">technical</option>
        </select>
      </label>
      <label>
        <span>Nota</span>
        <textarea :value="newNote" rows="3" @input="emit('update-note-field', { field: 'newNote', value: $event.target.value })"></textarea>
      </label>
      <div class="field-actions">
        <button class="btn-primary" :disabled="savingNote" @click="emit('add-note')">
          {{ savingNote ? 'Guardando...' : 'Guardar nota' }}
        </button>
      </div>
    </div>

    <p v-if="notes.length === 0" class="empty-state">Sin notas registradas.</p>
    <div v-else class="notes-list">
      <article v-for="note in notes" :key="note.id" class="note-card" :class="noteTypeClass(note.note_type)">
        <header>
          <strong>{{ note.note_type }}</strong>
          <small>{{ formatDate(note.created_at) }}</small>
        </header>
        <p>{{ note.note }}</p>
      </article>
    </div>
  </section>
</template>

<script setup>
defineProps({
  notes: {
    type: Array,
    default: () => []
  },
  showNoteForm: {
    type: Boolean,
    default: false
  },
  newNote: {
    type: String,
    default: ''
  },
  newNoteType: {
    type: String,
    default: 'internal'
  },
  savingNote: {
    type: Boolean,
    default: false
  },
  noteTypeClass: {
    type: Function,
    required: true
  },
  formatDate: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['toggle-note-form', 'update-note-field', 'add-note'])
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/repairDetailAdminShared.css"></style>
