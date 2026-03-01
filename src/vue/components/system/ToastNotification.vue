<template>
  <div class="toast-container">
    <transition-group name="toast" tag="div">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast"
        :class="`toast-${toast.type}`"
      >
        <div class="toast-content">
          <span class="toast-icon">{{ getIcon(toast.type) }}</span>
          <span class="toast-message">{{ toast.message }}</span>
        </div>
        <button
          @click="removeToast(toast.id)"
          class="toast-close"
        >
          ✕
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const toasts = ref([])
let toastId = 0

const getIcon = (type) => {
  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠️',
    info: 'ℹ️'
  }
  return icons[type] || 'ℹ️'
}

const removeToast = (id) => {
  toasts.value = toasts.value.filter(t => t.id !== id)
}

const addToast = (message, type = 'info', duration = 4000) => {
  const id = ++toastId
  const toast = { id, message, type }
  toasts.value.push(toast)

  if (duration > 0) {
    setTimeout(() => removeToast(id), duration)
  }

  return id
}

// Expose methods for global use
defineExpose({
  addToast,
  success: (msg, duration) => addToast(msg, 'success', duration),
  error: (msg, duration) => addToast(msg, 'error', duration),
  warning: (msg, duration) => addToast(msg, 'warning', duration),
  info: (msg, duration) => addToast(msg, 'info', duration)
})
</script>

<style scoped lang="scss">
@import "@/scss/_core.scss";

.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-radius: 8px;
  background: $color-white;
  box-shadow: 0 4px 12px rgba($color-black, 0.15);
  pointer-events: auto;
  animation: slideIn 0.3s ease-out;
  max-width: 400px;
  min-width: 300px;
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  transform: translateX(400px);
  opacity: 0;
}

.toast-leave-to {
  transform: translateX(400px);
  opacity: 0;
}

/* Toast Types */
.toast-success {
  background: $color-green-200-legacy;
  border-left: 4px solid $color-green-400-legacy;
  color: $color-green-darker-legacy;
}

.toast-error {
  background: $color-red-200-legacy;
  border-left: 4px solid $color-red-400-legacy;
  color: $color-red-900-legacy;
}

.toast-warning {
  background: $color-orange-100-legacy;
  border-left: 4px solid $color-orange-400-legacy;
  color: $color-orange-900-legacy;
}

.toast-info {
  background: $color-blue-150-legacy;
  border-left: 4px solid $color-blue-400-legacy;
  color: $color-blue-800-legacy;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.toast-icon {
  font-size: 1.2rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
}

.toast-message {
  font-size: 0.95rem;
  line-height: 1.4;
}

.toast-close {
  background: none;
  border: none;
  color: currentColor;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0;
  margin-left: 1rem;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.toast-close:hover {
  opacity: 1;
}

@media (max-width: 640px) {
  .toast-container {
    top: 10px;
    right: 10px;
    left: 10px;
  }

  .toast {
    min-width: auto;
    max-width: 100%;
  }
}
</style>
