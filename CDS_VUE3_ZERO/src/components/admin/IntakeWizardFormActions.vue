<template>
  <div class="form-actions">
    <BaseButton
      type="button"
      variant="ghost"
      :disabled="isSubmitting"
      @click="$emit('reset')"
    >
      Limpiar todo
    </BaseButton>

    <BaseButton
      type="submit"
      variant="primary"
      size="lg"
      :loading="isSubmitting"
      :disabled="!canSubmit"
    >
      {{ isSubmitting ? 'Creando OT...' : 'Crear Orden de Trabajo' }}
    </BaseButton>
  </div>
</template>

<script setup>
import { BaseButton } from '@/components/base'

defineProps({
  isSubmitting: {
    type: Boolean,
    default: false
  },
  canSubmit: {
    type: Boolean,
    default: false
  }
})

defineEmits(['reset'])
</script>

<style scoped>
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 2px solid var(--cds-light-2);
  position: sticky;
  bottom: 0;
  background: var(--cds-surface-1);
  backdrop-filter: blur(8px);
  padding: 1rem;
  margin: 0 -1rem -1rem;
  border-radius: var(--cds-radius-lg) var(--cds-radius-lg) 0 0;
}

@media (max-width: 768px) {
  .form-actions {
    flex-direction: column;
  }

  .form-actions :deep(.base-button) {
    width: 100%;
  }
}
</style>
