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
  gap: var(--intake-form-actions-gap, 1rem);
  padding-top: var(--intake-form-actions-padding, 1rem);
  border-top: 2px solid var(--cds-light-2);
  position: sticky;
  bottom: 0;
  background: var(--cds-surface-1);
  backdrop-filter: blur(8px);
  padding: var(--intake-form-actions-padding, 1rem);
  margin: 0 var(--intake-form-actions-offset, -1rem) var(--intake-form-actions-offset, -1rem);
  border-radius: var(--cds-radius-lg) var(--cds-radius-lg) 0 0;
}

@media (max-width: 768px) {
  .form-actions {
    flex-direction: row;
    padding: 0.55rem 0.75rem;
    gap: 0.5rem;
  }

  /* Botón "Limpiar" — compacto, solo ocupa lo necesario */
  .form-actions :deep(.base-button:first-child) {
    flex: 0 0 auto;
    min-height: 40px;
    font-size: var(--cds-text-sm);
    padding-inline: 0.9rem;
  }

  /* Botón "Crear OT" — ocupa el resto */
  .form-actions :deep(.base-button:last-child) {
    flex: 1;
    min-height: 40px;
    font-size: var(--cds-text-sm);
  }
}
</style>
