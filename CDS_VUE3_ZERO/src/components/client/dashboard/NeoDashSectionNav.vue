<template>
  <section class="neo-dash-nav-surface" aria-label="Secciones del dashboard">
    <div class="neo-dash-section-nav">
      <button
        v-for="section in sections"
        :key="section.key"
        type="button"
        class="neo-dash-section-button"
        :class="{ 'neo-dash-section-button--active': section.key === activeSection }"
        :style="{ '--neo-section-accent': section.accent || '#4d4a47' }"
        @click="$emit('select', section.key)"
      >
        <span class="neo-dash-section-icon">
          <i :class="section.icon"></i>
        </span>
        <span class="neo-dash-section-button-copy">{{ section.label }}</span>
      </button>
    </div>
  </section>
</template>

<script setup>
defineProps({
  sections: {
    type: Array,
    default: () => [],
  },
  activeSection: {
    type: String,
    default: 'overview',
  },
})

defineEmits(['select'])
</script>

<style src="./neoDashboardShared.css"></style>
