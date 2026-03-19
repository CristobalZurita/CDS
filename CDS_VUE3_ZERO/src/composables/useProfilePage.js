import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { extractErrorMessage } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

function normalizeProfilePayload(payload) {
  return {
    email: String(payload?.email || ''),
    fullName: String(payload?.full_name || ''),
    phone: String(payload?.phone || ''),
    address: String(payload?.address || ''),
    joinDate: payload?.member_since || null,
    stats: {
      totalRepairs: Number(payload?.stats?.total_repairs || 0),
      totalSpent: Number(payload?.stats?.total_spent || 0),
      avgRepairDays: payload?.stats?.avg_repair_days == null ? null : Number(payload.stats.avg_repair_days)
    }
  }
}

export function useProfilePage() {
  const router = useRouter()
  const authStore = useAuthStore()
  const editMode = ref(false)
  const isLoading = ref(false)
  const error = ref('')
  const success = ref('')

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
    totalSpent: 0,
    avgRepairDays: null
  })

  const preferences = ref({
    emailNotifications: true,
    whatsappNotifications: true,
    smsNotifications: false
  })

  const showChangePassword = ref(false)
  const showDeleteAccount = ref(false)
  const showPassword = ref(false)
  const passwordForm = ref({
    current: '',
    next: '',
    confirm: ''
  })

  const userInitials = computed(() => {
    const names = String(user.value.fullName || '').trim().split(/\s+/).filter(Boolean)
    if (names.length === 0) return 'CL'
    return `${names[0][0] || ''}${names[1]?.[0] || ''}`.toUpperCase()
  })

  const memberSince = computed(() => {
    if (!user.value.joinDate) return '—'
    const date = new Date(user.value.joinDate)
    if (Number.isNaN(date.getTime())) return '—'

    return new Intl.DateTimeFormat('es-CL', {
      year: 'numeric',
      month: 'long'
    }).format(date)
  })

  const totalRepairs = computed(() => Number(stats.value.totalRepairs || 0))
  const totalSpent = computed(() => {
    const amount = Number(stats.value.totalSpent || 0)
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  })

  const avgRepairDays = computed(() => {
    if (stats.value.avgRepairDays == null) return null
    const nextValue = Number(stats.value.avgRepairDays)
    return Number.isFinite(nextValue) ? nextValue : null
  })

  function resetMessages() {
    error.value = ''
    success.value = ''
  }

  function syncFormData() {
    formData.value = {
      email: user.value.email,
      fullName: user.value.fullName,
      phone: user.value.phone,
      address: user.value.address
    }
  }

  async function loadProfile() {
    isLoading.value = true
    resetMessages()

    try {
      const response = await api.get('/client/profile')
      const normalized = normalizeProfilePayload(response?.data || {})

      user.value = {
        email: normalized.email,
        fullName: normalized.fullName,
        phone: normalized.phone,
        address: normalized.address,
        joinDate: normalized.joinDate
      }

      stats.value = {
        totalRepairs: normalized.stats.totalRepairs,
        totalSpent: normalized.stats.totalSpent,
        avgRepairDays: normalized.stats.avgRepairDays
      }

      syncFormData()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      isLoading.value = false
    }
  }

  async function saveProfile() {
    isLoading.value = true
    resetMessages()

    try {
      const payload = {
        email: formData.value.email,
        full_name: formData.value.fullName,
        phone: formData.value.phone,
        address: formData.value.address
      }

      const response = await api.put('/client/profile', payload)
      const normalized = normalizeProfilePayload(response?.data || {})

      user.value = {
        email: normalized.email,
        fullName: normalized.fullName,
        phone: normalized.phone,
        address: normalized.address,
        joinDate: normalized.joinDate
      }

      stats.value = {
        totalRepairs: normalized.stats.totalRepairs,
        totalSpent: normalized.stats.totalSpent,
        avgRepairDays: normalized.stats.avgRepairDays
      }

      syncFormData()
      editMode.value = false
      success.value = 'Perfil actualizado exitosamente.'
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      isLoading.value = false
    }
  }

  function cancelEdit() {
    editMode.value = false
    syncFormData()
    resetMessages()
  }

  function toggleEditMode() {
    if (editMode.value) {
      cancelEdit()
      return
    }
    editMode.value = true
    resetMessages()
  }

  function savePreferences() {
    resetMessages()
    success.value = 'Preferencias guardadas localmente.'
  }

  async function changePassword() {
    resetMessages()

    if (!passwordForm.value.current || !passwordForm.value.next || !passwordForm.value.confirm) {
      error.value = 'Completa todos los campos de contraseña.'
      return
    }

    if (passwordForm.value.next !== passwordForm.value.confirm) {
      error.value = 'Las contraseñas no coinciden.'
      return
    }

    isLoading.value = true

    try {
      await api.post('/client/profile/change-password', {
        current_password: passwordForm.value.current,
        new_password: passwordForm.value.next
      })
      success.value = 'Contraseña actualizada exitosamente.'
      showChangePassword.value = false
      passwordForm.value = { current: '', next: '', confirm: '' }
      showPassword.value = false
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      isLoading.value = false
    }
  }

  async function deleteAccount() {
    resetMessages()
    isLoading.value = true

    try {
      await api.delete('/client/profile')
      authStore.clearSession()
      showDeleteAccount.value = false
      await router.push({ name: 'login' })
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      isLoading.value = false
    }
  }

  onMounted(loadProfile)

  return {
    editMode,
    isLoading,
    error,
    success,
    user,
    formData,
    preferences,
    showChangePassword,
    showDeleteAccount,
    showPassword,
    passwordForm,
    userInitials,
    memberSince,
    totalRepairs,
    totalSpent,
    avgRepairDays,
    toggleEditMode,
    saveProfile,
    savePreferences,
    changePassword,
    deleteAccount
  }
}
