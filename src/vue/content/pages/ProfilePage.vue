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
        <button @click="editMode = !editMode" class="btn-edit" data-testid="profile-edit-toggle">
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
              <input v-model="formData.email" type="email" class="form-input" data-testid="profile-email-input" />
            </div>

            <div class="form-group" v-if="!editMode">
              <label>Nombre Completo</label>
              <p class="value">{{ user.fullName }}</p>
            </div>
            <div class="form-group" v-else>
              <label>Nombre Completo</label>
              <input v-model="formData.fullName" type="text" class="form-input" data-testid="profile-name-input" />
            </div>

            <div class="form-group" v-if="!editMode">
              <label>Teléfono</label>
              <p class="value">{{ user.phone || '—' }}</p>
            </div>
            <div class="form-group" v-else>
              <label>Teléfono</label>
              <input v-model="formData.phone" type="tel" class="form-input" data-testid="profile-phone-input" />
            </div>

            <div class="form-group" v-if="!editMode">
              <label>Dirección</label>
              <p class="value">{{ user.address || '—' }}</p>
            </div>
            <div class="form-group" v-else>
              <label>Dirección</label>
              <input v-model="formData.address" type="text" class="form-input" data-testid="profile-address-input" />
            </div>

            <div class="form-group" v-if="editMode">
              <button @click="saveProfile" class="btn-save" data-testid="profile-save">Guardar Cambios</button>
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

            <button @click="savePreferences" class="btn-save mt" data-testid="profile-preferences-save">
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

            <button @click="showChangePassword = true" class="btn-secondary" data-testid="profile-open-password-modal">
              🔐 Cambiar contraseña
            </button>

            <button @click="showTwoFactorSetup = true" class="btn-secondary" data-testid="profile-open-2fa">
              🛡️ Configurar 2FA
            </button>

            <p class="last-activity">
              Última actividad: hace 2 horas
            </p>
          </div>

          <div class="card danger">
            <h2>Zona de Peligro</h2>
            <p class="danger-warning">
              Estas acciones no se pueden deshacer
            </p>
            <button @click="showDeleteAccount = true" class="btn-danger" data-testid="profile-open-delete-modal">
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
          <div class="password-field">
            <input v-model="passwordForm.current" :type="showPassword ? 'text' : 'password'" class="form-input" data-testid="profile-password-current" />
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              {{ showPassword ? 'Ocultar' : 'Mostrar' }}
            </button>
          </div>
        </div>
        <div class="form-group">
          <label>Nueva contraseña</label>
          <div class="password-field">
            <input v-model="passwordForm.new" :type="showPassword ? 'text' : 'password'" class="form-input" data-testid="profile-password-new" />
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              {{ showPassword ? 'Ocultar' : 'Mostrar' }}
            </button>
          </div>
        </div>
        <div class="form-group">
          <label>Confirmar contraseña</label>
          <div class="password-field">
            <input v-model="passwordForm.confirm" :type="showPassword ? 'text' : 'password'" class="form-input" data-testid="profile-password-confirm" />
            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
              {{ showPassword ? 'Ocultar' : 'Mostrar' }}
            </button>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="showChangePassword = false" class="btn-secondary" data-testid="profile-password-cancel">Cancelar</button>
          <button @click="changePassword" class="btn-primary" data-testid="profile-password-save">Cambiar</button>
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
          <button @click="showDeleteAccount = false" class="btn-secondary" data-testid="profile-delete-cancel">Cancelar</button>
          <button @click="deleteAccount" class="btn-danger" data-testid="profile-delete-confirm">Eliminar Permanentemente</button>
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
const showPassword = ref(false)

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

<style lang="scss" scoped>
@import "@/scss/_core.scss";

.profile-page {
  min-height: 100vh;
  background: linear-gradient(135deg, $light-1 0%, $light-3 100%);
  padding: $spacer-xl $spacer-md;
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
  background: $color-white;
  padding: $spacer-xl;
  border-radius: $border-radius-lg;
  margin-bottom: $spacer-xl;
  box-shadow: $shadow-md;
}

.header-content {
  display: flex;
  align-items: center;
  gap: $spacer-xl;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, $color-indigo-legacy, $color-purple-legacy);
  color: $color-white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $text-2xl;
  font-weight: $fw-bold;
}

.profile-header h1 {
  margin: 0 0 $spacer-xs 0;
  color: $text-color;
  font-size: $text-2xl;
}

.subtitle {
  margin: 0;
  color: $light-6;
  font-size: $text-base;
}

.btn-edit {
  padding: $spacer-sm $spacer-lg;
  background: $light-2;
  border: 2px solid $light-4;
  border-radius: $border-radius-md;
  cursor: pointer;
  font-weight: $fw-semibold;
  color: $text-color-muted;
  transition: $transition-fast;
}

