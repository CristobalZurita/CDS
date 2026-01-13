<template>
  <div class="inline-link-list">
    <a v-for="(link, idx) in links"
       :key="idx"
       :href="link.href"
       :class="['inline-link', { button: isButton }]"
       :target="link.target || '_self'">
      <i v-if="link.faIcon" :class="link.faIcon"></i>
      <span>{{ link.label }}</span>
    </a>
  </div>
</template>

<script setup>
defineProps({
  links: { type: Array, required: true },
  isButton: { type: Boolean, default: false }
})
</script>

<style scoped>
.inline-link-list {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.inline-link {
  text-decoration: none;
  color: #007bff;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0;
  transition: color 0.3s;
}

.inline-link:hover {
  color: #0056b3;
  text-decoration: underline;
}

.inline-link.button {
  background: #007bff;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  text-decoration: none;
}

.inline-link.button:hover {
  background: #0056b3;
  text-decoration: none;
}
</style>
