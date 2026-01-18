<template>
  <header class="admin-topbar">
    <div>
      <h1 class="title">{{ title || 'Panel Administrativo' }}</h1>
      <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
    </div>
    <div class="actions">
      <router-link to="/dashboard" class="btn-link">Ver panel cliente</router-link>
      <button class="btn-logout" type="button" @click="handleLogout">
        Cerrar sesión
      </button>
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' }
})

const authStore = useAuthStore()

const handleLogout = () => {
  authStore.logout()
}
</script>

<style scoped lang="scss">
@import "/src/scss/_theming.scss";

.admin-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  background: lighten($vintage-beige, 5%);
  border-radius: 12px;
  padding: 1.6rem 2rem;
  margin: 1.75rem 2.5rem 0;
  border: 1px solid rgba(62, 60, 56, 0.2);
  box-shadow: 0 8px 18px rgba(62, 60, 56, 0.18);
}

.title {
  margin: 0;
  color: $brand-text;
  font-size: 1.8rem;
}

.subtitle {
  margin: 0.35rem 0 0;
  color: $text-muted;
  font-size: 1rem;
}

.actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-link {
  color: $brand-text;
  text-decoration: none;
  font-weight: 600;
  border-bottom: 1px solid rgba(62, 60, 56, 0.35);
  padding-bottom: 2px;
}

.btn-logout {
  padding: 0.65rem 1.2rem;
  background: rgba(236, 107, 0, 0.15);
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

@include media-breakpoint-down(md) {
  .admin-topbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .actions {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}
</style>
