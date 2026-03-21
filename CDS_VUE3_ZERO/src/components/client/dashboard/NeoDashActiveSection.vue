<template>
  <section class="neo-dash-section-surface">
    <header class="neo-dash-section-head">
      <p v-if="eyebrow" class="neo-dash-eyebrow">{{ eyebrow }}</p>
      <h2 class="neo-dash-section-title">{{ title }}</h2>
      <p v-if="description" class="neo-dash-section-copy">{{ description }}</p>
      <div v-if="$slots.actions" class="neo-dash-inline-actions">
        <slot name="actions" />
      </div>
    </header>
    <slot />
  </section>
</template>

<script setup>
defineProps({
  eyebrow: {
    type: String,
    default: '',
  },
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: '',
  },
})
</script>

<style src="./neoDashboardShared.css"></style>
