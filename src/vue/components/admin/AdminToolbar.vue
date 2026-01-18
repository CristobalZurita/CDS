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

<style scoped lang="scss">
@import "/src/scss/_theming.scss";

.admin-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  background: $vintage-beige;
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  border: 1px solid rgba(62, 60, 56, 0.2);
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.2);
  margin-bottom: 1.5rem;
}

.title {
  margin: 0;
  color: $brand-text;
}

.subtitle {
  margin: 0.35rem 0 0;
  color: $text-muted;
  font-size: 0.9rem;
}

.btn-logout {
  padding: 0.65rem 1.2rem;
  background: rgba(236, 107, 0, 0.18);
  color: $brand-text;
  border: 2px solid rgba(236, 107, 0, 0.6);
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: rgba(236, 107, 0, 0.3);
  border-color: rgba(236, 107, 0, 0.75);
}
</style>
