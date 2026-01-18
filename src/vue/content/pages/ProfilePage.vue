<template>
  <div class="profile-page">
    <div class="profile-container">
      <!-- Header -->
      <div class="profile-header">
        <div class="header-content">
          <div class="avatar">{{ userInitials }}</div>
          <div>
            <h1>{{ user.fullName }}</h1>
            <p class="subtitle">Cliente desde {{ memberSince }}</p>
          </div>
        </div>
        <button @click="editMode = !editMode" class="btn-edit">
          {{ editMode ? '✕ Cancelar' : '✏️ Editar Perfil' }}
        </button>
      </div>

      <!-- Main Content -->
      <div class="profile-content">
        <!-- Left Column: Personal Info -->
        <div class="column">
          <div class="card">
            <h2>Información Personal</h2>

            <div class="form-group" v-if="!editMode">
              <label>Email</label>
              <p class="value">{{ user.email }}</p>
            </div>
            <div class="form-group" v-else>
              <label>Email</label>
              <input v-model="formData.email" type="email" class="form-input" />
            </div>

            <div class="form-group" v-if="!editMode">
              <label>Nombre Completo</label>
              <p class="value">{{ user.fullName }}</p>
            </div>
            <div class="form-group" v-else>
              <label>Nombre Completo</label>
              <input v-model="formData.fullName" type="text" class="form-input" />
            </div>

            <div class="form-group" v-if="!editMode">
              <label>Teléfono</label>
              <p class="value">{{ user.phone || '—' }}</p>
            </div>
            <div class="form-group" v-else>
              <label>Teléfono</label>
              <input v-model="formData.phone" type="tel" class="form-input" />
            </div>

            <div class="form-group" v-if="!editMode">
              <label>Dirección</label>
              <p class="value">{{ user.address || '—' }}</p>
            </div>
            <div class="form-group" v-else>
              <label>Dirección</label>
              <input v-model="formData.address" type="text" class="form-input" />
            </div>

            <div class="form-group" v-if="editMode">
              <button @click="saveProfile" class="btn-save">Guardar Cambios</button>
            </div>
          </div>

          <div class="card">
            <h2>Preferencias</h2>

            <label class="checkbox-label">
              <input v-model="preferences.emailNotifications" type="checkbox" />
              <span>Recibir notificaciones por email</span>
            </label>

            <label class="checkbox-label">
              <input v-model="preferences.whatsappNotifications" type="checkbox" />
              <span>Recibir actualizaciones por WhatsApp</span>
            </label>

            <label class="checkbox-label">
              <input v-model="preferences.smsNotifications" type="checkbox" />
              <span>Recibir SMS de recordatorios</span>
            </label>

            <button @click="savePreferences" class="btn-save mt">
              Guardar Preferencias
            </button>
          </div>
        </div>

        <!-- Right Column: Stats & Actions -->
        <div class="column">
          <div class="stats-card">
            <h3>Estadísticas</h3>
            <div class="stat">
              <span class="stat-value">{{ totalRepairs }}</span>
              <span class="stat-label">Reparaciones totales</span>
            </div>
            <div class="stat">
              <span class="stat-value">${{ totalSpent }}</span>
              <span class="stat-label">Total invertido</span>
            </div>
            <div class="stat">
              <span class="stat-value">{{ avgRepairDays }} días</span>
              <span class="stat-label">Promedio reparación</span>
            </div>
          </div>

          <div class="card">
            <h2>Seguridad</h2>

            <button @click="showChangePassword = true" class="btn-secondary">
              🔐 Cambiar contraseña
            </button>

            <button @click="showTwoFactorSetup = true" class="btn-secondary">
              🛡️ Configurar 2FA
            </button>

            <p style="font-size: 0.85rem; color: #718096; margin-top: 1rem;">
              Última actividad: hace 2 horas
            </p>
          </div>

          <div class="card danger">
            <h2>Zona de Peligro</h2>
            <p style="color: #742a2a; margin-bottom: 1rem;">
              Estas acciones no se pueden deshacer
            </p>
            <button @click="showDeleteAccount = true" class="btn-danger">
              🗑️ Eliminar cuenta
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <div v-if="showChangePassword" class="modal-overlay" @click="showChangePassword = false">
      <div class="modal" @click.stop>
        <h3>Cambiar Contraseña</h3>
        <div class="form-group">
          <label>Contraseña actual</label>
          <input v-model="passwordForm.current" type="password" class="form-input" />
        </div>
        <div class="form-group">
          <label>Nueva contraseña</label>
          <input v-model="passwordForm.new" type="password" class="form-input" />
        </div>
        <div class="form-group">
          <label>Confirmar contraseña</label>
          <input v-model="passwordForm.confirm" type="password" class="form-input" />
        </div>
        <div class="modal-actions">
          <button @click="showChangePassword = false" class="btn-secondary">Cancelar</button>
          <button @click="changePassword" class="btn-primary">Cambiar</button>
        </div>
      </div>
    </div>

    <div v-if="showDeleteAccount" class="modal-overlay" @click="showDeleteAccount = false">
      <div class="modal danger" @click.stop>
        <h3>⚠️ Eliminar Cuenta</h3>
        <p>
          ¿Estás seguro de que deseas eliminar tu cuenta? Esta acción es irreversible y se
          eliminarán todos tus datos.
        </p>
        <div class="modal-actions">
          <button @click="showDeleteAccount = false" class="btn-secondary">Cancelar</button>
          <button @click="deleteAccount" class="btn-danger">Eliminar Permanentemente</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/services/api'
import { showSuccess, showError } from '@/services/toastService'

const editMode = ref(false)
const isLoading = ref(false)

