<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Clientes</h1>
        <p>Gestion de clientes, dispositivos y ordenes de trabajo.</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" :disabled="loading" @click="loadClients">
          {{ loading ? 'Actualizando...' : 'Actualizar' }}
        </button>
        <button class="btn-primary" :disabled="loading" @click="toggleCreateForm">
          {{ showCreateForm ? 'Cerrar ingreso' : 'Nuevo cliente' }}
        </button>
        <button class="btn-secondary" :disabled="!selectedClient" @click="toggleEditForm">
          {{ showEditForm ? 'Cerrar edicion' : 'Editar cliente' }}
        </button>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <ClientsCreatePanel
      v-if="showCreateForm"
      :form="createForm"
      :loading="loading"
      :address-field-ref="setCreateAddressRef"
      @update-field="updateCreateField"
      @submit="createClient"
    />

    <section class="panel-card">
      <div class="split-grid">
        <ClientsListPanel
          :search-query="searchQuery"
          :clients="filteredClients"
          :selected-client-id="selectedClientId"
          @update-search="searchQuery = $event"
          @select-client="selectClient"
        />

        <ClientsDetailPanel
          :selected-client="selectedClient"
          :loading="loading"
          :context-loading="contextLoading"
          :show-edit-form="showEditForm"
          :show-device-form="showDeviceForm"
          :show-repair-form="showRepairForm"
          :edit-form="editForm"
          :device-form="deviceForm"
          :editing-device-id="editingDeviceId"
          :editing-device-form="editingDeviceForm"
          :repair-form="repairForm"
          :devices="devices"
          :repairs="repairs"
          :edit-address-ref="setEditAddressRef"
          @toggle-device-form="toggleDeviceForm"
          @toggle-repair-form="toggleRepairForm"
          @delete-client="deleteSelectedClient"
          @update-client="updateSelectedClient"
          @create-device="createDeviceForSelectedClient"
          @start-device-edit="startDeviceEdit"
          @cancel-device-edit="cancelDeviceEdit"
          @save-device="saveDeviceForSelectedClient"
          @delete-device="deleteDeviceForSelectedClient"
          @create-repair="createRepairForSelectedClient"
          @update-edit-field="updateEditField"
          @update-device-field="updateDeviceField"
          @update-editing-device-field="updateEditingDeviceField"
          @update-repair-field="updateRepairField"
        />
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, onUnmounted, watch } from 'vue'
import ClientsCreatePanel from '@/components/admin/ClientsCreatePanel.vue'
import ClientsDetailPanel from '@/components/admin/ClientsDetailPanel.vue'
import ClientsListPanel from '@/components/admin/ClientsListPanel.vue'
import { useClientsPage } from '@/composables/useClientsPage'
import { usePlacesAutocomplete } from '@/composables/usePlacesAutocomplete'

const {
  clients,
  devices,
  repairs,
  loading,
  contextLoading,
  error,
  searchQuery,
  selectedClientId,
  selectedClient,
  filteredClients,
  showCreateForm,
  showEditForm,
  showDeviceForm,
  showRepairForm,
  createForm,
  editForm,
  deviceForm,
  editingDeviceId,
  editingDeviceForm,
  repairForm,
  selectClient,
  toggleCreateForm,
  toggleEditForm,
  toggleDeviceForm,
  toggleRepairForm,
  loadClients,
  createClient,
  updateSelectedClient,
  deleteSelectedClient,
  createDeviceForSelectedClient,
  startDeviceEdit,
  cancelDeviceEdit,
  saveDeviceForSelectedClient,
  deleteDeviceForSelectedClient,
  createRepairForSelectedClient
} = useClientsPage()

const { initAutocomplete } = usePlacesAutocomplete()
const createAddressRef = ref(null)
const editAddressRef = ref(null)
let _cleanupCreate = () => {}
let _cleanupEdit = () => {}

function setCreateAddressRef(element) {
  createAddressRef.value = element
}

function setEditAddressRef(element) {
  editAddressRef.value = element
}

function updateCreateField({ field, value }) {
  createForm.value[field] = value
}

function updateEditField({ field, value }) {
  editForm.value[field] = value
}

function updateDeviceField({ field, value }) {
  deviceForm.value[field] = value
}

function updateEditingDeviceField({ field, value }) {
  editingDeviceForm.value[field] = value
}

function updateRepairField({ field, value }) {
  repairForm.value[field] = value
}

watch(
  () => createAddressRef.value,
  async (el) => {
    _cleanupCreate()
    if (el) {
      _cleanupCreate = await initAutocomplete(el, ({ address, city, region, country }) => {
        createForm.value.address = address
        if (city) createForm.value.city = city
        if (region) createForm.value.region = region
        if (country) createForm.value.country = country
      })
    }
  }
)

// Re-attach when edit form becomes visible (input renders lazily)
watch(
  () => editAddressRef.value,
  async (el) => {
    _cleanupEdit()
    if (el) {
      _cleanupEdit = await initAutocomplete(el, ({ address, city, region, country }) => {
        editForm.value.address = address
        if (city) editForm.value.city = city
        if (region) editForm.value.region = region
        if (country) editForm.value.country = country
      })
    }
  }
)

onUnmounted(() => { _cleanupCreate(); _cleanupEdit() })
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped src="./clientsPageShared.css"></style>
