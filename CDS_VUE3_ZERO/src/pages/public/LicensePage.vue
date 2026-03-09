<template>
  <main class="legal-page">
    <section class="legal-card">
      <header class="legal-header">
        <h1>{{ title }}</h1>
        <p>{{ subtitle }}</p>
      </header>

      <article
        v-for="section in sections"
        :id="section.id"
        :key="section.id"
        class="legal-section"
      >
        <h2 v-if="section.title">{{ section.title }}</h2>
        <p v-for="(item, idx) in section.items" :key="idx">{{ item }}</p>
      </article>
    </section>
  </main>
</template>

<script setup>
import { useLicensePage } from '@/composables/useLicensePage'

const { title, subtitle, sections } = useLicensePage()
</script>

<style scoped>
.legal-page {
  padding: 1rem;
}

.legal-card {
  max-width: 980px;
  margin: 0 auto;
  background: var(--cds-white);
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
  border-radius: 1rem;
  padding: 1rem;
}

.legal-header h1 {
  margin: 0;
  font-size: var(--cds-text-3xl);
  line-height: var(--cds-leading-tight);
}

.legal-header p {
  margin-top: 0.4rem;
  font-size: var(--cds-text-base);
  color: var(--cds-text-muted);
}

.legal-section + .legal-section {
  margin-top: 1rem;
}

.legal-section h2 {
  margin: 0 0 0.6rem;
  font-size: var(--cds-text-xl);
}

.legal-section p {
  margin: 0 0 0.6rem;
  font-size: var(--cds-text-base);
  line-height: var(--cds-leading-normal);
}
</style>
