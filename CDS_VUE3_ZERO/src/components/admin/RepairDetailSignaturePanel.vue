<template>
  <section class="panel-card">
    <h2>Firma y foto de cliente</h2>
    <div class="action-grid">
      <button class="btn-secondary" :disabled="performingAction" @click="emit('request-signature', 'ingreso')">Solicitar firma ingreso</button>
      <button class="btn-secondary" :disabled="performingAction" @click="emit('request-signature', 'retiro')">Solicitar firma retiro</button>
      <button class="btn-secondary" :disabled="performingAction" @click="emit('request-photo-upload')">Solicitar foto cliente</button>
      <button
        v-if="signatureRequest?.id && signatureRequest?.status === 'pending'"
        class="btn-danger"
        :disabled="performingAction"
        @click="emit('cancel-signature')"
      >
        Cancelar solicitud firma
      </button>
    </div>
    <p><strong>Firma ingreso:</strong> {{ repair?.signature_ingreso_path ? 'OK' : 'Pendiente' }}</p>
    <p><strong>Firma retiro:</strong> {{ repair?.signature_retiro_path ? 'OK' : 'Pendiente' }}</p>
    <p v-if="signatureRequest"><strong>Solicitud firma:</strong> {{ signatureRequest.request_type || '—' }} · {{ signatureRequest.status || 'pending' }}</p>
    <p v-if="photoUploadRequest"><strong>Solicitud foto:</strong> {{ photoUploadRequest.photo_type || 'client' }} · {{ photoUploadRequest.status || 'pending' }}</p>
    <p v-if="signatureLink" class="link-line"><strong>Link firma:</strong> <a :href="signatureLink" target="_blank" rel="noopener">{{ signatureLink }}</a></p>
    <p v-if="photoUploadLink" class="link-line"><strong>Link foto:</strong> <a :href="photoUploadLink" target="_blank" rel="noopener">{{ photoUploadLink }}</a></p>
  </section>
</template>

<script setup>
defineProps({
  repair: {
    type: Object,
    default: null
  },
  performingAction: {
    type: Boolean,
    default: false
  },
  signatureLink: {
    type: String,
    default: ''
  },
  signatureRequest: {
    type: Object,
    default: null
  },
  photoUploadLink: {
    type: String,
    default: ''
  },
  photoUploadRequest: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['request-signature', 'request-photo-upload', 'cancel-signature'])
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/repairDetailAdminShared.css"></style>
