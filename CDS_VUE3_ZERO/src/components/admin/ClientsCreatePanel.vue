<template>
  <section class="panel-card">
    <h2>Nuevo cliente</h2>
    <div class="form-grid two-cols">
      <label><span>Nombre *</span><input :value="form.name" type="text" @input="updateField('name', $event.target.value)" /></label>
      <label><span>Email</span><input :value="form.email" type="email" @input="updateField('email', $event.target.value)" /></label>
      <label><span>Telefono</span><input :value="form.phone" type="text" @input="updateField('phone', $event.target.value)" /></label>
      <label><span>Telefono alterno</span><input :value="form.phone_alt" type="text" @input="updateField('phone_alt', $event.target.value)" /></label>
      <label><span>Ciudad</span><input :value="form.city" type="text" @input="updateField('city', $event.target.value)" /></label>
      <label><span>Region</span><input :value="form.region" type="text" @input="updateField('region', $event.target.value)" /></label>
      <label><span>Pais</span><input :value="form.country" type="text" @input="updateField('country', $event.target.value)" /></label>
      <label class="full"><span>Direccion</span><input :ref="addressFieldRef" :value="form.address" type="text" @input="updateField('address', $event.target.value)" /></label>
      <label class="full"><span>Notas</span><textarea :value="form.notes" rows="3" @input="updateField('notes', $event.target.value)"></textarea></label>
    </div>
    <div class="panel-actions">
      <button class="btn-primary" :disabled="loading" @click="emit('submit')">
        {{ loading ? 'Guardando...' : 'Guardar cliente' }}
      </button>
    </div>
  </section>
</template>

<script setup>
const props = defineProps({
  form: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  addressFieldRef: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['update-field', 'submit'])

function updateField(field, value) {
  emit('update-field', { field, value })
}
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
