<template>
  <component
    :is="tag"
    class="base-card"
    :class="cardClasses"
  >
    <!-- Header -->
    <header v-if="title || $slots.header || $slots.actions" class="card-header">
      <div class="card-header-content">
        <slot name="header">
          <h3 v-if="title" class="card-title">{{ title }}</h3>
          <p v-if="subtitle" class="card-subtitle">{{ subtitle }}</p>
        </slot>
      </div>
      <div v-if="$slots.actions" class="card-actions">
        <slot name="actions"></slot>
      </div>
    </header>

    <!-- Media (imagen o contenido superior) -->
    <div v-if="$slots.media" class="card-media">
      <slot name="media"></slot>
    </div>

    <!-- Contenido principal -->
    <div class="card-body" :class="bodyClasses">
      <slot></slot>
    </div>

    <!-- Footer -->
    <footer v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </footer>
  </component>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tag: { type: String, default: 'article' },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'outlined', 'filled', 'elevated'].includes(value)
  },
  padding: {
    type: String,
    default: 'md',
    validator: (value) => ['none', 'sm', 'md', 'lg'].includes(value)
  },
  hover: { type: Boolean, default: false },
  clickable: { type: Boolean, default: false }
})

const cardClasses = computed(() => ({
  [`variant-${props.variant}`]: true,
  [`padding-${props.padding}`]: true,
  'is-hoverable': props.hover,
  'is-clickable': props.clickable
}))

const bodyClasses = computed(() => ({
  'has-padding': props.padding !== 'none'
}))
</script>

<style scoped>
.base-card {
  display: flex;
  flex-direction: column;
  background: var(--cds-white);
  border-radius: var(--cds-radius-md);
  overflow: hidden;
  transition: all 0.2s ease;
}

/* Variantes */
.variant-default {
  border: 1px solid var(--cds-border-card);
}

.variant-outlined {
  border: 2px solid var(--cds-border-strong);
  background: transparent;
}

.variant-filled {
  background: var(--cds-surface-1);
  border: none;
}

.variant-elevated {
  border: none;
  box-shadow: var(--cds-shadow-md);
}

/* Estados hover y clickable */
.is-hoverable:hover {
  box-shadow: var(--cds-shadow-md);
  transform: translateY(-2px);
}

.is-clickable {
  cursor: pointer;
}

.is-clickable:hover {
  box-shadow: var(--cds-shadow-lg);
  transform: translateY(-2px);
}

/* Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid var(--cds-border-card);
}

.card-header-content {
  flex: 1;
  min-width: 0;
}

.card-title {
  margin: 0;
  font-size: var(--cds-text-lg);
  font-weight: 600;
  color: var(--cds-text-normal);
  line-height: 1.3;
}

.card-subtitle {
  margin: 0.25rem 0 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

/* Media */
.card-media {
  width: 100%;
  overflow: hidden;
}

.card-media :deep(img) {
  width: 100%;
  height: auto;
  display: block;
}

/* Body */
.card-body {
  flex: 1 1 auto;
}

.card-body.has-padding {
  padding: 1rem;
}

/* Padding variants */
.padding-none .card-body {
  padding: 0;
}

.padding-sm .card-body.has-padding,
.padding-sm .card-header {
  padding: 0.75rem;
}

.padding-lg .card-body.has-padding,
.padding-lg .card-header {
  padding: 1.5rem;
}

/* Footer */
.card-footer {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--cds-border-card);
  background: color-mix(in srgb, var(--cds-light) 5%, white);
}

.padding-sm .card-footer {
  padding: 0.5rem 0.75rem;
}

.padding-lg .card-footer {
  padding: 1rem 1.5rem;
}
</style>
