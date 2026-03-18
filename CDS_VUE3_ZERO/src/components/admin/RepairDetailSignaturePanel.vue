<template>
  <section class="panel-card">
    <h2>Firma y foto de cliente</h2>
    <div class="action-grid">
      <button class="btn-secondary" :disabled="performingAction" @click="emit('request-signature', 'ingreso')">Solicitar firma ingreso</button>
      <button class="btn-secondary" :disabled="performingAction" @click="emit('request-signature', 'retiro')">Solicitar firma retiro</button>
      <button class="btn-secondary" :disabled="performingAction" @click="emit('request-photo-upload')">Solicitar foto cliente</button>
    </div>
    <p><strong>Firma ingreso:</strong> {{ repair?.signature_ingreso_path ? 'OK' : 'Pendiente' }}</p>
    <p><strong>Firma retiro:</strong> {{ repair?.signature_retiro_path ? 'OK' : 'Pendiente' }}</p>
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
  photoUploadLink: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['request-signature', 'request-photo-upload'])
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/repairDetailAdminShared.css"></style>
