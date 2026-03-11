<template>
  <header class="admin-topbar">
    <div class="title-block">
      <h1 class="title">{{ title || 'Panel Administrativo' }}</h1>
      <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
    </div>
    <div class="actions">
      <button class="btn-logout" type="button" @click="handleLogout">
        Cerrar sesión
      </button>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' }
})

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: var(--color-white, #fff);
  border-bottom: 1px solid var(--color-light, #e0e0e0);
}

.title-block {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  color: var(--color-dark, #1a1a2e);
}

.subtitle {
  margin: 0;
  color: var(--color-gray-600, #666);
  font-size: 0.9rem;
}

.actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-logout {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid var(--color-danger, #dc3545);
  color: var(--color-danger, #dc3545);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: var(--color-danger, #dc3545);
  color: var(--color-white, #fff);
}

@media (max-width: 768px) {
  .admin-topbar {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}
</style>
