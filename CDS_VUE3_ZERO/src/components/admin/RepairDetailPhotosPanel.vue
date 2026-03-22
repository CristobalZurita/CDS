<template>
  <section class="panel-card">
    <div class="panel-head">
      <h2>Fotos ({{ photos.length }})</h2>
      <button class="btn-secondary" @click="emit('toggle-upload')">
        {{ showPhotoUpload ? 'Cerrar carga' : 'Agregar foto' }}
      </button>
    </div>

    <div v-if="showPhotoUpload" class="form-grid two-cols panel-nested">
      <label class="full"><span>Archivo</span><input type="file" accept="image/*" capture="environment" @change="emit('file-selected', $event)" /></label>
      <label>
        <span>Tipo</span>
        <select :value="newPhotoType" @change="emit('update-photo-field', { field: 'newPhotoType', value: $event.target.value })">
          <option value="general">general</option>
          <option value="before">before</option>
          <option value="after">after</option>
          <option value="damage">damage</option>
          <option value="component">component</option>
          <option value="client">client</option>
        </select>
      </label>
      <label>
        <span>Descripcion</span>
        <input :value="newPhotoCaption" type="text" placeholder="Descripcion opcional" @input="emit('update-photo-field', { field: 'newPhotoCaption', value: $event.target.value })" />
      </label>
      <div class="field-actions full">
        <button class="btn-primary" :disabled="uploadingPhoto || !selectedFile" @click="emit('upload-photo')">
          {{ uploadingPhoto ? 'Subiendo...' : 'Subir foto' }}
        </button>
      </div>
    </div>

    <p v-if="photos.length === 0" class="empty-state">Sin fotos registradas.</p>
    <div v-else class="photos-grid">
      <article v-for="photo in photos" :key="photo.id" class="photo-card">
        <img :src="photo.resolved_photo_url" :alt="photo.caption || 'Foto OT'" />
        <div class="photo-meta">
          <span>{{ photo.photo_type }}</span>
          <small>{{ photo.caption || 'Sin descripcion' }}</small>
          <small>{{ formatDate(photo.created_at) }}</small>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
defineProps({
  photos: {
    type: Array,
    default: () => []
  },
  showPhotoUpload: {
    type: Boolean,
    default: false
  },
  selectedFile: {
    type: Object,
    default: null
  },
  newPhotoCaption: {
    type: String,
    default: ''
  },
  newPhotoType: {
    type: String,
    default: 'general'
  },
  uploadingPhoto: {
    type: Boolean,
    default: false
  },
  formatDate: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['toggle-upload', 'file-selected', 'update-photo-field', 'upload-photo'])
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/repairDetailAdminShared.css"></style>
