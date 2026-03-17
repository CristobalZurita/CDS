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

<style scoped src="./commonLegalPage.css"></style>
