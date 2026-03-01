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
@use "@/scss/_theming.scss" as *;

.admin-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: $spacer-lg;
  background: $vintage-beige;
  border-radius: $border-radius-lg;
  padding: 1.25rem $spacer-lg;
  border: 1px solid rgba($color-dark, 0.2);
  box-shadow: 0 10px 22px rgba($color-black, 0.2);
  margin-bottom: $spacer-lg;
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
  background: rgba($color-primary, 0.18);
  color: $brand-text;
  border: 2px solid rgba($color-primary, 0.6);
  border-radius: $border-radius-md;
  font-weight: $fw-semibold;
  cursor: pointer;
  transition: $transition-fast;
}

.btn-logout:hover {
  background: rgba($color-primary, 0.3);
  border-color: rgba($color-primary, 0.75);
}
</style>
