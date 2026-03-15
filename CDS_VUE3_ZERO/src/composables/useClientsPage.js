import { onMounted, ref, watch } from 'vue'
import { useClientManagement } from './useClientManagement'
import { useDeviceManagement } from './useDeviceManagement'
import { useRepairManagement } from './useRepairManagement'

export function useClientsPage() {
  const selectedClientId = ref(0)
  const loading = ref(false)
  const contextLoading = ref(false)
  const error = ref('')

  async function loadSelectedClientContext() {
    if (!Number(selectedClientId.value)) {
      deviceMgr.devices.value = []
      repairMgr.clearRepairs()
      return
    }

    contextLoading.value = true

    try {
      await Promise.all([
        deviceMgr.loadDevices(selectedClientId.value),
        repairMgr.loadRepairs(selectedClientId.value)
      ])

      const hasCurrentDevice = deviceMgr.devices.value.some(
        (d) => Number(d.id) === Number(repairMgr.repairForm.value.device_id || 0)
      )
      if (!hasCurrentDevice) {
        repairMgr.repairForm.value.device_id = deviceMgr.devices.value[0]?.id || ''
      }
    } catch {
      deviceMgr.devices.value = []
      repairMgr.clearRepairs()
    } finally {
      contextLoading.value = false
    }
  }

  const clientMgr = useClientManagement({
    selectedClientId,
    loading,
    error,
    onClientDeleted: async () => {
      deviceMgr.devices.value = []
      repairMgr.clearRepairs()
    }
  })

  const deviceMgr = useDeviceManagement({
    selectedClientId,
    contextLoading,
    error,
    onDeviceCreated: loadSelectedClientContext
  })

  const repairMgr = useRepairManagement({
    selectedClientId,
    contextLoading,
    error,
    devices: deviceMgr.devices,
    onRepairCreated: async () => {
      await Promise.all([loadSelectedClientContext(), clientMgr.loadClients()])
    }
  })

  watch(selectedClientId, async () => {
    clientMgr.resetEditForm()
    await loadSelectedClientContext()
  })

  onMounted(async () => {
    await clientMgr.loadClients()
    await loadSelectedClientContext()
  })

  return {
    // client
    clients: clientMgr.clients,
    loading,
    contextLoading,
    error,
    searchQuery: clientMgr.searchQuery,
    selectedClientId,
    selectedClient: clientMgr.selectedClient,
    filteredClients: clientMgr.filteredClients,
    showCreateForm: clientMgr.showCreateForm,
    showEditForm: clientMgr.showEditForm,
    createForm: clientMgr.createForm,
    editForm: clientMgr.editForm,
    selectClient: clientMgr.selectClient,
    toggleCreateForm: clientMgr.toggleCreateForm,
    toggleEditForm: clientMgr.toggleEditForm,
    loadClients: clientMgr.loadClients,
    createClient: clientMgr.createClient,
    updateSelectedClient: clientMgr.updateSelectedClient,
    deleteSelectedClient: clientMgr.deleteSelectedClient,
    // device
    devices: deviceMgr.devices,
    showDeviceForm: deviceMgr.showDeviceForm,
    deviceForm: deviceMgr.deviceForm,
    toggleDeviceForm: deviceMgr.toggleDeviceForm,
    createDeviceForSelectedClient: deviceMgr.createDeviceForSelectedClient,
    // repair
    repairs: repairMgr.repairs,
    showRepairForm: repairMgr.showRepairForm,
    repairForm: repairMgr.repairForm,
    toggleRepairForm: repairMgr.toggleRepairForm,
    createRepairForSelectedClient: repairMgr.createRepairForSelectedClient
  }
}
