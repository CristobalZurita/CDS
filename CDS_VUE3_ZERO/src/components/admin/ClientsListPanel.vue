<template>
  <aside class="list-panel">
    <div class="toolbar">
      <label>
        <span>Buscar cliente</span>
        <input :value="searchQuery" type="search" placeholder="Nombre, codigo, email o telefono" @input="emit('update-search', $event.target.value)" />
      </label>
    </div>

    <h3>Listado</h3>
    <p v-if="clients.length === 0" class="empty-state">Sin clientes para el filtro actual.</p>
    <ul v-else class="list-reset">
      <li
        v-for="client in clients"
        :key="client.id"
        :class="['list-item', { active: selectedClientId === client.id }]"
        @click="emit('select-client', client)"
      >
        <div class="item-head">
          <strong>{{ client.name || `Cliente #${client.id}` }}</strong>
          <span class="chip">{{ client.client_code || `#${client.id}` }}</span>
        </div>
        <small>{{ client.email || 'Sin email' }}</small>
      </li>
    </ul>
  </aside>
</template>

<script setup>
defineProps({
  searchQuery: {
    type: String,
    default: ''
  },
  clients: {
    type: Array,
    default: () => []
  },
  selectedClientId: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update-search', 'select-client'])
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/clientsPageShared.css"></style>