.btn-edit:hover {
  background: $light-3;
  border-color: $light-5;
}

/* Content */
.profile-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $spacer-xl;
}

.password-field {
  display: flex;
  gap: $spacer-sm;
  align-items: center;
}

.toggle-password {
  border: 1px solid $light-4;
  background: $light-1;
  padding: $spacer-xs $spacer-sm;
  border-radius: $border-radius-sm;
  font-size: $text-sm;
}

.column {
  display: flex;
  flex-direction: column;
  gap: $spacer-xl;
}

.card {
  background: $color-white;
  border-radius: $border-radius-lg;
  padding: $spacer-xl;
  box-shadow: $shadow-md;
}

.card h2 {
  margin: 0 0 $spacer-lg 0;
  color: $text-color;
  font-size: $text-xl;
}

.card.danger {
  border-left: 4px solid $color-danger;
}

.last-activity {
  font-size: $text-sm;
  color: $light-6;
  margin-top: $spacer-md;
}

.danger-warning {
  color: $color-red-900-legacy;
  margin-bottom: $spacer-md;
}

/* Form */
.form-group {
  margin-bottom: $spacer-lg;
}

.form-group label {
  display: block;
  margin-bottom: $spacer-sm;
  font-weight: $fw-semibold;
  color: $text-color-muted;
  font-size: $text-sm;
}

.form-input {
  width: 100%;
  padding: $spacer-sm;
  border: 1px solid $light-4;
  border-radius: $border-radius-md;
  font-size: $text-base;
}

.form-input:focus {
  outline: none;
  border-color: $color-primary;
  box-shadow: 0 0 0 3px rgba($color-primary, 0.1);
}

.form-group .value {
  margin: 0;
  color: $text-color;
  font-size: $text-base;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: $spacer-sm;
  margin-bottom: $spacer-md;
  cursor: pointer;
  color: $text-color-muted;
}

.checkbox-label input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

/* Stats */
.stats-card {
  background: $color-white;
  border-radius: $border-radius-lg;
  padding: $spacer-xl;
  box-shadow: $shadow-md;
}

.stats-card h3 {
  margin: 0 0 $spacer-lg 0;
  color: $text-color;
  font-size: $text-xl;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: $spacer-sm;
  margin-bottom: $spacer-lg;
  padding-bottom: $spacer-lg;
  border-bottom: 1px solid $light-3;
}

.stat:last-child {
  border-bottom: none;
}

.stat-value {
  font-size: $text-2xl;
  font-weight: $fw-bold;
  color: $color-primary;
}

.stat-label {
  font-size: $text-sm;
  color: $light-6;
}

/* Buttons */
.btn-save,
.btn-secondary,
.btn-primary,
.btn-danger {
  width: 100%;
  padding: $spacer-sm;
  border: none;
  border-radius: $border-radius-md;
  font-weight: $fw-semibold;
  cursor: pointer;
  transition: $transition-fast;
  margin-bottom: $spacer-sm;
}

.btn-save {
  background: linear-gradient(135deg, $color-indigo-legacy, $color-purple-legacy);
  color: $color-white;
}

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: $shadow-md;
}

.btn-secondary {
  background: $light-2;
  color: $text-color-muted;
  border: 2px solid $light-4;
}

.btn-secondary:hover {
  background: $light-3;
}

.btn-danger {
  background: $color-red-200-legacy;
  color: $color-red-900-legacy;
  border: 2px solid $color-red-500-legacy;
}

.btn-danger:hover {
  background: $color-red-500-legacy;
  color: $color-white;
}

.mt {
  margin-top: $spacer-md;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba($color-black, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: $z-index-modal;
}

.modal {
  background: $color-white;
  border-radius: $border-radius-lg;
  padding: $spacer-xl;
  max-width: 500px;
  width: 100%;
  box-shadow: $shadow-xl;
}

.modal h3 {
  margin: 0 0 $spacer-lg 0;
  color: $text-color;
  font-size: $text-xl;
}

.modal p {
  color: $light-6;
  line-height: $lh-relaxed;
  margin-bottom: $spacer-lg;
}

.modal-actions {
  display: flex;
  gap: $spacer-md;
}

.modal-actions button {
  flex: 1;
}

/* Responsive */
@include media-breakpoint-down(md) {
  .profile-content {
    grid-template-columns: 1fr;
  }

  .profile-page {
    padding: $spacer-md;
  }

  .profile-header {
    flex-direction: column;
    align-items: flex-start;
    gap: $spacer-lg;
  }

  .header-content {
    flex-direction: column;
    gap: $spacer-md;
  }

  .btn-edit {
    width: 100%;
  }
}
</style>
