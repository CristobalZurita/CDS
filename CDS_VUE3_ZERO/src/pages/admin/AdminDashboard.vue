<template>
  <AdminLayout title="Admin Dashboard" subtitle="Panel de control administrativo">
    <!-- Stats Cards -->
    <StatsCards :stats="stats" />
    
    <!-- KPI Zones -->
    <KpiZones
      :summary="kpiSummary"
      :dashboard="kpiDashboard"
      :revenue="kpiRevenue"
      :inventory="kpiInventory"
      :clients="kpiClients"
      :warranty="kpiWarranty"
    />
    
    <!-- Recent Repairs -->
    <section class="admin-section">
      <div class="section-header">
        <h2 class="section-title">🔧 Últimas Reparaciones</h2>
        <router-link to="/admin/repairs" class="btn-link">Ver todas</router-link>
      </div>
      <RepairsList />
    </section>
    
    <!-- Users Management -->
    <section class="admin-section">
      <div class="section-header">
        <h2 class="section-title">👤 Gestión de Usuarios</h2>
        <button class="btn-primary" @click="toggleUserForm">
          {{ showUserForm ? 'Cancelar' : 'Nuevo Usuario' }}
        </button>
      </div>
      
      <div v-if="showUserForm" class="user-form-card">
        <h4>{{ selectedUser ? 'Editar usuario' : 'Crear usuario' }}</h4>
        <UserForm :user="selectedUser" @saved="onUserSaved" />
      </div>
      
      <UserList :key="userRefreshKey" @edit="onEditUser" />
    </section>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import AdminLayout from '@/components/admin/layout/AdminLayout.vue'
import StatsCards from '@/components/admin/StatsCards.vue'
import KpiZones from '@/components/admin/KpiZones.vue'
import RepairsList from '@/components/admin/RepairsList.vue'
import UserList from '@/components/admin/UserList.vue'
import UserForm from '@/components/admin/UserForm.vue'

const stats = ref({})
const kpiSummary = ref({})
const kpiDashboard = ref({})
const kpiRevenue = ref({})
const kpiInventory = ref({})
const kpiClients = ref({})
const kpiWarranty = ref({})

const showUserForm = ref(false)
const selectedUser = ref(null)
const userRefreshKey = ref(0)

const safeData = (result, fallback = {}) => {
  if (result.status !== 'fulfilled') return fallback
  return result.value || fallback
}

async function loadStats() {
  const [
    statsRes,
    summaryRes,
    dashboardRes,
    revenueRes,
    inventoryRes,
    clientsRes,
    warrantyRes
  ] = await Promise.allSettled([
    api.get('/stats', { params: { extended: true } }),
    api.get('/analytics/kpis/summary'),
    api.get('/analytics/dashboard'),
    api.get('/analytics/revenue'),
    api.get('/analytics/inventory'),
    api.get('/analytics/clients'),
    api.get('/analytics/warranties')
  ])

  stats.value = safeData(statsRes, {})
  kpiSummary.value = safeData(summaryRes, {})
  kpiDashboard.value = safeData(dashboardRes, {})
  kpiRevenue.value = safeData(revenueRes, {})
  kpiInventory.value = safeData(inventoryRes, {})
  kpiClients.value = safeData(clientsRes, {})
  kpiWarranty.value = safeData(warrantyRes, {})
}

onMounted(loadStats)

function onUserSaved() {
  showUserForm.value = false
  selectedUser.value = null
  userRefreshKey.value += 1
}

function toggleUserForm() {
  if (showUserForm.value) {
    showUserForm.value = false
    selectedUser.value = null
    return
  }
  selectedUser.value = null
  showUserForm.value = true
}

function onEditUser(user) {
  selectedUser.value = user
  showUserForm.value = true
}
</script>

<style scoped>
.admin-section {
  background: var(--color-white, #fff);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.section-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-dark, #1a1a2e);
}

.btn-link {
  color: var(--color-primary, #ff6b35);
  text-decoration: none;
  font-weight: 600;
}

.btn-link:hover {
  text-decoration: underline;
}

.btn-primary {
  padding: 0.5rem 1rem;
  background: var(--color-primary, #ff6b35);
  color: var(--color-white, #fff);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: opacity 0.2s;
}

.btn-primary:hover {
  opacity: 0.9;
}

.user-form-card {
  background: var(--color-bg, #f5f5f5);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.user-form-card h4 {
  margin: 0 0 1rem 0;
  color: var(--color-dark, #1a1a2e);
}
</style>
