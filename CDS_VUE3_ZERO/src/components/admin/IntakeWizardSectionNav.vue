<template>
  <nav class="wizard-nav">
    <a
      v-for="section in sections"
      :key="section.id"
      :href="`#${section.id}`"
      :class="{ 'is-active': activeSection === section.id }"
      @click.prevent="$emit('navigate', section.id)"
    >
      {{ section.label }}
    </a>
  </nav>
</template>

<script setup>
defineProps({
  sections: {
    type: Array,
    default: () => []
  },
  activeSection: {
    type: String,
    default: ''
  }
})

defineEmits(['navigate'])
</script>

<style scoped>
.wizard-nav {
  position: fixed;
  right: var(--intake-nav-offset-inline, 2rem);
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: var(--intake-nav-padding, 0.5rem);
  background: var(--cds-white);
  border-radius: var(--cds-radius-lg);
  box-shadow: var(--cds-shadow-md);
  z-index: 90;
}

.wizard-nav a {
  padding: var(--intake-nav-link-pad-block, 0.5rem) var(--intake-nav-link-pad-inline, 0.75rem);
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  text-decoration: none;
  border-radius: var(--cds-radius-sm);
  transition: all 0.2s ease;
  white-space: nowrap;
}

.wizard-nav a:hover {
  background: var(--cds-light-1);
  color: var(--cds-text-normal);
}

.wizard-nav a.is-active {
  background: var(--cds-primary);
  color: var(--cds-white);
}

@media (max-width: 768px) {
  .wizard-nav {
    display: none;
  }
}
</style>
