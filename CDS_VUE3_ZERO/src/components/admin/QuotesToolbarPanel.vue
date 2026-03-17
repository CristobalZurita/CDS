<template>
  <section class="panel-card toolbar-grid">
    <label>
      <span>Buscar</span>
      <input
        :value="searchQuery"
        type="search"
        placeholder="COT, cliente o problema"
        @input="emit('update:searchQuery', $event.target.value)"
        @keyup.enter="emit('refresh')"
      />
    </label>

    <label>
      <span>Estado</span>
      <select :value="statusFilter" @change="emit('update:statusFilter', $event.target.value); emit('refresh')">
        <option value="">Todos</option>
        <option v-for="option in statusOptions" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>
    </label>

    <label class="checkbox-row">
      <input :checked="sendWhatsapp" type="checkbox" @change="emit('update:sendWhatsapp', $event.target.checked)" />
      <span>Enviar tambien por WhatsApp</span>
    </label>

    <label class="full">
      <span>Mensaje opcional de envio</span>
      <input
        :value="customMessage"
        type="text"
        placeholder="Mensaje para cliente"
        @input="emit('update:customMessage', $event.target.value)"
      />
    </label>
  </section>
</template>

<script setup>
defineProps({
  searchQuery: {
    type: String,
    default: ''
  },
  statusFilter: {
    type: String,
    default: ''
  },
  customMessage: {
    type: String,
    default: ''
  },
  sendWhatsapp: {
    type: Boolean,
    default: true
  },
  statusOptions: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits([
  'update:searchQuery',
  'update:statusFilter',
  'update:customMessage',
  'update:sendWhatsapp',
  'refresh'
])
</script>

<style scoped src="@/pages/admin/commonAdminPage.css"></style>
<style scoped src="@/pages/admin/quotesPageShared.css"></style>
