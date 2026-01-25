<template>
  <div class="admin-shell">
    <AdminSidebar />
    <div class="admin-main">
      <AdminTopbar :title="title" :subtitle="subtitle" />
      <div v-if="context" class="admin-context">
        <div class="context-item">
          <span class="label">Cliente</span>
          <span class="value">{{ context.clientName || 'SIN_DATO' }}</span>
        </div>
        <div class="context-item">
          <span class="label">Código</span>
          <span class="value">{{ context.clientCode || 'SIN_DATO' }}</span>
        </div>
        <div class="context-item">
          <span class="label">Instrumento</span>
          <span class="value">{{ context.instrument || 'SIN_DATO' }}</span>
        </div>
        <div v-if="context.otCode" class="context-item">
          <span class="label">OT</span>
          <span class="value">{{ context.otCode }}</span>
        </div>
      </div>
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
  subtitle: { type: String, default: '' },
  context: { type: Object, default: null }
})
</script>

<style scoped lang="scss">
@import "/src/scss/_theming.scss";

.admin-shell {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100vh;
  background: linear-gradient(180deg, lighten($vintage-beige, 4%) 0%, $vintage-beige 70%, lighten($vintage-beige, 2%) 100%);
  font-size: 1.05rem;
  line-height: 1.6;
}

.admin-main {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.admin-context {
  position: sticky;
  top: 0;
  z-index: 9;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  padding: 1rem 2.5rem;
  background: #f6f2ea;
  border-bottom: 1px solid rgba(62, 60, 56, 0.2);
}

.context-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  font-size: 0.95rem;
}

.context-item .label {
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 0.72rem;
  color: $text-muted;
}

.context-item .value {
  font-weight: 700;
  color: $brand-text;
}

.admin-content {
  padding: 2.5rem 2.75rem 3.25rem;
  font-size: 1.05rem;
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
  padding: 1rem 1rem;
  text-align: left;
  font-size: 1rem;
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
