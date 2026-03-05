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
