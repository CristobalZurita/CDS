<template>
  <div class="admin-shell" data-testid="admin-shell">
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

<style lang="scss" scoped>
@use '@/scss/core' as *;

.admin-shell {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100vh;
  background: linear-gradient(180deg, lighten($vintage-beige, 4%) 0%, $vintage-beige 70%, lighten($vintage-beige, 2%) 100%);
  font-size: $text-md;
  line-height: $lh-relaxed;
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
  gap: $spacer-md;
  padding: $spacer-md 2.5rem;
  background: $vintage-beige;
  border-bottom: 1px solid rgba($color-dark, 0.2);
}

.context-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  font-size: $text-base;
}

.context-item .label {
  text-transform: uppercase;
  letter-spacing: $ls-wide;
  font-size: $text-2xs;
  color: $text-muted;
}

.context-item .value {
  font-weight: $fw-bold;
  color: $color-dark;
}

.admin-content {
  padding: 2.5rem 2.75rem 3.25rem;
  font-size: $text-md;
}

.admin-content :deep(.admin-section) {
  background: $vintage-beige;
  border-radius: $border-radius-lg;
  border: 1px solid rgba($color-dark, 0.18);
  padding: $spacer-lg;
  box-shadow: 0 12px 26px rgba($color-dark, 0.15);
  margin-bottom: 1.75rem;
}

.admin-content :deep(.admin-section-header) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: $spacer-md;
  margin-bottom: $spacer-md;
}

.admin-content :deep(.admin-section-title) {
  margin: 0;
  font-size: $h4-size;
  color: $color-dark;
  font-family: $font-family-heading;
}

.admin-content :deep(.admin-table) {
  width: 100%;
  border-collapse: collapse;
  background: $color-white;
  border-radius: $border-radius-lg;
  overflow: hidden;
  box-shadow: 0 10px 20px rgba($color-dark, 0.12);
}

.admin-content :deep(.admin-table th),
.admin-content :deep(.admin-table td) {
  padding: $spacer-md $spacer-md;
  text-align: left;
  font-size: $text-base;
  color: $color-dark;
}

.admin-content :deep(.admin-table thead) {
  background: rgba($color-primary, 0.12);
}

.admin-content :deep(.admin-table tbody tr + tr) {
  border-top: 1px solid rgba($color-dark, 0.12);
}

.admin-content :deep(.admin-btn) {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 0.9rem;
  border-radius: $border-radius-md;
  border: 2px solid transparent;
  font-weight: $fw-semibold;
  cursor: pointer;
  transition: $transition-fast;
}

.admin-content :deep(.admin-btn-primary) {
  background: rgba($color-primary, 0.18);
  border-color: rgba($color-primary, 0.6);
  color: $color-dark;
}

.admin-content :deep(.admin-btn-primary:hover) {
  background: rgba($color-primary, 0.32);
  border-color: rgba($color-primary, 0.8);
}

.admin-content :deep(.admin-btn-outline) {
  background: transparent;
  border-color: rgba($color-dark, 0.3);
  color: $color-dark;
}

.admin-content :deep(.admin-btn-outline:hover) {
  background: rgba($color-dark, 0.08);
}

@include media-breakpoint-down(lg) {
  .admin-shell {
    grid-template-columns: 1fr;
  }
}
</style>
