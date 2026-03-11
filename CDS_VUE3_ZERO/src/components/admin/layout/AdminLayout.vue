<template>
  <div class="admin-shell" data-testid="admin-shell">
    <AdminSidebar />
    <div class="admin-main">
      <AdminTopbar :title="title" :subtitle="subtitle" />
      <div class="admin-content">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import AdminSidebar from './AdminSidebar.vue'
import AdminTopbar from './AdminTopbar.vue'

defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' }
})
</script>

<style scoped>
.admin-shell {
  display: flex;
  min-height: 100vh;
  background-color: var(--color-bg, #f5f5f5);
}

.admin-main {
  flex: 1;
  margin-left: 260px;
  display: flex;
  flex-direction: column;
}

.admin-content {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .admin-main {
    margin-left: 0;
  }
  
  .admin-content {
    padding: 1rem;
  }
}
</style>
