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
  --badge-pad-block: 0.35rem;
  --badge-pad-inline: 0.75rem;
  --badge-font-size: var(--cds-text-base);
  --badge-radius: var(--cds-radius-pill);
  --badge-bg: var(--cds-light-2);
  --badge-text: var(--cds-text-normal);
  --badge-border-width: 0;
  --badge-border-color: transparent;
  --badge-outline-border: var(--cds-light-4);
  --badge-outline-text: var(--cds-text-normal);
  --badge-dot-size: 0.5rem;
  --badge-dismiss-size: 1rem;
  --badge-dismiss-opacity: 0.6;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: var(--badge-pad-block) var(--badge-pad-inline);
  border: var(--badge-border-width) solid var(--badge-border-color);
  border-radius: var(--badge-radius);
  background: var(--badge-bg);
  color: var(--badge-text);
  font-size: var(--badge-font-size);
  font-weight: var(--cds-font-medium);
  white-space: nowrap;
  transition: all 0.2s ease;
}

/* Tamaños */
.size-sm {
  --badge-pad-block: 0.2rem;
  --badge-pad-inline: 0.6rem;
  --badge-font-size: var(--cds-text-sm);
  --badge-radius: 0.25rem;
}

.size-md {
  --badge-pad-block: 0.35rem;
  --badge-pad-inline: 0.75rem;
  --badge-font-size: var(--cds-text-base);
  --badge-radius: var(--cds-radius-pill);
}

.size-lg {
  --badge-pad-block: 0.5rem;
  --badge-pad-inline: 1rem;
  --badge-font-size: var(--cds-text-lg);
  --badge-radius: var(--cds-radius-pill);
}

/* Bordes redondeados completos */
.is-rounded.size-sm {
  --badge-radius: var(--cds-radius-pill);
}

/* Variantes */
.variant-default {
  --badge-bg: var(--cds-surface-2);
  --badge-text: var(--cds-text-normal);
  --badge-outline-border: var(--cds-border-input);
  --badge-outline-text: var(--cds-text-normal);
}

.variant-primary {
  --badge-bg: #e3c09d;
  --badge-text: #7c3911;
  --badge-outline-border: #bf7b46;
  --badge-outline-text: var(--cds-primary);
}

.variant-success {
  --badge-bg: var(--cds-valid-bg);
  --badge-text: var(--cds-valid-text);
  --badge-outline-border: var(--cds-valid-border);
  --badge-outline-text: var(--cds-valid-text);
}

.variant-warning {
  --badge-bg: var(--cds-warning-bg);
  --badge-text: var(--cds-warning-text);
  --badge-outline-border: var(--cds-warning-border);
  --badge-outline-text: var(--cds-warning-text);
}

.variant-danger {
  --badge-bg: var(--cds-invalid-bg);
  --badge-text: var(--cds-invalid-text);
  --badge-outline-border: var(--cds-invalid-border);
  --badge-outline-text: var(--cds-invalid-text);
}

.variant-info {
  --badge-bg: #ccd5da;
  --badge-text: #384751;
  --badge-outline-border: #8797a1;
  --badge-outline-text: var(--cds-info);
}

.variant-neutral {
  --badge-bg: var(--cds-dark);
  --badge-text: var(--cds-white);
  --badge-outline-border: var(--cds-dark);
  --badge-outline-text: var(--cds-dark);
}

.status-badge.is-outlined {
  --badge-bg: transparent;
  --badge-border-width: 1px;
  --badge-border-color: var(--badge-outline-border);
  --badge-text: var(--badge-outline-text);
}

/* Dot indicator */
.badge-dot {
  width: var(--badge-dot-size);
  height: var(--badge-dot-size);
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
  width: var(--badge-dismiss-size);
  height: var(--badge-dismiss-size);
  margin-left: 0.25rem;
  padding: 0;
  border: none;
  background: transparent;
  color: currentColor;
  font-size: 1.1em;
  line-height: 1;
  cursor: pointer;
  opacity: var(--badge-dismiss-opacity);
  transition: opacity 0.2s ease;
}

.badge-dismiss:hover {
  opacity: 1;
}
</style>
