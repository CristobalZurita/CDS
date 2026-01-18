<template>
  <div class="admin-shell">
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
import AdminSidebar from '@/vue/components/admin/layout/AdminSidebar.vue'
import AdminTopbar from '@/vue/components/admin/layout/AdminTopbar.vue'

defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' }
})
</script>

<style scoped lang="scss">
@import "/src/scss/_theming.scss";

.admin-shell {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100vh;
  background: linear-gradient(180deg, lighten($vintage-beige, 4%) 0%, $vintage-beige 70%, lighten($vintage-beige, 2%) 100%);
}

.admin-main {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.admin-content {
  padding: 2.25rem 2.5rem 3rem;
  font-size: 1rem;
}

.admin-content :deep(.admin-section) {
  background: $vintage-beige;
  border-radius: 14px;
  border: 1px solid rgba(62, 60, 56, 0.18);
  padding: 1.5rem;
  box-shadow: 0 12px 26px rgba(62, 60, 56, 0.15);
  margin-bottom: 1.75rem;
}

.admin-content :deep(.admin-section-header) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.admin-content :deep(.admin-section-title) {
  margin: 0;
  font-size: 1.4rem;
  color: $brand-text;
  font-family: $headings-font-family;
}

.admin-content :deep(.admin-table) {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 20px rgba(62, 60, 56, 0.12);
}

.admin-content :deep(.admin-table th),
.admin-content :deep(.admin-table td) {
  padding: 0.85rem 0.9rem;
  text-align: left;
  font-size: 0.95rem;
  color: $brand-text;
}

.admin-content :deep(.admin-table thead) {
  background: rgba(236, 107, 0, 0.12);
}

.admin-content :deep(.admin-table tbody tr + tr) {
  border-top: 1px solid rgba(62, 60, 56, 0.12);
}

.admin-content :deep(.admin-btn) {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 0.9rem;
  border-radius: 8px;
  border: 2px solid transparent;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.admin-content :deep(.admin-btn-primary) {
  background: rgba(236, 107, 0, 0.18);
  border-color: rgba(236, 107, 0, 0.6);
  color: $brand-text;
}

.admin-content :deep(.admin-btn-primary:hover) {
  background: rgba(236, 107, 0, 0.32);
  border-color: rgba(236, 107, 0, 0.8);
}

.admin-content :deep(.admin-btn-outline) {
  background: transparent;
  border-color: rgba(62, 60, 56, 0.3);
  color: $brand-text;
}

.admin-content :deep(.admin-btn-outline:hover) {
  background: rgba(62, 60, 56, 0.08);
}

@include media-breakpoint-down(lg) {
  .admin-shell {
    grid-template-columns: 1fr;
  }
}
</style>
