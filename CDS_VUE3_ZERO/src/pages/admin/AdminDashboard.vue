<template>
  <div class="admin-dashboard-page">
    <!-- Stats Cards -->
    <section class="stats-section">
      <div class="stat-card">
        <div class="stat-icon">👤</div>
        <div class="stat-info">
          <span class="stat-value">{{ formatNumber(stats.users) }}</span>
          <span class="stat-label">Usuarios</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏢</div>
        <div class="stat-info">
          <span class="stat-value">{{ formatNumber(stats.clients) }}</span>
          <span class="stat-label">Clientes</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🔧</div>
        <div class="stat-info">
          <span class="stat-value">{{ formatNumber(stats.repairs) }}</span>
          <span class="stat-label">Reparaciones</span>
        </div>
      </div>
    </section>
    
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
    <section class="content-section">
      <div class="section-header">
        <h2>Últimas Reparaciones</h2>
        <router-link to="/admin/repairs" class="btn-link">Ver todas →</router-link>
      </div>
      <RepairsList />
    </section>
    
    <!-- Users Management -->
    <section class="content-section">
      <div class="section-header">
        <h2>Gestión de Usuarios</h2>
        <button class="btn-primary" @click="toggleUserForm">
          {{ showUserForm ? 'Cancelar' : '+ Nuevo Usuario' }}
        </button>
      </div>
      
      <div v-if="showUserForm" class="form-panel">
        <h3>{{ selectedUser ? 'Editar usuario' : 'Crear usuario' }}</h3>
        <UserForm :user="selectedUser" @saved="onUserSaved" />
      </div>
      
      <UserList :key="userRefreshKey" @edit="onEditUser" />
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
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

const formatNumber = (val) => {
  const num = Number(val)
  return Number.isFinite(num) ? num.toLocaleString('es-CL') : '0'
}

const safeData = (result, fallback = {}) => {
  if (result.status !== 'fulfilled') return fallback
  return result.value?.data || result.value || fallback
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
.admin-dashboard-page {
  max-width: 1760px;
  margin: 0 auto;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2.2rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: var(--cds-white);
  border-radius: var(--cds-radius-lg);
  padding: 2.2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  box-shadow: var(--cds-shadow-sm);
  border: 1px solid var(--cds-light-2);
}

.stat-icon {
  font-size: 3rem;
  width: 5.2rem;
  height: 5.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--cds-primary) 0%, var(--cds-orange-pastel) 100%);
  border-radius: var(--cds-radius-lg);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 3rem;
  font-weight: 700;
  color: var(--cds-text-normal);
  line-height: 1.2;
}

.stat-label {
  font-size: 1.5rem;
  color: var(--cds-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.content-section {
  background: var(--cds-white);
  border-radius: var(--cds-radius-lg);
  padding: 2.2rem;
  margin-bottom: 2.2rem;
  box-shadow: var(--cds-shadow-sm);
  border: 1px solid var(--cds-light-2);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.9rem;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.section-header h2 {
  margin: 0;
  font-size: 1.65rem;
  font-weight: 600;
  color: var(--cds-text-normal);
}

.btn-link {
  color: var(--cds-primary);
  text-decoration: none;
  font-weight: 500;
  font-size: 1.3rem;
}

.btn-link:hover {
  text-decoration: underline;
}

.btn-primary {
  padding: 0.95rem 1.9rem;
  background: var(--cds-primary);
  color: var(--cds-white);
  border: none;
  border-radius: var(--cds-radius-md);
  cursor: pointer;
  font-weight: 500;
  font-size: 1.3rem;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: color-mix(in srgb, var(--cds-primary) 85%, black);
}

.form-panel {
  background: var(--cds-light-1);
  border-radius: var(--cds-radius-md);
  padding: 2.2rem;
  margin-bottom: 2.2rem;
  border: 1px solid var(--cds-light-2);
}

.form-panel h3 {
  margin: 0 0 1.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--cds-text-normal);
}
</style>
