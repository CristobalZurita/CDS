<template>
  <div class="admin-toolbar">
    <div class="admin-title">
      <h1 class="title">{{ title }}</h1>
      <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
    </div>
    <button class="btn-logout" type="button" @click="handleLogout">
      Cerrar sesión
    </button>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  title: { type: String, default: 'Admin' },
  subtitle: { type: String, default: '' }
})

const authStore = useAuthStore()

const handleLogout = () => {
  authStore.logout()
}
</script>
