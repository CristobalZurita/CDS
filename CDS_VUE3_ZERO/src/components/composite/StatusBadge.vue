<template>
  <span
    class="status-badge"
    :class="badgeClasses"
    :title="tooltip || label"
  >
    <!-- Dot indicator -->
    <span v-if="showDot" class="badge-dot"></span>
    
    <!-- Icon -->
    <span v-if="icon" class="badge-icon">{{ icon }}</span>
    
    <!-- Label -->
    <span class="badge-label">{{ label }}</span>
    
    <!-- Dismiss button -->
    <button
      v-if="dismissible"
      type="button"
      class="badge-dismiss"
      @click.stop="$emit('dismiss')"
      aria-label="Cerrar"
    >
      ×
    </button>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // Contenido
  label: { type: String, required: true },
  icon: { type: String, default: '' },
  tooltip: { type: String, default: '' },
  
  // Variante (estado)
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'primary', 'success', 'warning', 'danger', 'info', 'neutral'].includes(v)
  },
  
  // Tamaño
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  },
  
  // Apariencia
  showDot: { type: Boolean, default: false },
  dismissible: { type: Boolean, default: false },
  outlined: { type: Boolean, default: false },
  rounded: { type: Boolean, default: false }
})

const emit = defineEmits(['dismiss'])

const badgeClasses = computed(() => ({
  [`variant-${props.variant}`]: true,
  [`size-${props.size}`]: true,
  'has-dot': props.showDot,
  'has-icon': !!props.icon,
  'is-dismissible': props.dismissible,
  'is-outlined': props.outlined,
  'is-rounded': props.rounded
}))
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-weight: 500;
  white-space: nowrap;
  transition: all 0.2s ease;
}

/* Tamaños */
.size-sm {
  padding: 0.2rem 0.6rem;
  font-size: var(--cds-text-sm);
  border-radius: 0.25rem;
}

.size-md {
  padding: 0.35rem 0.75rem;
  font-size: var(--cds-text-base);
  border-radius: 9999px;
}

.size-lg {
  padding: 0.5rem 1rem;
  font-size: var(--cds-text-lg);
  border-radius: 9999px;
}

/* Bordes redondeados completos */
.is-rounded.size-sm {
  border-radius: 9999px;
}

/* Variantes */
.variant-default {
  background: var(--cds-light-2);
  color: var(--cds-text-normal);
}

.variant-default.is-outlined {
  background: transparent;
  border: 1px solid var(--cds-light-4);
}

.variant-primary {
  background: color-mix(in srgb, var(--cds-primary) 15%, white);
  color: color-mix(in srgb, var(--cds-primary) 70%, black);
}

.variant-primary.is-outlined {
  background: transparent;
  border: 1px solid var(--cds-primary);
  color: var(--cds-primary);
}

.variant-success {
  background: color-mix(in srgb, var(--cds-success) 15%, white);
  color: color-mix(in srgb, var(--cds-success) 70%, black);
}

.variant-success.is-outlined {
  background: transparent;
  border: 1px solid var(--cds-success);
  color: var(--cds-success);
}

.variant-warning {
  background: color-mix(in srgb, var(--cds-warning) 20%, white);
  color: color-mix(in srgb, var(--cds-warning) 60%, black);
}

.variant-warning.is-outlined {
  background: transparent;
  border: 1px solid var(--cds-warning);
  color: color-mix(in srgb, var(--cds-warning) 80%, black);
}

.variant-danger {
  background: color-mix(in srgb, var(--cds-danger) 15%, white);
  color: var(--cds-danger);
}

.variant-danger.is-outlined {
  background: transparent;
  border: 1px solid var(--cds-danger);
  color: var(--cds-danger);
}

.variant-info {
  background: color-mix(in srgb, var(--cds-info) 15%, white);
  color: color-mix(in srgb, var(--cds-info) 70%, black);
}

.variant-info.is-outlined {
  background: transparent;
  border: 1px solid var(--cds-info);
  color: var(--cds-info);
}

.variant-neutral {
  background: var(--cds-dark);
  color: var(--cds-white);
}

.variant-neutral.is-outlined {
  background: transparent;
  border: 1px solid var(--cds-dark);
  color: var(--cds-dark);
}

/* Dot indicator */
.badge-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.8;
}

/* Icono */
.badge-icon {
  display: inline-flex;
  align-items: center;
  opacity: 0.9;
}

/* Dismiss button */
.badge-dismiss {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1rem;
  height: 1rem;
  margin-left: 0.25rem;
  padding: 0;
  border: none;
  background: transparent;
  color: currentColor;
  font-size: 1.1em;
  line-height: 1;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.badge-dismiss:hover {
  opacity: 1;
}
</style>
