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
