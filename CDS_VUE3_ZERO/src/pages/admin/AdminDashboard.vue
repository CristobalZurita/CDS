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
import { ref } from 'vue'
import KpiZones from '@/components/admin/KpiZones.vue'
import RepairsList from '@/components/admin/RepairsList.vue'
import UserList from '@/components/admin/UserList.vue'
import UserForm from '@/components/admin/UserForm.vue'
import { useAdminDashboardPage } from '@/composables/useAdminDashboardPage'

const {
  stats,
  kpiSummary,
  kpiDashboard,
  kpiRevenue,
  kpiInventory,
  kpiClients,
  kpiWarranty,
} = useAdminDashboardPage()

const showUserForm = ref(false)
const selectedUser = ref(null)
const userRefreshKey = ref(0)

const formatNumber = (val) => {
  const num = Number(val)
  return Number.isFinite(num) ? num.toLocaleString('es-CL') : '0'
}

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
  max-width: 1880px;
  margin: 0 auto;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: var(--admin-space-lg, 1.8rem);
  margin-bottom: var(--admin-space-xl, 2.4rem);
}

.stat-card {
  background: var(--cds-white);
  border-radius: var(--cds-radius-lg);
  padding: var(--admin-space-xl, 2.4rem);
  display: flex;
  align-items: center;
  gap: var(--admin-space-md, 1.2rem);
  box-shadow: var(--cds-shadow-sm);
  border: 1px solid var(--cds-border-card);
}

.stat-icon {
  font-size: var(--cds-text-3xl);
  width: 6rem;
  height: 6rem;
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
  font-size: var(--cds-text-4xl);
  font-weight: 700;
  color: var(--cds-text-normal);
  line-height: 1;
}

.stat-label {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.content-section {
  background: var(--cds-white);
  border-radius: var(--cds-radius-lg);
  padding: var(--admin-space-xl, 2.4rem);
  margin-bottom: var(--admin-space-lg, 1.8rem);
  box-shadow: var(--cds-shadow-sm);
  border: 1px solid var(--cds-border-card);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--admin-space-lg, 1.8rem);
  flex-wrap: wrap;
  gap: var(--admin-space-md, 1.2rem);
}

.section-header h2 {
  margin: 0;
  font-size: var(--cds-text-2xl);
  font-weight: 600;
  color: var(--cds-text-normal);
}

.btn-link {
  color: var(--cds-primary);
  text-decoration: none;
  font-weight: 500;
  font-size: var(--cds-text-base);
}

.btn-link:hover {
  text-decoration: underline;
}

.btn-primary {
  min-height: var(--admin-control-min-height, 52px);
  padding: 0.95rem 1.9rem;
  background: var(--cds-primary);
  color: var(--cds-white);
  border: none;
  border-radius: var(--cds-radius-md);
  cursor: pointer;
  font-weight: 500;
  font-size: var(--cds-text-base);
  transition: background 0.2s;
}

.btn-primary:hover {
  background: color-mix(in srgb, var(--cds-primary) 85%, black);
}

.form-panel {
  background: var(--cds-light-1);
  border-radius: var(--cds-radius-md);
  padding: var(--admin-space-xl, 2.4rem);
  margin-bottom: var(--admin-space-lg, 1.8rem);
  border: 1px solid var(--cds-border-card);
}

.form-panel h3 {
  margin: 0 0 var(--admin-space-md, 1.2rem) 0;
  font-size: var(--cds-text-xl);
  font-weight: 600;
  color: var(--cds-text-normal);
}
</style>