const user = ref({
  email: '',
  fullName: '',
  phone: '',
  address: '',
  joinDate: null
})

const formData = ref({
  email: '',
  fullName: '',
  phone: '',
  address: ''
})

const stats = ref({
  totalRepairs: 0,
  totalSpent: 0
})

// Preferences
const preferences = ref({
  emailNotifications: true,
  whatsappNotifications: true,
  smsNotifications: false
})

// Modals
const showChangePassword = ref(false)
const showTwoFactorSetup = ref(false)
const showDeleteAccount = ref(false)

const passwordForm = ref({
  current: '',
  new: '',
  confirm: ''
})

// Computed
const userInitials = computed(() => {
  const names = (user.value.fullName || '').split(' ')
  return (names[0]?.[0] || '') + (names[1]?.[0] || '')
})

const memberSince = computed(() => {
  if (!user.value.joinDate) return '—'
  return new Intl.DateTimeFormat('es-CL', {
    year: 'numeric',
    month: 'long'
  }).format(new Date(user.value.joinDate))
})

const totalRepairs = computed(() => stats.value.totalRepairs)
const totalSpent = computed(() => stats.value.totalSpent)
const avgRepairDays = computed(() => 10)

const syncFormData = () => {
  formData.value = {
    email: user.value.email,
    fullName: user.value.fullName,
    phone: user.value.phone,
    address: user.value.address
  }
}

const loadProfile = async () => {
  isLoading.value = true
  try {
    const { data } = await api.get('/client/profile')
    user.value = {
      email: data.email || '',
      fullName: data.full_name || '',
      phone: data.phone || '',
      address: data.address || '',
      joinDate: data.member_since
    }
    stats.value = {
      totalRepairs: data.stats?.total_repairs || 0,
      totalSpent: data.stats?.total_spent || 0
    }
    syncFormData()
  } catch (err) {
    showError(err.response?.data?.detail || 'Error cargando perfil')
  } finally {
    isLoading.value = false
  }
}

// Methods
const saveProfile = async () => {
  isLoading.value = true
  try {
    const payload = {
      email: formData.value.email,
      full_name: formData.value.fullName,
      phone: formData.value.phone,
      address: formData.value.address
    }
    const { data } = await api.put('/client/profile', payload)
    user.value = {
      email: data.email || '',
      fullName: data.full_name || '',
      phone: data.phone || '',
      address: data.address || '',
      joinDate: data.member_since
    }
    stats.value = {
      totalRepairs: data.stats?.total_repairs || 0,
      totalSpent: data.stats?.total_spent || 0
    }
    editMode.value = false
    syncFormData()
    showSuccess('Perfil actualizado exitosamente')
  } catch (err) {
    showError(err.response?.data?.detail || 'Error guardando perfil')
  } finally {
    isLoading.value = false
  }
}

const savePreferences = () => {
  showSuccess('Preferencias guardadas')
}

const changePassword = () => {
  if (passwordForm.value.new !== passwordForm.value.confirm) {
    showError('Las contraseñas no coinciden')
    return
  }
  showSuccess('Contraseña cambiada exitosamente')
  showChangePassword.value = false
  passwordForm.value = { current: '', new: '', confirm: '' }
}

const deleteAccount = () => {
  showSuccess('Cuenta eliminada (demo)')
  showDeleteAccount.value = false
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem 1rem;
}

.profile-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* Header */
.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: 700;
}

.profile-header h1 {
  margin: 0 0 0.25rem 0;
  color: #2d3748;
  font-size: 1.8rem;
}

.subtitle {
  margin: 0;
  color: #718096;
  font-size: 0.95rem;
}

.btn-edit {
  padding: 0.75rem 1.5rem;
  background: #edf2f7;
  border: 2px solid #cbd5e0;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  color: #4a5568;
  transition: all 0.2s;
}

.btn-edit:hover {
  background: #e2e8f0;
  border-color: #a0aec0;
}

/* Content */
.profile-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.card h2 {
  margin: 0 0 1.5rem 0;
  color: #2d3748;
  font-size: 1.2rem;
}

.card.danger {
  border-left: 4px solid #f56565;
}

/* Form */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #4a5568;
  font-size: 0.9rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  font-size: 1rem;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group .value {
  margin: 0;
  color: #2d3748;
  font-size: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  cursor: pointer;
  color: #4a5568;
}

.checkbox-label input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

/* Stats */
.stats-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stats-card h3 {
  margin: 0 0 1.5rem 0;
  color: #2d3748;
  font-size: 1.2rem;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.stat:last-child {
  border-bottom: none;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #667eea;
}

.stat-label {
  font-size: 0.85rem;
  color: #718096;
}

/* Buttons */
.btn-save,
.btn-secondary,
.btn-primary,
.btn-danger {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 0.75rem;
}

.btn-save {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #edf2f7;
  color: #4a5568;
  border: 2px solid #cbd5e0;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

.btn-danger {
  background: #fed7d7;
  color: #742a2a;
  border: 2px solid #fc8181;
}

.btn-danger:hover {
  background: #fc8181;
  color: white;
}

.mt {
  margin-top: 1rem;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal h3 {
  margin: 0 0 1.5rem 0;
  color: #2d3748;
  font-size: 1.3rem;
}

.modal p {
  color: #718096;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
}

.modal-actions button {
  flex: 1;
}

/* Responsive */
@media (max-width: 768px) {
  .profile-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .profile-page {
    padding: 1rem;
  }

  .profile-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1.5rem;
  }

  .header-content {
    flex-direction: column;
    gap: 1rem;
  }

  .btn-edit {
    width: 100%;
  }
}
</style>
