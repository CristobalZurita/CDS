<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="confirm-dialog-overlay"
      @click.self="emit('cancel')"
    >
      <div
        class="confirm-dialog"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="titleId"
        :aria-describedby="descriptionId"
      >
        <header class="confirm-dialog__header">
          <h2 :id="titleId" class="confirm-dialog__title">{{ title }}</h2>
          <button
            type="button"
            class="confirm-dialog__close"
            aria-label="Cerrar"
            @click="emit('cancel')"
          >
            ×
          </button>
        </header>

        <div class="confirm-dialog__body">
          <p :id="descriptionId" class="confirm-dialog__message">{{ message }}</p>
          <slot />
        </div>

        <footer class="confirm-dialog__actions">
          <BaseButton
            type="button"
            variant="ghost"
            @click="emit('cancel')"
          >
            {{ cancelLabel }}
          </BaseButton>
          <BaseButton
            ref="confirmButtonRef"
            type="button"
            :variant="confirmVariant"
            :loading="confirmLoading"
            :disabled="confirmDisabled"
            @click="emit('confirm')"
          >
            {{ confirmLabel }}
          </BaseButton>
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import BaseButton from './BaseButton.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: 'Confirmar acción' },
  message: { type: String, default: '' },
  confirmLabel: { type: String, default: 'Confirmar' },
  cancelLabel: { type: String, default: 'Cancelar' },
  confirmVariant: {
    type: String,
    default: 'danger',
    validator: (value) => ['primary', 'secondary', 'ghost', 'danger', 'success', 'warning'].includes(value)
  },
  confirmLoading: { type: Boolean, default: false },
  confirmDisabled: { type: Boolean, default: false }
})

const emit = defineEmits(['confirm', 'cancel'])
const confirmButtonRef = ref(null)
const titleId = `confirm-title-${Math.random().toString(36).slice(2, 11)}`
const descriptionId = `confirm-description-${Math.random().toString(36).slice(2, 11)}`

function onKeydown(event) {
  if (event.key === 'Escape' && props.open) {
    emit('cancel')
  }
}

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      window.addEventListener('keydown', onKeydown)
      await nextTick()
      confirmButtonRef.value?.focus?.()
      return
    }
    window.removeEventListener('keydown', onKeydown)
  }
)

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.confirm-dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.5);
}

.confirm-dialog {
  width: min(100%, 30rem);
  display: grid;
  gap: 0;
  border-radius: var(--cds-radius-lg);
  background: var(--cds-white);
  box-shadow: var(--cds-shadow-lg);
  overflow: hidden;
}

.confirm-dialog__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--cds-border-card);
}

.confirm-dialog__title {
  margin: 0;
  font-size: var(--cds-text-xl);
  color: var(--cds-text-normal);
}

.confirm-dialog__close {
  border: none;
  background: none;
  color: var(--cds-text-muted);
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
}

.confirm-dialog__body {
  display: grid;
  gap: 0.6rem;
  padding: 1.25rem;
}

.confirm-dialog__message {
  margin: 0;
  font-size: var(--cds-text-base);
  color: var(--cds-text-normal);
  line-height: 1.5;
}

.confirm-dialog__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem 1.25rem;
  flex-wrap: wrap;
}

@media (max-width: 640px) {
  .confirm-dialog__actions {
    flex-direction: column-reverse;
  }

  .confirm-dialog__actions :deep(.base-button) {
    width: 100%;
  }
}
</style>
