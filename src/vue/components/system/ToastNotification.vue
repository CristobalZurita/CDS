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
